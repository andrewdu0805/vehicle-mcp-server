import os
import asyncpg
import uvicorn
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP
mcp = FastMCP("Oil_Database_Search")

# 資料庫連線資訊
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """
    搜尋適合特定車款的機油。
    :param brand: 車輛品牌 (例如: AUDI)
    :param model: 車輛型號 (例如: A1)
    :param year: 生產年份 (例如: 2015)
    """
    # 確保有資料庫連線字串
    if not DATABASE_URL:
        return "錯誤：尚未設定 DATABASE_URL 環境變數。"

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        query = "SELECT brand, model, chassis_code, viscosity, matched_product, shop_url FROM engine_oils WHERE enable_display = TRUE"
        args = []
        counter = 1

        if brand:
            query += f" AND brand ILIKE ${counter}"
            args.append(f"%{brand}%")
            counter += 1
        if model:
            query += f" AND model ILIKE ${counter}"
            args.append(f"%{model}%")
            counter += 1
        if year:
            query += f" AND start_year <= ${counter} AND (end_year >= ${counter} OR end_year = 9999)"
            args.append(year)
            counter += 1

        rows = await conn.fetch(query, *args)
        if not rows:
            return "找不到符合條件的機油資訊。"
        
        results = []
        for r in rows:
            results.append(f"【{r['brand']} {r['model']} ({r['chassis_code']})】\n建議黏度：{r['viscosity']}\n推薦產品：{r['matched_product']}\n購買連結：{r['shop_url']}")
        
        return "\n---\n".join(results)
    finally:
        await conn.close()

# --- 關鍵修正區段 ---
# 1. 導出 ASGI app 物件，讓 uvicorn 認得它
app = mcp.app 

if __name__ == "__main__":
    # 2. 獲取 Zeabur 指定的 PORT，預設為 8080
    port = int(os.getenv("PORT", 8080))
    # 3. 強制使用 uvicorn 啟動並綁定 0.0.0.0 以開放外網連線
    uvicorn.run(app, host="0.0.0.0", port=port, interface="asgi")
