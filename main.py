import os
import asyncpg
import uvicorn  # 記得 import uvicorn
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    # ... (您原本的 search_engine_oil 邏輯保持不變) ...
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # (這裡省略重複的 SQL 邏輯代碼)
        return "搜尋結果..." 
    finally:
        await conn.close()

# --- 關鍵修正區段 ---
# 必須定義 app，Dockerfile 的 uvicorn 才能找到它
app = mcp.app 

if __name__ == "__main__":
    # 本地測試時仍可直接執行 python main.py
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
