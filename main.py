import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋適合特定車款的機油。"""
    if not DATABASE_URL:
        return "錯誤：DATABASE_URL 未設定"
    
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
            return "找不到符合條件的資訊。"
        
        results = [f"【{r['brand']} {r['model']} ({r['chassis_code']})】\n建議黏度：{r['viscosity']}\n推薦產品：{r['matched_product']}\n連結：{r['shop_url']}" for r in rows]
        return "\n---\n".join(results)
    finally:
        await conn.close()

# --- 核心修正：這是 Zeabur 唯一能跑通的寫法 ---
# 直接獲取 FastMCP 預先封裝好的 ASGI App 物件
# 不要寫在 if __name__ == "__main__" 裡面
app = mcp.app
