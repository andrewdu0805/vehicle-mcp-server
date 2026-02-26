import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from starlette.responses import StreamingResponse

# 1. 初始化 FastMCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 定義工具 (邏輯保持不變)
@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
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

# 3. 【關鍵修正】手動建立 FastAPI 並掛載 MCP 的 SSE 端點
app = FastAPI()

# 讓根目錄直接回應，方便測試網址是否活著
@app.get("/")
async def root():
    return {"status": "ok", "message": "MCP Server is running"}

# 手動掛載 MCP 的 SSE 邏輯到 /sse 路徑
@app.get("/sse")
async def sse_endpoint(request: Request):
    async with mcp._mcp_server as server:
        # 這裡呼叫 FastMCP 內建的 SSE 處理器
        return await mcp.sse_app()(request.scope, request.receive, request._send)

# 手動掛載消息接收到 /messages 路徑
@app.post("/messages")
async def messages_endpoint(request: Request):
    async with mcp._mcp_server as server:
        return await mcp.sse_app()(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
