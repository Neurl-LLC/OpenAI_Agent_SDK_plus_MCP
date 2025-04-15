from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from zoneinfo import ZoneInfo
import uvicorn

# Create an MCP server
mcp = FastMCP("Tutorial")

# Define tools
@mcp.tool()
def get_time_in_timezone(timezone: str) -> str:
    """
    Given a timezone this tool returns the current time in that time zone
    """
    try:
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    except ValueError:
        return "Invalid time zone. Please provide a valid time zone name."

# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

if __name__ == '__main__':
    uvicorn.run('server:app', port=8000)
