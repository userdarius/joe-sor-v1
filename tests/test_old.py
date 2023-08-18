import pytest
import src.main as main
import src.Pool as Pool

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
BTC_B_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS_BTC_B_USDC, "v2.1")# poolTest = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")
# idTest = poolTest.activeBinId
# binStepTest = poolTest.lbBinStep
# swapForYTest = True
USDCAmountTest = 1 * 10**6  # 1 USDC (6 decimals)
quoteTestUSDCToAVAX = main.get_v2_quote(
    USDCAmountTest, AVAX_USDC.activeBinId, AVAX_USDC.lbBinStep, False
)
# # print("quote test 1 USDC to AVAX : " + str(quoteTestUSDCToAVAX / 10**18) + " AVAX")
AVAXAmountTest = 1 * 10**18  # 1 AVAX (18 decimals)
quoteTestAVAXToUSDC = main.get_v2_quote(
    AVAXAmountTest, AVAX_USDC.activeBinId, AVAX_USDC.lbBinStep, True
)
# print("quote test 1 AVAX to USDC : " + str(quoteTestAVAXToUSDC / 10**6) + " USDC")

# print(
#    "Pool : "
#    + str(pools[0].name)
#    + " - (reserveA, reserveB) : "
#    + str(get_reserves(pools[0]))
# )
# print(
#    "reserveA and reserveB for the AVAX.b / USDC pool on avalanche : "
#    + str(get_reserves(Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")))
# )

# Swap x to y (1 AVAX.b to USDC)
# print(swap(1 * 10**8, True, params_fetched_from_rpc, fetched_bin_step, now))


# Swap y to x (30000 USDC to AVAX.b)
# print(swap(30000 * 10**6, False, params_fetched_from_rpc, fetched_bin_step, now))


# Swap x to y (1 AVAX.b to USDC)
# print(get_amount_out(AVAX_USDC, 1 * 10**8, AVAX_USDC.tokenX, AVAX_USDC.tokenY))
# print(get_amount_out(AVAX_USDC, 1 * 10**18, AVAX_USDC.tokenX, AVAX_USDC.tokenY))
