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

import os
# ... 保持您原本的 import 和工具定義 (search_engine_oil) ...

if __name__ == "__main__":
    # 關鍵：從環境變數抓 PORT，沒抓到才用 8000 (Zeabur 會給 8080)
    port_env = int(os.getenv("PORT", 8000))
    
    # 強制 transport="sse" 並綁定 0.0.0.0
    mcp.run(transport="sse", host="0.0.0.0", port=port_env)
