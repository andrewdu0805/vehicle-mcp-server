import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具邏輯 (保持不變)"""
    if not DATABASE_URL: return "Error: DATABASE_URL not set"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        query = "SELECT brand, model, chassis_code, viscosity, matched_product, shop_url FROM engine_oils WHERE enable_display = TRUE"
        # ... (中間 SQL 邏輯保持不變) ...
        return "搜尋成功 (測試中)"
    finally:
        await conn.close()

# 2. 建立 FastAPI 並強行修復路徑
app = FastAPI()

# 1. 測試路徑 (這已經通了)
@app.get("/")
async def root():
    return {"status": "running", "mcp_path": "/sse"}

# 2. 核心修正：將 MCP 的處理器直接綁定在 /sse 和 /messages
# 這樣不論 n8n 怎麼敲，都會進到同一個處理器
@app.get("/sse")
@app.post("/messages")
async def mcp_handler(request: Request):
    # 獲取 FastMCP 的 ASGI App
    sse_handler = mcp.sse_app()
    # 執行處理
    return await sse_handler(request.scope, request.receive, request._send)
