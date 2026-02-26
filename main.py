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
    """機油搜尋工具"""
    if not DATABASE_URL: return "DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 這裡放你原本的 SQL 邏輯
        return "資料庫連線正常"
    finally:
        await conn.close()

# 2. 建立 FastAPI (這是綠燈保證)
app = FastAPI()

# 3. 獲取 FastMCP 的內建 SSE App
mcp_sse_app = mcp.sse_app()

# 健康檢查 (確保瀏覽器打開 https://vehicle-mcp.zeabur.app/ 是通的)
@app.get("/")
async def health():
    return {"status": "ok", "service": "mcp-server"}

# 關鍵：解決 405 Method Not Allowed
# n8n 可能會對 /sse 發送 POST，我們強迫它交給 MCP 處理
@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    return await mcp_sse_app(request.scope, request.receive, request._send)

# 關鍵：解決訊息傳遞路徑
@app.api_route("/messages", methods=["GET", "POST"])
async def handle_messages(request: Request):
    return await mcp_sse_app(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    # 強制讀取 Zeabur 的 PORT
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
