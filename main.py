import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋引擎機油工具"""
    if not DATABASE_URL: return "錯誤：尚未設定 DATABASE_URL"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 這裡維持你原本的 SQL 邏輯
        return "資料庫連線成功！"
    finally:
        await conn.close()

app = FastAPI()
mcp_handler = mcp.sse_app()

@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    return await mcp_handler(request.scope, request.receive, request._send)

@app.post("/messages")
async def handle_messages(request: Request):
    return await mcp_handler(request.scope, request.receive, request._send)

@app.get("/")
async def root():
    return {"status": "ok", "service": "Google Cloud Run MCP"}

if __name__ == "__main__":
    import uvicorn
    # Cloud Run 會透過環境變數指定 PORT，這行是成功的關鍵
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
