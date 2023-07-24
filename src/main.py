import Bin
import Pool
import Token
import Quote

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
BIN_ID = "8376042"

pools = Pool.get_pools(BARN_URL, CHAIN, "v2.0", 100)
for pool in pools:
    print(pool.name + " - " + pool.pairAddress)

tokens = Token.get_tokens(BARN_URL, CHAIN)
for token in tokens:
    print(token.name + " - " + token.tokenAddress)

for pool in pools:
    print(pool.name + " - " + str(pool.activeBinId))

bins = Bin.get_bin(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS, BIN_ID)
for bin in bins:
    print(bin.binId)


# simulate swap
def swap(amount_to_swap: int, token_in: str, token_out: str, bin_step: int):
    amount_in, amount_out = amount_to_swap, 0
    active_bin_id = pools[0].activeBinId

    while amount_in > 0:
        bin_reserves = bins.get(active_bin_id)
        if bin_reserves is None:
            break


def find_best_path_for_amount_in(
    amount_in: int, route: list, token_in: str, token_out: str
) -> Quote:
    pass


def find_best_path_for_amount_out(
    amount_out: int, route: list, token_in: str, token_out: str
) -> Quote:
    pass
