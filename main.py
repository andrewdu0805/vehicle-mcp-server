import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response

# 1. 初始化
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋引擎機油工具邏輯 (保持不變)"""
    # ... 原本的 SQL 代碼 ...
    return "工具連線成功"

# 2. 建立 FastAPI
app = FastAPI()

# 獲取 MCP 的內建 ASGI 處理器
mcp_handler = mcp.sse_app()

# --- 核心修正：接受所有方法 (GET/POST) 到所有路徑 ---
@app.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def catch_all_mcp(request: Request, path: str):
    # 這裡會強制處理 n8n 發出的所有請求
    # 解決 405 Method Not Allowed 的問題
    return await mcp_handler(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
