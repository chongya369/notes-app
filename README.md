# 便签小程序

一个支持多端访问的便签管理应用，提供 Windows 桌面客户端与 Web 网页端两种使用方式，后端基于 FastAPI 构建，数据存储于本地 SQLite 数据库。

## 功能特性

- 用户认证：注册 / 登录，基于 JWT 令牌鉴权，密码使用 PBKDF2-SHA256 加盐哈希
- 便签管理：新建、编辑、删除、查看便签
- 便签颜色：支持自定义便签背景色，内置多种预设颜色
- 拖拽排序：支持便签自定义排序
- 多端访问：
  - 桌面客户端：多便签独立窗口、系统托盘常驻、窗口置顶、自动登录
  - Web 端：浏览器即开即用，响应式界面
- 注册管控：可关闭注册或设置注册密钥限制
- API 文档：内置 Swagger UI 自动生成的接口文档

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | FastAPI、SQLAlchemy（异步）、aiosqlite、python-jose（JWT）、pydantic-settings |
| 桌面客户端 | PyQt6、pystray（系统托盘）、Pillow、requests |
| Web 前端 | 原生 HTML / CSS / JavaScript、Sortable.js（拖拽排序） |
| 数据库 | SQLite |

## 项目结构

```
便签小程序/
├── backend/                    # 后端服务
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置项（pydantic-settings）
│   ├── models.py               # 数据库模型与 Pydantic Schema
│   ├── auth.py                 # 密码哈希与 JWT 鉴权
│   ├── routers/
│   │   ├── auth.py             # 注册 / 登录接口
│   │   └── notes.py            # 便签 CRUD 与排序接口
│   └── requirements.txt
├── frontend_desktop/           # Windows 桌面客户端
│   ├── main.py                 # 应用入口与控制器
│   ├── api_client.py           # 后端 API 调用封装
│   ├── config_manager.py       # 本地配置管理
│   ├── note_window.py          # 单个便签窗口
│   ├── note_list_window.py     # 便签列表窗口
│   ├── settings_window.py      # 登录 / 设置窗口
│   ├── tray_manager.py         # 系统托盘管理
│   └── requirements.txt
├── frontend_web/static/        # Web 前端静态资源
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── data/                       # SQLite 数据库存放目录
├── install.bat                 # 一键安装依赖
├── start_backend.bat           # 启动后端 API
├── start_backend_web.bat       # 启动后端 + Web 前端
└── start_desktop.bat           # 启动桌面客户端
```

## 环境要求

- Python 3.10 及以上
- Windows 操作系统（桌面客户端依赖 PyQt6 与 pystray）
- 网络访问（首次安装依赖时需要）

## 快速开始

### 1. 安装依赖

双击运行 `install.bat`，或在项目根目录执行：

```bash
python -m pip install -r backend/requirements.txt
python -m pip install -r frontend_desktop/requirements.txt
```

### 2. 启动后端服务

- 仅启动后端 API：

  ```bash
  start_backend.bat
  ```
  等价于 `python backend/main.py`

- 启动后端并挂载 Web 前端：

  ```bash
  start_backend_web.bat
  ```
  等价于 `python backend/main.py --web`

启动后：
- API 根路径：`http://127.0.0.1:8000/`
- API 文档（Swagger UI）：`http://127.0.0.1:8000/docs`
- Web 前端（仅 `--web` 模式）：`http://127.0.0.1:8000/web`

### 3. 使用桌面客户端

确保后端服务已启动，然后运行：

```bash
start_desktop.bat
```

客户端启动后常驻系统托盘：
- 双击托盘图标：显示 / 隐藏所有便签
- 托盘右键菜单：新建便签、便签列表、设置、退出
- 首次使用需在「设置」中填写服务器地址并注册 / 登录

### 4. 使用 Web 端

以 `--web` 模式启动后端后，浏览器访问 `http://127.0.0.1:8000/web` 即可使用。

## 配置说明

### 后端配置

后端配置位于 [backend/config.py](backend/config.py)，默认值可通过项目根目录下的 `.env` 文件覆盖：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `host` | `127.0.0.1` | 服务监听地址 |
| `port` | `8000` | 服务监听端口 |
| `database_url` | `sqlite+aiosqlite:///./data/notes.db` | 数据库连接 |
| `secret_key` | `your-secret-key-please-change-in-production` | JWT 签名密钥，生产环境务必修改 |
| `access_token_expire_minutes` | `10080`（7 天） | 令牌有效期 |
| `registration_enabled` | `True` | 是否开放注册 |
| `registration_key` | `""` | 注册密钥，为空则不校验 |

`.env` 示例：

```env
SECRET_KEY=your-secure-random-string
REGISTRATION_ENABLED=true
REGISTRATION_KEY=
```

### 桌面客户端配置

桌面客户端的配置文件位于用户主目录 `~/.sticky_notes/config.json`，记录服务器地址、用户名、是否自动登录与记住密码等信息，可在「设置」窗口中图形化修改。

## API 接口概览

| 方法 | 路径 | 说明 | 鉴权 |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录，返回 JWT | 否 |
| GET | `/api/notes` | 获取当前用户所有便签 | 是 |
| POST | `/api/notes` | 新建便签 | 是 |
| GET | `/api/notes/{id}` | 获取单个便签 | 是 |
| PUT | `/api/notes/{id}` | 更新便签内容 / 颜色 | 是 |
| DELETE | `/api/notes/{id}` | 删除便签 | 是 |
| PUT | `/api/notes/sort` | 批量更新便签排序 | 是 |
| GET | `/health` | 健康检查 | 否 |

完整请求 / 响应结构详见 `http://127.0.0.1:8000/docs`。

## 数据存储

- 数据库文件：`data/notes.db`（首次启动后端时自动创建）
- 表结构：
  - `users`：用户信息（用户名、密码哈希、创建时间）
  - `notes`：便签信息（标题、内容、颜色、排序、创建 / 更新时间）

## 安全说明

- 密码使用 PBKDF2-SHA256 加盐哈希存储，迭代次数 100000
- 接口鉴权基于 JWT Bearer Token
- 默认 `secret_key` 仅适用于本地测试，**生产环境部署前请务必修改**
- 后端默认仅监听 `127.0.0.1`，如需跨机器访问请修改 `host` 并评估安全风险
