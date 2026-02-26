import os
import asyncpg
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response

# 1. 初始化 MCP
mcp = FastMCP("Oil_Database_Search")
DATABASE_URL = os.getenv("DATABASE_URL")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    """搜尋引擎機油工具"""
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
        return "\n---\n".join([f"【{r['brand']} {r['model']}】\n黏度：{r['viscosity']}\n產品：{r['matched_product']}" for r in rows])
    finally:
        await conn.close()

# 2. 建立 FastAPI
app = FastAPI()
mcp_handler = mcp.sse_app()

# --- 核心修正：強迫關閉壓縮與快取 ---
@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    response = await mcp_handler(request.scope, request.receive, request._send)
    if isinstance(response, Response):
        response.headers["Content-Encoding"] = "identity" # 禁用壓縮
        response.headers["Cache-Control"] = "no-cache"     # 禁用快取
        response.headers["X-Accel-Buffering"] = "no"       # 禁用 Nginx 緩衝
    return response

@app.post("/messages")
async def handle_messages(request: Request):
    return await mcp_handler(request.scope, request.receive, request._send)

@app.get("/")
async def root():
    return {"status": "ok"}
