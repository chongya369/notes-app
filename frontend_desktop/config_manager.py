"""
配置管理模块
管理服务端地址、用户凭据等配置信息
"""
import json
import os
from typing import Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "server_url": "http://127.0.0.1:8000",
        "username": "",
        "password": "",
        "auto_login": False,
        "remember_password": False
    }
    
    # 预设便签颜色
    PRESET_COLORS = [
        "#FFE4B5",  # 黄色
        "#E6F3FF",  # 蓝色
        "#E6FFE6",  # 绿色
        "#FFE6F3",  # 粉色
        "#F3E6FF",  # 紫色
        "#FFF0E6",  # 橙色
    ]
    
    def __init__(self, config_file: str = None):
        """初始化配置管理器"""
        if config_file is None:
            # 配置文件存放在用户目录下
            config_dir = Path.home() / ".sticky_notes"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"
        
        self.config_file = Path(config_file)
        self.config = self.load()
    
    def load(self) -> dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保新增字段有默认值
                    return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置项"""
        self.config[key] = value
        self.save()
    
    def update(self, data: dict):
        """批量更新配置"""
        self.config.update(data)
        self.save()
    
    @property
    def server_url(self) -> str:
        """获取服务器地址"""
        return self.config.get("server_url", self.DEFAULT_CONFIG["server_url"])
    
    @server_url.setter
    def server_url(self, value: str):
        """设置服务器地址"""
        self.config["server_url"] = value
        self.save()
    
    @property
    def username(self) -> str:
        """获取用户名"""
        return self.config.get("username", "")
    
    @username.setter
    def username(self, value: str):
        """设置用户名"""
        self.config["username"] = value
        self.save()
    
    @property
    def password(self) -> str:
        """获取密码"""
        return self.config.get("password", "")
    
    @password.setter
    def password(self, value: str):
        """设置密码"""
        self.config["password"] = value
        self.save()
    
    @property
    def auto_login(self) -> bool:
        """是否自动登录"""
        return self.config.get("auto_login", False)
    
    @auto_login.setter
    def auto_login(self, value: bool):
        """设置自动登录"""
        self.config["auto_login"] = value
        self.save()
    
    @property
    def remember_password(self) -> bool:
        """是否记住密码"""
        return self.config.get("remember_password", False)
    
    @remember_password.setter
    def remember_password(self, value: bool):
        """设置记住密码"""
        self.config["remember_password"] = value
        self.save()
    
    def clear_credentials(self):
        """清除用户凭据"""
        self.config["username"] = ""
        self.config["password"] = ""
        self.config["auto_login"] = False
        self.save()
