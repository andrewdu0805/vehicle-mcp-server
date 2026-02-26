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

# 測試用：確認網址活著
@app.get("/")
async def root():
    return {"status": "running"}

# 關鍵：手動將 MCP 的 sse 處理器掛載到根目錄
# 這樣 n8n 敲 /sse 或 /messages 時就不會跑錯地方
mcp_asgi = mcp.sse_app()

@app.get("/sse")
@app.post("/messages")
async def handle_mcp(request: Request):
    return await mcp_asgi(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
