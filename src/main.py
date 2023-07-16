import bins

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"


bins = bins.get_bins(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS)
for bin in bins:
    print(bin.binId)
