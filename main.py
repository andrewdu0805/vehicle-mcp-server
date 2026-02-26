import os
import asyncpg
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具 (邏輯保持不變)"""
    if not DATABASE_URL:
        return "錯誤：DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # ... 原本的 SQL 查詢邏輯 ...
        return "搜尋成功 (測試中)"
    finally:
        await conn.close()

# 2. 【關鍵】建立一個標準的 Starlette App 並掛載 MCP 的 SSE 端點
# 這會自動建立 /sse 和 /messages 路徑
app = Starlette(
    routes=[
        Mount("/", app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    # 獲取 Zeabur 給的埠號
    port = int(os.getenv("PORT", 8080))
    # 使用 uvicorn 啟動 app
    uvicorn.run(app, host="0.0.0.0", port=port)
