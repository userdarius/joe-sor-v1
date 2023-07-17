import Bin
import Pool
import Token

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
BIN_ID = "8376042"

pools = Pool.get_pools(BARN_URL, CHAIN, "v2.0", 100)
for pool in pools:
    print(pool.pairAddress)

tokens = Token.get_tokens(BARN_URL, CHAIN)
for token in tokens:
    print(token.tokenAddress)

bins = Bin.get_bin(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS, BIN_ID)
for bin in bins:
    print(bin.priceXY)
