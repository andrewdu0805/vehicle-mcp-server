import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 1. 初始化
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 定義工具 (您的邏輯保持不變)
@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具..."""
    if not DATABASE_URL:
        return "錯誤：DATABASE_URL 未設定"
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        query = "SELECT brand, model, chassis_code, viscosity, matched_product, shop_url FROM engine_oils WHERE enable_display = TRUE"
        args = []
        counter = 1
        if brand:
            query += f" AND brand ILIKE ${counter}"; args.append(f"%{brand}%"); counter += 1
        if model:
            query += f" AND model ILIKE ${counter}"; args.append(f"%{model}%"); counter += 1
        if year:
            query += f" AND start_year <= ${counter} AND (end_year >= ${counter} OR end_year = 9999)"; args.append(year); counter += 1

        rows = await conn.fetch(query, *args)
        if not rows: return "找不到符合條件的資訊。"
        
        results = [f"【{r['brand']} {r['model']}】\n建議黏度：{r['viscosity']}\n推薦產品：{r['matched_product']}\n連結：{r['shop_url']}" for r in rows]
        return "\n---\n".join(results)
    finally:
        await conn.close()

# 3. 【核心修正】將 FastMCP 轉換為標準 ASGI App
# 這一行必須在 if __name__ == "__main__" 之外！
app = mcp.app

if __name__ == "__main__":
    # 本地測試用，Zeabur 不會跑這段
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
