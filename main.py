from server import mcp

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8003,
        path="/mcp",
        log_level="info",
    )