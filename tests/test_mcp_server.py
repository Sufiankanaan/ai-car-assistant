import asyncio

from mcp_server import server


def test_server_lists_the_three_calculators():
    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert names == {"fuel_cost", "monthly_payment", "estimate_tco"}


def test_fuel_cost_tool_has_a_description():
    tools = asyncio.run(server.list_tools())
    fuel = next(t for t in tools if t.name == "fuel_cost")
    assert fuel.description