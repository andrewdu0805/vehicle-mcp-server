import os
import asyncpg
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from fastmcp_mount import MountFastMCP  # 導入專門修正路徑的工具

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油邏輯 (保持不變)"""
    # ... 原本的 SQL 代碼 ...
    return "工具運作正常"

# 2. 建立 FastAPI
app = FastAPI()

# 3. 使用 MountFastMCP 包裝 SSE App 並掛載到根目錄
# 這會自動處理 /sse 和 /messages 路徑，並修正網域前綴 Bug
app.mount("/", MountFastMCP(mcp.sse_app()))

if __name__ == "__main__":
    import uvicorn
    # Zeabur 會給 PORT 環境變數，通常是 8080
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
