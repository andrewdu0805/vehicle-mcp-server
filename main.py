import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP，這會讓 n8n 識別這個工具
mcp = FastMCP("Oil_Database_Search")

# 資料庫連線資訊（稍後從 Zeabur 環境變數抓取）
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """
    搜尋適合特定車款的機油。
    :param brand: 車輛品牌 (例如: AUDI)
    :param model: 車輛型號 (例如: A1)
    :param year: 生產年份 (例如: 2015)
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 建立基礎 SQL 查詢，只找 enable_display 為 true 的資料
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
        
        # 格式化結果給 AI 閱讀
        results = []
        for r in rows:
            results.append(f"【{r['brand']} {r['model']} ({r['chassis_code']})】\n建議黏度：{r['viscosity']}\n推薦產品：{r['matched_product']}\n購買連結：{r['shop_url']}")
        
        return "\n---\n".join(results)
    finally:
        await conn.close()

if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(mcp.app, host="0.0.0.0", port=8080)  
