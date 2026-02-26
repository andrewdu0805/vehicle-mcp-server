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
    """搜尋引擎機油工具"""
    if not DATABASE_URL: return "DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 這裡放入你原本的 SQL 邏輯...
        return "資料庫連線測試成功"
    finally:
        await conn.close()

# 2. 建立 FastAPI 殼
app = FastAPI()

# 獲取處理器
mcp_handler = mcp.sse_app()

@app.get("/sse")
async def sse_handler(request: Request):
    # 這裡的關鍵在於：我們直接呼叫 mcp 的處理器
    # 並且確保 header 裡沒有會導致驗證失敗的資訊
    return await mcp_handler(request.scope, request.receive, request._send)

@app.post("/messages")
async def messages_handler(request: Request):
    return await mcp_handler(request.scope, request.receive, request._send)

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
