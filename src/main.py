import Bin
import Pool
import Token
import Quote
from typing import Tuple
import Structs
from decimal import Decimal, getcontext
from typing import List, Union
from constants import Constants
from math import ceil
from Structs import Routes, Route, Pair
import Params
from web3 import Web3

BARN_URL = "https://barn.traderjoexyz.com"
NODE_URL = "https://endpoints.omniatech.io/v1/avax/mainnet/public"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0x4224f6F4C9280509724Db2DbAc314621e4465C29"
NB_PART = 5
MAX_UINT256 = (1 << 256) - 1


BTC_b_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.1")
decimalX = BTC_b_USDC.tokenX.decimals
decimalY = BTC_b_USDC.tokenY.decimals
fetched_bin_step = BTC_b_USDC.lbBinStep
fetched_active_id = BTC_b_USDC.activeBinId

# BIN STATE
# fetch bins from API
bins = Bin.get_bins(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS, fetched_active_id)

# initialize an empty dictionary to store bins
bins_dict = {}

# iterate over bins and store in dictionary
for bin in bins:
    bins_dict[bin.binId] = [
        int(bin.reserveX * 10**decimalX),
        int(bin.reserveY * 10**decimalY),
    ]


params_fetched_from_rpc = Params.get_params(NODE_URL, PAIR_ADDRESS)


route = {"part": 0, "amount": 0, "pairs": []}
routes = {"tokens": [], "routes": []}


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


def _getAllRoutes(swapRoutes) -> List[Structs.Routes]:
    pass


# Returns the routes and parts for a given amount in
# @param allRoutes All routes to get the routes and parts for
# @param amountIn The amount of tokenIn to swap
# @return routes, parts The routes and parts for the given amount in
def _getRoutesAndParts(
    allRoutes: List[Structs.Routes], amountIn: int
) -> List[Structs.Routes]:
    pass


def _getAmountOutFromRoute(amountIn: int, route, pair):
    pass


# takes in a Pool object for pair, int as amountIn, Token object for tokenOut - TODO : check if tokenIn not needed for swap
def get_amount_out(pair, amount_in, token_out):
    amount_out = None
    virtual_amount_without_slippage = None
    fees = None

    swap_for_y = pair.tokenY == token_out
    fees = 0.003e18
    # 0.3% fees

    try:
        swap_amount_out = swap(
            amount_in, swap_for_y, params_fetched_from_rpc, fetched_bin_step, now
        )
        amount_out = swap_amount_out

        virtual_amount_without_slippage = getV2Quote(
            amount_in - fees, pair.activeBinId, pair.lbBinStep, swap_for_y
        )
        swap_fees = get_total_fee(params_fetched_from_rpc, pair.lbBinStep)
        fees = get_fee_amount(amount_in, swap_fees)
    except Exception:
        pass

    return amount_out, virtual_amount_without_slippage, fees


# Returns the reserves of a pair
# returns reserveA, reserveB. The reserves of the pair in tokenA and tokenB
def get_reserves(pair) -> Tuple[int, int]:
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


# Set the precision for Decimal numbers
# getcontext().prec = 128


# Calculate amountOut if amount was swapped with no slippage and no fees
def getV2Quote(amount, activeId, binStep, swapForY):
    if swapForY:
        quote = int(amount * get_price_from_id(activeId, binStep)) // (2**128)
    else:
        quote = int(amount * (2**128)) // get_price_from_id(activeId, binStep)

    return quote


def get_price_from_id(active_id, bin_step):
    base = (1 << 128) + (bin_step << 128) // 10_000
    exponent = active_id - 2**23
    return pow(base, exponent)


def pow(x, y):
    invert = False
    if y == 0:
        return 1 << 128

    if y < 0:
        invert = True
        abs_y = -y
    else:
        abs_y = y

    if abs_y < 0x100000:
        result = 1 << 128
        squared = x
        if x > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
            squared = MAX_UINT256 // x
            invert = not invert

        if abs_y & 0x1:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x2:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x4:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x8:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x10:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x20:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x40:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x80:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x100:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x200:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x400:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x800:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x1000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x2000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x4000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x8000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x10000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x20000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x40000:
            result = (result * squared) >> 128
        squared = (squared * squared) >> 128
        if abs_y & 0x80000:
            result = (result * squared) >> 128
    else:
        raise Exception("Uint128x128Math__PowOverflow")

    if result == 0:
        raise Exception("Uint128x128Math__PowUnderflow")

    if invert:
        return (1 << 256) // result
    else:
        return result


def get_price(bin_step, active_id):
    base = (1 << 128) + (bin_step << 128) // 10_000
    exponent = active_id - 2**23
    return pow(base, exponent)


def get_base_fee(params, bin_step):
    return params.base_factor * bin_step * 10**10


def get_variable_fee(params, bin_step):
    return (
        (params.volatility_accumulator * bin_step) ** 2
        * params.variable_fee_control
        // 100
    )


