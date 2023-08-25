import pytest
import sys
sys.path.append('/Users/darius/Code/Trader Joe/joe-sor-v1/')
from src import main, Pool

BARN_URL = "https://barn.traderjoexyz.com"
NODE_URL = "https://rpc.ankr.com/avalanche"
BACKSTOP_NODE_URL = "https://api.avax.network/ext/bc/C/rpc"
CHAIN = "avalanche"
RADIUS = 50
PAIR_ADDRESS_WAVAX_USDC = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
PAIR_ADDRESS_BTC_B_USDC = "0x4224f6F4C9280509724Db2DbAc314621e4465C29"
NB_PART = 5
MAX_UINT256 = (1 << 256) - 1


AVAX_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS_WAVAX_USDC, "v2.1")
BTC_B_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS_BTC_B_USDC, "v2.1")

v2pools = Pool.get_pools(BARN_URL, CHAIN, "all", 100)

routesAU = main.get_all_routes(v2pools, AVAX_USDC.tokenX, AVAX_USDC.tokenY)
routesBU = main.get_all_routes(v2pools, BTC_B_USDC.tokenX, BTC_B_USDC.tokenY)


tokenInAU = AVAX_USDC.tokenX  # AVAX
tokenOutAU = AVAX_USDC.tokenY  # USDC
tokenInBU = BTC_B_USDC.tokenX  # BTC.b
tokenOutBU = BTC_B_USDC.tokenY  # USDC

for i, route in enumerate(routesAU):
    print(f"route {i} : ")
    for pair in route:
        print(pair.name + " " + pair.version)
    # print(get_amount_out_from_route(2 * 10**17, route, tokenInAU, tokenOutAU))
    print(" ")

routes_result = main.get_routes_and_parts(routesAU, 1 * 10**18, tokenInAU, tokenOutAU)

for route_info in routes_result:
    print(f"Route Index: {route_info['route_index']}")
    print(f"Pair Index: {route_info['pair_index']}")
    print(f"Pair: {route_info['pair'].name}")
    print(f"Amount: {route_info['amount']}")
    print("-" * 50)  # print a separator for clarity

# BTC.b to USDC
for i, route in enumerate(routesBU):
    print(f"route {i} : ")
    for pair in route:
        print(pair.name + " " + pair.version)
    print(" ")

routes_result = get_routes_and_parts(routesBU, 1 * 10**6, tokenInBU, tokenOutBU)

for route_info in routes_result:
    print(f"Route Index: {route_info['route_index']}")
    print(f"Pair Index: {route_info['pair_index']}")
    print(f"Pair: {route_info['pair'].name}")
    print(f"Amount: {route_info['amount']}")
    print("-" * 50)  # print a separator for clarity
