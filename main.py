import os
import asyncpg
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from starlette.routing import Mount

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具 (保持不變)"""
    if not DATABASE_URL: return "Error: DATABASE_URL not set"
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

# 2. 建立 FastAPI
app = FastAPI()

# 測試路徑
@app.get("/")
async def root():
    return {"status": "running", "mcp_path": "/sse"}

# --- 關鍵修正：使用 Mount ---
# 這會把 /sse 和 /messages 等所有 MCP 需要的路徑一次掛載好
# 並且正確處理所有的 Header 和長連線
app.mount("/mcp", mcp.sse_app())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
