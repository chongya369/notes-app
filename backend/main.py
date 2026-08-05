import argparse
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config import settings
from models import init_db
from routers import auth, notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("✓ 数据库初始化完成")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/", summary="根路径")
async def root():
    return {
        "message": "欢迎使用便签小程序API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", summary="健康检查")
async def health():
    return {"status": "ok"}


frontend_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend_web",
    "static"
)
frontend_path = os.path.abspath(frontend_path)

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/web", summary="网页前端入口")
    async def web_index():
        index_path = os.path.join(frontend_path, "index.html")
        return FileResponse(index_path)
    print(f"✓ 网页前端目录已挂载: {frontend_path}")


def main():
    parser = argparse.ArgumentParser(description="便签小程序后端服务")
    parser.add_argument("--host", type=str, default=settings.host, help="服务器地址")
    parser.add_argument("--port", type=int, default=settings.port, help="服务器端口")
    args = parser.parse_args()

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    data_dir = os.path.abspath(data_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✓ 创建数据目录: {data_dir}")

    print(f"\n{'='*50}")
    print(f"便签小程序后端服务启动中...")
    print(f"网页前端: http://{args.host}:{args.port}/web")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    print(f"{'='*50}\n")

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=False
    )


if __name__ == "__main__":
    main()
