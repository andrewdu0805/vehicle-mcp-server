import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 初始化
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油資訊 (邏輯保持不變)"""
    if not DATABASE_URL: return "錯誤：DATABASE_URL 未設定"
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        query = "SELECT brand, model, chassis_code, viscosity, matched_product, shop_url FROM engine_oils WHERE enable_display = TRUE"
        args = []
        counter = 1
        if brand: query += f" AND brand ILIKE ${counter}"; args.append(f"%{brand}%"); counter += 1
        if model: query += f" AND model ILIKE ${counter}"; args.append(f"%{model}%"); counter += 1
        if year: query += f" AND start_year <= ${counter} AND (end_year >= ${counter} OR end_year = 9999)"; args.append(year); counter += 1
        rows = await conn.fetch(query, *args)
        if not rows: return "找不到符合條件的資訊。"
        return "\n---\n".join([f"【{r['brand']} {r['model']}】\n建議黏度：{r['viscosity']}\n推薦產品：{r['matched_product']}\n連結：{r['shop_url']}" for r in rows])
    finally:
        await conn.close()

if __name__ == "__main__":
    # 關鍵：只指定 transport，其餘交給 Zeabur 環境變數控管
    mcp.run(transport="sse")
