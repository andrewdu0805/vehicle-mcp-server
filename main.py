import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具 (保持你的 SQL 邏輯)"""
    return "連線成功，工具準備就緒"

# 2. 建立 FastAPI app (解決 Attribute "app" not found)
app = FastAPI()

# 獲取處理器
mcp_handler = mcp.sse_app()

# 3. 萬用路由：解決 Request validation failed
@app.api_route("/{path:path}", methods=["GET", "POST"])
async def handle_mcp(request: Request, path: str):
    # 這裡直接轉發，不再經過嚴格的 Host 驗證
    return await mcp_handler(request.scope, request.receive, request._send)
