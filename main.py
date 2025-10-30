from fastmcp import FastMCP

mcp = FastMCP("My MCP Application")

@mcp.tool
def greeting(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
   mcp.run()
