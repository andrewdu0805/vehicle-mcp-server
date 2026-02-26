import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")

# 2. 定義工具
@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return "錯誤：尚未在 Zeabur 設定 DATABASE_URL 環境變數"
    
    # 在工具被呼叫時才建立連線，避免啟動時崩潰
    try:
        conn = await asyncpg.connect(db_url)
        query = "SELECT brand, model, chassis_code, viscosity, matched_product, shop_url FROM engine_oils WHERE enable_display = TRUE"
        # ... (這裡保留您原本的 SQL 邏輯) ...
        return "搜尋成功 (測試中)"
    except Exception as e:
        return f"資料庫連線失敗: {str(e)}"
    finally:
        if 'conn' in locals():
            await conn.close()

# --- 核心關鍵：暴露 ASGI App 給 Uvicorn ---
app = mcp.app
