"""本地 OAuth 2.1 MCP 示例：python 14_mcp/servers/oauth_server.py。

浏览器中使用演示账号 alice / demo-password 登录，再选择同意或拒绝授权。
仅用于本地学习，演示账号不是生产环境的身份认证系统。
客户端注册、授权码和令牌保存在内存中，重启服务后失效。
"""

import secrets
import time
from dataclasses import dataclass
from html import escape
from urllib.parse import parse_qs, urlparse

from mcp.server.auth.provider import AuthorizationParams, construct_redirect_uri
from mcp.server.auth.settings import ClientRegistrationOptions
from mcp.shared.auth import OAuthClientInformationFull
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

from fastmcp import FastMCP
from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider
from fastmcp.server.dependencies import get_access_token


@dataclass
class PendingAuthorization:
    client: OAuthClientInformationFull
    params: AuthorizationParams
    expires_at: float
    csrf_token: str


class MockLoginOAuthProvider(InMemoryOAuthProvider):
    """复用 OAuth 协议实现，只替换自动同意步骤为 mock 登录授权。"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pending: dict[str, PendingAuthorization] = {}
        self.code_users: dict[str, str] = {}
        # 公开的演示账号，仅用于本地 mock 登录。
        self.users = {"alice": "demo-password"}

    async def authorize(self, client, params):
        # 此时 SDK 已校验客户端、redirect_uri、scope 和 PKCE 参数。
        self.pending = {
            key: value for key, value in self.pending.items()
            if value.expires_at > time.time()
        }
        request_id = secrets.token_urlsafe(32)
        self.pending[request_id] = PendingAuthorization(
            client, params, time.time() + 300, secrets.token_urlsafe(32)
        )
        return f"{str(self.base_url).rstrip('/')}/login?request_id={request_id}"

    def get_routes(self, mcp_path=None):
        return super().get_routes(mcp_path) + [
            Route("/login", self.login, methods=["GET", "POST"])
        ]

    def login_page(self, request_id, pending, error="", status_code=200):
        client_name = escape(pending.client.client_name or pending.client.client_id)
        scopes = escape(" ".join(pending.params.scopes))
        response = HTMLResponse(
            f"""<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><title>Mock OAuth 登录授权</title>
<body style="font-family: sans-serif; max-width: 460px; margin: 60px auto; padding: 20px">
<h1>Mock OAuth 登录授权</h1>
<p>应用：<strong>{client_name}</strong></p>
<p>申请权限：<code>{scopes}</code></p>
<p>本地演示账号：alice / demo-password</p>
<p role="alert" style="color: #b42318">{escape(error)}</p>
<form method="post" action="/login">
<input type="hidden" name="request_id" value="{escape(request_id)}">
<input type="hidden" name="csrf_token" value="{pending.csrf_token}">
<p><label>用户名 <input name="username" autocomplete="username" required></label></p>
<p><label>密码 <input name="password" type="password" autocomplete="current-password" required></label></p>
<button name="decision" value="approve">登录并同意授权</button>
<button name="decision" value="deny" formnovalidate>拒绝授权</button>
</form></body></html>""",
            status_code=status_code,
            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
                     "X-Frame-Options": "DENY"},
        )
        response.set_cookie(
            "oauth_demo_csrf", pending.csrf_token,
            httponly=True, samesite="lax", max_age=300, path="/login",
        )
        return response

    async def login(self, request: Request):
        form = await request.form() if request.method == "POST" else request.query_params
        request_id = str(form.get("request_id", ""))
        pending = self.pending.get(request_id)
        if pending is None or pending.expires_at <= time.time():
            self.pending.pop(request_id, None)
            return HTMLResponse("授权请求已失效，请重新运行客户端。", status_code=400)
        if request.method == "GET":
            return self.login_page(request_id, pending)

        csrf_token = str(form.get("csrf_token", ""))
        cookie = request.cookies.get("oauth_demo_csrf", "")
        if not (secrets.compare_digest(csrf_token.encode(), pending.csrf_token.encode())
                and secrets.compare_digest(cookie.encode(), pending.csrf_token.encode())):
            return HTMLResponse("授权表单校验失败，请重新打开授权页面。", status_code=403)

        decision = form.get("decision")
        if decision == "deny":
            self.pending.pop(request_id)
            redirect_uri = construct_redirect_uri(
                str(pending.params.redirect_uri), error="access_denied",
                error_description="User denied authorization", state=pending.params.state,
            )
        elif decision == "approve":
            username = str(form.get("username", ""))
            password = str(form.get("password", ""))
            expected = self.users.get(username)
            if expected is None or not secrets.compare_digest(password.encode(), expected.encode()):
                return self.login_page(request_id, pending, "用户名或密码错误。", 401)
            # 登录并明确同意后才生成授权码，继续 SDK 的 PKCE 换令牌流程。
            redirect_uri = await super().authorize(pending.client, pending.params)
            code = parse_qs(urlparse(redirect_uri).query)["code"][0]
            self.code_users[code] = username
            self.pending.pop(request_id)
        else:
            return HTMLResponse("无效的授权决定。", status_code=400)

        response = RedirectResponse(redirect_uri, status_code=302,
                                    headers={"Cache-Control": "no-store"})
        response.delete_cookie("oauth_demo_csrf", path="/login")
        return response

    async def exchange_authorization_code(self, client, authorization_code):
        tokens = await super().exchange_authorization_code(client, authorization_code)
        self.access_tokens[tokens.access_token].subject = self.code_users.pop(authorization_code.code)
        return tokens

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        access_token = self.access_tokens[self._refresh_to_access_map[refresh_token.token]]
        subject = access_token.subject
        tokens = await super().exchange_refresh_token(client, refresh_token, scopes)
        self.access_tokens[tokens.access_token].subject = subject
        return tokens


auth = MockLoginOAuthProvider(
    base_url="http://localhost:8002",
    client_registration_options=ClientRegistrationOptions(
        enabled=True,
        valid_scopes=["demo:read"],
        default_scopes=["demo:read"],
    ),
    required_scopes=["demo:read"],
)

# /mcp 校验 OAuth 签发的 Bearer Token，未认证的请求返回 401。
# provider 同时提供 OAuth 元数据、客户端注册、授权和令牌端点。
mcp = FastMCP("OAuth Demo", auth=auth)


@mcp.tool
async def get_auth_info() -> dict:
    """查看登录用户、OAuth 客户端和授权范围，不返回令牌。"""
    access_token = get_access_token()
    return {
        "username": access_token.subject,
        "client_id": access_token.client_id,
        "scopes": access_token.scopes,
        "message": "OAuth authentication succeeded",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8002)
