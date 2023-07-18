import Bin
import Pool
import Token
from math import log2

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

current_price_xy = bins[0].priceXY
current_price_yx = bins[0].priceYX
PAIR_BIN_STEP = pool.lbBinStep

log_price = (current_price_xy * 10**18) / (current_price_yx * 10**18)
active_id = int(log2(log_price) / log2(1 + PAIR_BIN_STEP / 10_000) + 2**23)

print(active_id)
