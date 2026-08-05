import requests
import json
from typing import Optional, List, Dict


class APIClient:
    """API客户端封装"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.username: Optional[str] = None

    def set_token(self, token: str, username: str):
        """设置认证token"""
        self.token = token
        self.username = username

    def clear_token(self):
        """清除认证token"""
        self.token = None
        self.username = None

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def register(self, username: str, password: str, key: str = "") -> Dict:
        """用户注册"""
        try:
            data = {"username": username, "password": password}
            if key:
                data["key"] = key
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json=data
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"detail": f"网络错误: {str(e)}"}

    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json={"username": username, "password": password}
            )
            data = response.json()
            if response.status_code == 200:
                self.set_token(data["access_token"], username)
                return {"success": True, "token": data["access_token"]}
            return data
        except requests.exceptions.RequestException as e:
            return {"detail": f"网络错误: {str(e)}"}

    def get_notes(self) -> List[Dict]:
        """获取所有便签"""
        try:
            response = requests.get(
                f"{self.base_url}/api/notes",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []

    def create_note(self, title: str = "", content: str = "", color: str = "#FFE4B5") -> Dict:
        """创建便签"""
        try:
            response = requests.post(
                f"{self.base_url}/api/notes",
                headers=self.get_headers(),
                json={"title": title, "content": content, "color": color}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"detail": f"网络错误: {str(e)}"}

    def update_note(self, note_id: int, title: str = None, content: str = None, color: str = None) -> Dict:
        """更新便签"""
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if color is not None:
            data["color"] = color

        try:
            response = requests.put(
                f"{self.base_url}/api/notes/{note_id}",
                headers=self.get_headers(),
                json=data
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"detail": f"网络错误: {str(e)}"}

    def delete_note(self, note_id: int) -> Dict:
        """删除便签"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/notes/{note_id}",
                headers=self.get_headers()
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"detail": f"网络错误: {str(e)}"}

    def check_health(self) -> bool:
        """检查服务器是否正常"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
