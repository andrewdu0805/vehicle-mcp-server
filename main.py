import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 1. 初始化
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋引擎機油工具"""
    if not DATABASE_URL: return "錯誤：DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # (這裡保持你原本的 SQL 邏輯...)
        return "資料庫連線測試成功"
    finally:
        await conn.close()

# 2. 獲取底層 SSE App
mcp_app = mcp.sse_app()

# 3. 建立一個簡易的代理，確保根目錄 (/) 不會報 404，方便 Zeabur 監控
async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] == "/":
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"status": "ok", "info": "MCP Server is running"}',
        })
    else:
        # 其餘所有請求 (如 /sse, /messages) 全部丟給 MCP 處理
        await mcp_app(scope, receive, send)
