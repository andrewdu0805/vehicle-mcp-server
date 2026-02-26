import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Oil_Database_Search")

@mcp.tool()
async def search_engine_oil(brand: str = None, model: str = None, year: int = None):
    # 這裡放你原本的 SQL 代碼
    return "連線成功"

if __name__ == "__main__":
    # 這是 FastMCP 官方最標準的啟動方式
    mcp.run(transport="sse")
