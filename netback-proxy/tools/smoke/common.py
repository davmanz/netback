import os
import json
import uuid
from typing import Optional, Dict, Any
import httpx


class ProxySession:
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or os.getenv("SMOKE_BASE_URL") or "http://localhost:8080").rstrip("/")
        self.username = os.getenv("SMOKE_USER", "admin")
        self.password = os.getenv("SMOKE_PASS", "admin")
        self.access_token: Optional[str] = None
        # Permitir configurar timeout por parámetro o variable de entorno SMOKE_TIMEOUT
        if timeout is None:
            try:
                timeout = float(os.getenv("SMOKE_TIMEOUT", "15"))
            except Exception:
                timeout = 15.0
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self):
        self.client.close()

    def _xsrf_header(self) -> Dict[str, str]:
        # httpx almacena cookies en client.cookies
        xsrf = self.client.cookies.get("XSRF-TOKEN")
        return {"X-CSRF-Token": xsrf} if xsrf else {}

    def login(self) -> str:
        resp = self.client.post("/auth/login/", json={"username": self.username, "password": self.password})
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data.get("access")
        if not self.access_token:
            raise RuntimeError("No access token in login response")
        return self.access_token

    def request(self, method: str, path: str, json_body: Optional[Dict[str, Any]] = None) -> httpx.Response:
        headers: Dict[str, str] = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if method.upper() in ("POST", "PUT", "PATCH", "DELETE"):
            headers.update(self._xsrf_header())
        return self.client.request(method, path, json=json_body, headers=headers)

    # Helpers CRUD genéricos
    def post(self, path: str, body: Dict[str, Any]) -> httpx.Response:
        return self.request("POST", path, json_body=body)

    def get(self, path: str) -> httpx.Response:
        return self.request("GET", path)

    def put(self, path: str, body: Dict[str, Any]) -> httpx.Response:
        return self.request("PUT", path, json_body=body)

    def patch(self, path: str, body: Dict[str, Any]) -> httpx.Response:
        return self.request("PATCH", path, json_body=body)

    def delete(self, path: str) -> httpx.Response:
        return self.request("DELETE", path)


def random_nick(prefix: str = "smoke") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
