import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response

# 1. 初始化 MCP (不要改名字)
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具 (邏輯保持不變)"""
    if not DATABASE_URL: return "Error: DATABASE_URL not set"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 這裡放入你原本的 SQL 查詢邏輯...
        return "搜尋成功 (測試中)"
    finally:
        await conn.close()

# 2. 建立 FastAPI 殼
app = FastAPI()

# 測試用：確認伺服器還活著
@app.get("/")
async def health():
    return {"status": "running", "mcp_check": "manual_route"}

# --- 核心關鍵：手動橋接 SSE ---
# 我們不使用 mount，改用直接調用，這樣能強迫路徑對齊
mcp_handler = mcp.sse_app()

@app.get("/sse")
async def sse_interface(request: Request):
    # 強迫 MCP 處理這個 GET 請求
    return await mcp_handler(request.scope, request.receive, request._send)

@app.post("/messages")
async def messages_interface(request: Request):
    # 強迫 MCP 處理這個 POST 請求
    return await mcp_handler(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
