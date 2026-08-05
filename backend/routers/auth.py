from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, UserCreate, UserLogin, Token, get_db
from auth import verify_password, get_password_hash, create_access_token
from config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", summary="用户注册")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    if not settings.registration_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="注册功能已关闭"
        )

    if settings.registration_key:
        if not user_data.key or user_data.key != settings.registration_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="注册密钥无效"
            )

    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_password
    )
    db.add(new_user)
    await db.commit()

    return {"message": "注册成功", "username": new_user.username}


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录，返回JWT token"""
    # 查找用户
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    user = result.scalar_one_or_none()

    # 验证用户和密码
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")
