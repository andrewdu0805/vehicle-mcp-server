import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具 (保持不變)"""
    if not DATABASE_URL: return "Error: DATABASE_URL not set"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # ... 保持你原本的 SQL 邏輯 ...
        return "搜尋成功 (測試中)"
    finally:
        await conn.close()

# 2. 建立 FastAPI 殼
app = FastAPI()

# 獲取 MCP 的 ASGI 處理器
mcp_handler = mcp.sse_app()

# --- 核心關鍵：全通路導流 ---
# 無論 GET 或 POST，無論路徑是什麼，通通交給 MCP
@app.api_route("/{path:path}", methods=["GET", "POST"])
async def catch_all_mcp(request: Request, path: str):
    # 這裡會處理 /sse, /messages 以及任何 n8n 發出的請求
    return await mcp_handler(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
