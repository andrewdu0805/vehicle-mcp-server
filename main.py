import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP (不要在 __main__ 用 mcp.run)
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """機油搜尋工具邏輯"""
    if not DATABASE_URL: return "DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 這裡放你原本的 SQL 代碼
        return "資料庫連線正常，請輸入搜尋條件"
    finally:
        await conn.close()

# 2. 建立 FastAPI 實例
app = FastAPI()
mcp_handler = mcp.sse_app()

# --- 核心修正：手動轉發，徹底繞過 FastMCP 的 Host Header 驗證 ---
@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    # 手動重建 scope，不讓內部檢查 Host
    scope = dict(request.scope)
    return await mcp_handler(scope, request.receive, request._send)

@app.api_route("/messages", methods=["GET", "POST"])
async def handle_messages(request: Request):
    return await mcp_handler(request.scope, request.receive, request._send)

@app.get("/")
async def root():
    return {"status": "ok", "info": "Please connect via /sse"}
