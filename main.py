import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋引擎機油工具邏輯 (保持不變)"""
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

# 2. 建立 FastAPI
app = FastAPI()

# 獲取 FastMCP 的內建處理器
mcp_handler = mcp.sse_app()

# --- 核心修正：明確區分 GET (建立連線) 與 POST (傳送訊息) ---

@app.get("/sse")
async def handle_sse_get(request: Request):
    # n8n 第一次連線會敲這裡，必須回傳 SSE Stream
    return await mcp_handler(request.scope, request.receive, request._send)

@app.post("/sse")
@app.post("/messages")
async def handle_sse_post(request: Request):
    # n8n 傳送指令會敲這裡
    return await mcp_handler(request.scope, request.receive, request._send)

# 健康檢查路徑
@app.get("/")
async def root():
    return {"status": "ok", "mcp_endpoint": "/sse"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
