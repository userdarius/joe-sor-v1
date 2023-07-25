import Bin
import Pool
import Token
import Quote
from typing import Tuple

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
BIN_ID = "8376042"
NB_PART = 5

avax_usdc = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")
print(avax_usdc.name)

pair = {
    "pairAddress": "",
    "tokenX": Token,
    "tokenY": Token,
    "version": 0,
    "bin_step": 0,
    "activeId": 0,
}
route = {"part": 0, "amount": 0, "pairs": []}
routes = {"tokens": [], "routes": []}

# Create some pairs (for demonstration purposes)
pair1 = pair.copy()  # Make a copy so we can modify it without affecting the original
pair1["pairAddress"] = ""
pair1["tokenX"] = "token1"
pair1["tokenY"] = "token2"

pair2 = pair.copy()  # Make a copy so we can modify it without affecting the original
pair2["pairAddress"] = "address2"
pair2["tokenX"] = "token3"
pair2["tokenY"] = "token4"

# Add these pairs to the route
route["pairs"].append(pair1)
route["pairs"].append(pair2)

# Now the route dictionary contains a list of pairs
print(route)

pools = Pool.get_pools(BARN_URL, CHAIN, "v2.0", 100)
for pool in pools:
    print(
        pool.name
        + " - "
        + "binstep : "
        + str(pool.lbBinStep)
        + " - "
        + pool.pairAddress
        + " - "
        + "active bin id : "
        + str(pool.activeBinId)
    )

# list of all tokens on the avalanche dex
tokens = Token.get_tokens(BARN_URL, CHAIN)


bins = Bin.get_bin(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS, BIN_ID)
for bin in bins:
    print(bin.binId)


def find_best_path_for_amount_in(
    amount_in: int, route: list, token_in: str, token_out: str
) -> Quote:
    pass


def find_best_path_for_amount_out(
    amount_out: int, route: list, token_in: str, token_out: str
) -> Quote:
    pass


def get_reserves(pair: Pool) -> Tuple[int, int]:
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


print(get_reserves(pools[0]))
print(
    "reserveA and reserveB for the WAVAX/ USDC pool on avalanche : "
    + str(get_reserves(Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")))
)