def get_total_fee(params, bin_step):
    return int(get_base_fee(params, bin_step) + get_variable_fee(params, bin_step))


def get_fee_amount(amount_in, fee):
    return ceil(amount_in * fee // 10**18)


def get_fee_amount_from(amount_in, fee):
    denominator = 10**18 - fee
    return ceil(amount_in * fee // denominator)


def get_amounts(bin_reserves, params, bin_step, swap_for_y, active_id, amount_in):
    price = get_price(bin_step, active_id)

    if swap_for_y:
        bin_reserve_out = bin_reserves[1]
        max_amount_in = (int(bin_reserve_out) << 128) // price
    else:
        bin_reserve_out = bin_reserves[0]
        max_amount_in = int(bin_reserve_out * price) >> 128

    total_fee = get_total_fee(params, bin_step)
    max_fee = get_fee_amount(max_amount_in, total_fee)
    max_amount_in += max_fee

    if amount_in >= max_amount_in:
        fee_amount = max_fee
        amount_in = max_amount_in
        amount_out = bin_reserve_out
    else:
        fee_amount = get_fee_amount_from(amount_in, total_fee)

        amount_in_without_fees = amount_in - fee_amount

        if swap_for_y:
            amount_out = amount_in_without_fees * price >> 128
        else:
            amount_out = (amount_in_without_fees << 128) // price

        if amount_out > bin_reserve_out:
            amount_out = bin_reserve_out

    return amount_in, int(amount_out), fee_amount


def get_protocol_fees(fee_amount, params):
    return fee_amount * params.protocol_share // 10**18


def get_next_non_empty_bin(swap_for_y, active_id):
    ids = list(bins_dict.keys())
    ids.sort()

    if swap_for_y:
        # return the first id that is less than active_id
        for id in ids[::-1]:
            if id < active_id:
                return id
    else:
        # return the first id that is greater than active_id
        for id in ids:
            if id > active_id:
                return id
    return None


def swap(amount_to_swap, swap_for_y, params, bin_step, block_timestamp):
    amount_in, amount_out = amount_to_swap, 0
    id = params.active_id

    params.update_references(block_timestamp)

    while amount_in > 0:
        bin_reserves = bins_dict.get(id)
        if bin_reserves is None:
            break
        params.update_volatility_accumulator(id)

        amount_in_with_fees, amount_out_of_bin, fee_amount = get_amounts(
            bin_reserves, params, bin_step, swap_for_y, id, amount_in
        )
        amount_in -= amount_in_with_fees
        amount_out += amount_out_of_bin

        protocol_fees = get_protocol_fees(fee_amount, params)

        if protocol_fees > 0:
            amount_in_with_fees -= protocol_fees

            # protocol_fees_total += protocol_fees

        if swap_for_y:
            bin_reserves[0] += amount_in_with_fees
            bin_reserves[1] -= amount_out_of_bin
        else:
            bin_reserves[0] -= amount_out_of_bin
            bin_reserves[1] += amount_in_with_fees

        if amount_in == 0:
            break

        id = get_next_non_empty_bin(swap_for_y, id)

    if amount_in > 0:
        raise Exception("Not enough liquidity")

    params.active_id = id

    return amount_out


# poolTest = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")
# idTest = poolTest.activeBinId
# binStepTest = poolTest.lbBinStep
# swapForYTest = True
USDCAmountTest = 1 * 10**6  # 1 USDC (6 decimals)
quoteTestUSDCToBTC = getV2Quote(
    USDCAmountTest, fetched_active_id, fetched_bin_step, False
)
print("quote test 1 USDC to BTC : " + str(quoteTestUSDCToBTC / 10**8) + " BTC")
BTCAmountTest = 1 * 10**8  # 1 BTC (8 decimals)
quoteTestBTCToUSDC = getV2Quote(
    BTCAmountTest, fetched_active_id, fetched_bin_step, True
)
print("quote test 1 BTC to USDC : " + str(quoteTestBTCToUSDC / 10**6) + " USDC")

# print(
#    "Pool : "
#    + str(pools[0].name)
#    + " - (reserveA, reserveB) : "
#    + str(get_reserves(pools[0]))
# )
# print(
#    "reserveA and reserveB for the BTC.b / USDC pool on avalanche : "
#    + str(get_reserves(Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")))
# )

now = params_fetched_from_rpc.time_of_last_update + 25


print("tokenX : " + BTC_b_USDC.tokenX.name)
print("tokenY : " + BTC_b_USDC.tokenY.name)

# Swap x to y (1 BTC.b to USDC)
print(swap(1 * 10**8, True, params_fetched_from_rpc, fetched_bin_step, now))


# Swap y to x (30000 USDC to BTC.b)
print(swap(30000 * 10**6, False, params_fetched_from_rpc, fetched_bin_step, now))


# Swap x to y (1 BTC.b to USDC)
print(get_amount_out(BTC_b_USDC, 1 * 10**8, BTC_b_USDC.tokenY))
