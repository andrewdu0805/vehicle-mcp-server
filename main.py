import os
import asyncpg
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP (保持邏輯)
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋機油工具邏輯"""
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
        return "\n---\n".join([f"【{r['brand']} {r['model']}】\n黏度：{r['viscosity']}\n產品：{r['matched_product']}\n連結：{r['shop_url']}" for r in rows])
    finally:
        await conn.close()

# 2. 獲取 FastMCP 的 SSE 處理器
mcp_sse_app = mcp.sse_app()

# 3. 【核心修正】原生 ASGI 代理程式
# 解決 405 錯誤：不論是 GET 或 POST，通通強制餵給 MCP 處理器
async def app(scope, receive, send):
    # 如果是 HTTP 請求，強制把 method 改為處理器預期的類型 (如果是 /sse 就當 GET，其餘當 POST)
    # 這是為了解決 n8n 錯誤發送 POST /sse 的問題
    if scope["type"] == "http":
        if scope["path"].endswith("/sse"):
            scope["method"] = "GET"
        else:
            scope["method"] = "POST"
            
    # 直接交給 MCP 處理器執行，不透過 FastAPI 路由
    await mcp_sse_app(scope, receive, send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
