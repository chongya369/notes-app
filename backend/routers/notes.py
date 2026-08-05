from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import string

from models import Note, NoteCreate, NoteUpdate, NoteResponse, get_db
from auth import get_current_user, User

router = APIRouter(prefix="/api/notes", tags=["便签"])


async def generate_unique_title(db: AsyncSession, user_id: int, username: str) -> str:
    charset = string.ascii_letters + string.digits
    
    while True:
        random_part = ''.join(secrets.choice(charset) for _ in range(8))
        title = f"{username}_{random_part}"
        
        result = await db.execute(
            select(Note).where(
                Note.user_id == user_id,
                Note.title == title
            )
        )
        
        if not result.scalar_one_or_none():
            return title


@router.get("", response_model=List[NoteResponse], summary="获取所有便签")
async def get_notes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有便签"""
    result = await db.execute(
        select(Note)
        .where(Note.user_id == current_user.id)
        .order_by(Note.sort_order.asc())
    )
    notes = result.scalars().all()
    return notes


@router.post("", response_model=NoteResponse, summary="创建便签")
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新便签"""
    if not note_data.title:
        note_data.title = await generate_unique_title(
            db, current_user.id, current_user.username
        )
    
    await db.execute(
        update(Note)
        .where(Note.user_id == current_user.id)
        .values(sort_order=Note.sort_order + 1)
    )
    
    new_note = Note(
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        color=note_data.color,
        sort_order=0
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


@router.get("/{note_id}", response_model=NoteResponse, summary="获取单个便签")
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个便签详情"""
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="便签不存在"
        )

    return note


@router.put("/{note_id}", response_model=NoteResponse, summary="更新便签")
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新便签内容"""
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="便签不存在"
        )

    # 更新字段
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.color is not None:
        note.color = note_data.color

    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", summary="删除便签")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除便签"""
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="便签不存在"
        )

    await db.delete(note)
    
    await db.execute(
        update(Note)
        .where(
            Note.user_id == current_user.id,
            Note.sort_order > note.sort_order
        )
        .values(sort_order=Note.sort_order - 1)
    )
    
    await db.commit()

    return {"message": "删除成功"}


@router.put("/sort", summary="更新便签排序")
async def sort_notes(
    note_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批量更新便签排序"""
    for index, note_id in enumerate(note_ids):
        result = await db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
        note = result.scalar_one_or_none()
        if note:
            note.sort_order = index
    await db.commit()
    return {"message": "排序成功"}
