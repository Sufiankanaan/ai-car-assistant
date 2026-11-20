from mcp.server.mcpserver import MCPServer

from tools import estimate_tco, fuel_cost, monthly_payment

server = MCPServer(
    name="car-tools",
    instructions="Car cost calculators: trip fuel cost, monthly loan payment, and total cost of ownership.",
)

for tool in (fuel_cost, monthly_payment, estimate_tco):
    server.add_tool(tool)


if __name__ == "__main__":
    server.run()