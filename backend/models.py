from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# 数据库基础模型
Base = declarative_base()


# 用户表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# 便签表
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), default="")
    content = Column(Text, default="")
    color = Column(String(20), default="#FFE4B5")
    sort_order = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

# 异步会话工厂
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 初始化数据库
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 获取数据库会话
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Pydantic 模型 - 用于API请求和响应
class UserCreate(BaseModel):
    username: str
    password: str
    key: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class NoteCreate(BaseModel):
    title: Optional[str] = ""
    content: Optional[str] = ""
    color: Optional[str] = "#FFE4B5"


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    color: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
