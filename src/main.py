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
from Structs import Routes, Route
import Params
from web3 import Web3

BARN_URL = "https://barn.traderjoexyz.com"
NODE_URL = "https://endpoints.omniatech.io/v1/avax/mainnet/public"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
NB_PART = 5
MAX_UINT256 = (1 << 256) - 1


AVAX_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.1")
decimalX = AVAX_USDC.tokenX.decimals
decimalY = AVAX_USDC.tokenY.decimals
fetched_bin_step = AVAX_USDC.lbBinStep
fetched_active_id = AVAX_USDC.activeBinId

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
now = params_fetched_from_rpc.time_of_last_update + 25


# route = {"part": 0, "amount": 0, "pairs": []}
# routes = {"tokens": [], "routes": []}

# list of all tokens on the avalanche dex
tokens = Token.get_tokens(BARN_URL, CHAIN)


def find_best_path_from_amount_in_multi_path(swap_routes, amount_in):
    all_routes = get_all_routes(swap_routes)
    return get_routes_and_parts(all_routes, amount_in)


tokenIn = AVAX_USDC.tokenX
tokenOut = AVAX_USDC.tokenY

v2pools = Pool.get_pools(BARN_URL, CHAIN, "v2.0", 100)
for pool in v2pools:
    print(
        pool.name
        + " - "
        + "tokenX : "
        + str(pool.tokenX.name)
        + " - "
        + "tokenY : "
        + str(pool.tokenY.name)
    )


def isIn(pair, token):
    return pair.tokenX.name == token.name or pair.tokenY.name == token.name


def get_all_routes(pairs):
    routes = []

    for i in range(len(pairs)):
        pair = pairs[i]
        other = None

        if pair.tokenX.name == tokenIn.name:
            other = pair.tokenY
        elif pair.tokenY.name == tokenIn.name:
            other = pair.tokenX
        else:
            continue

        if other.name == tokenOut.name:
            routes.append([pairs[i]])
            continue

        for j in range(i + 1, len(pairs)):
            inner_other = other

            if pairs[j].tokenX.name == inner_other.name:
                inner_other = pairs[j].tokenY
            elif pairs[j].tokenY.name == inner_other.name:
                inner_other = pairs[j].tokenX
            else:
                continue

            if inner_other.name == tokenOut.name:
                routes.append([pairs[i], pairs[j]])
                continue

            for k in range(j + 1, len(pairs)):
                if isIn(pairs[k], inner_other) and isIn(pairs[k], tokenOut):
                    routes.append([pairs[i], pairs[j], pairs[k]])

    return routes


routes = get_all_routes(v2pools)

for route in routes:
    print("route : ")
    for pair in route:
        print(pair.tokenX.name + " - " + pair.tokenY.name)


# Returns the routes and parts for a given amount in
# @param allRoutes All routes to get the routes and parts for
# @param amountIn The amount of tokenIn to swap
# @return routes, parts The routes and parts for the given amount in
def get_routes_and_parts(
    all_routes: List[Structs.Routes], amount_in: int
) -> List[Structs.Routes]:
    for i in range(NB_PART):
        best_index_route = 0
        best_index_pairs = 0
        best_amount = 0

        for j in range(len(all_routes)):
            routes = all_routes[j].routes

            for k in range(len(routes)):
                route = routes[k]
                (
                    amounts,
                    virtual_amounts_without_slippage,
                    fees,
                ) = get_amount_out_from_route(
                    amount_in * route.part + 1 / NB_PART,
                    all_routes[j].tokens,
                    route.pairs,
                )
                amount_out = amounts[len(amounts) - 1]

                if amount_out > route.amount:
                    amount_out = amount_out - route.amount
                    if amount_out > best_amount:
                        best_amount = amount_out
                        best_index_pairs = k
                        best_index_route = j
    pass


def get_amount_out_from_route(amount_in: int, route, pairs):
    length = len(route) - 1
    amounts = []
    virtual_amounts_without_slippage = []
    fees = []

    amounts[0] = amount_in
    virtual_amounts_without_slippage[0] = amount_in

    for i in range(length):
        if amount_in > 0:
            amount_out, virtual_amount_without_slippage, fee = get_amount_out(
                pairs[i], amount_in, route[i], route[i + 1]
            )
            amount_in = amount_out
            fees[i] = fee

            amounts[i + 1] = amount_out
            virtual_amounts_without_slippage[i + 1] = virtual_amount_without_slippage

    return amounts, virtual_amounts_without_slippage, fees


# takes in a Pool object for pair, int as amountIn, Token object for tokenOut - TODO : check if tokenIn not needed for swap
def get_amount_out(pair, amount_in, token_in, token_out):
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

        virtual_amount_without_slippage = get_v2_quote(
            amount_in, pair.activeBinId, pair.lbBinStep, swap_for_y
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
def get_v2_quote(amount, activeId, binStep, swapForY):
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
quoteTestUSDCToAVAX = get_v2_quote(
    USDCAmountTest, fetched_active_id, fetched_bin_step, False
)
print("quote test 1 USDC to AVAX : " + str(quoteTestUSDCToAVAX / 10**18) + " AVAX")
AVAXAmountTest = 1 * 10**18  # 1 AVAX (18 decimals)
quoteTestAVAXToUSDC = get_v2_quote(
    AVAXAmountTest, fetched_active_id, fetched_bin_step, True
)
print("quote test 1 AVAX to USDC : " + str(quoteTestAVAXToUSDC / 10**6) + " USDC")

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
print(swap(1 * 10**8, True, params_fetched_from_rpc, fetched_bin_step, now))


# Swap y to x (30000 USDC to AVAX.b)
print(swap(30000 * 10**6, False, params_fetched_from_rpc, fetched_bin_step, now))


# Swap x to y (1 AVAX.b to USDC)
# print(get_amount_out(AVAX_USDC, 1 * 10**8, AVAX_USDC.tokenY))


# Get all routes
# print(get_all_routes([AVAX_USDC.tokenX, AVAX_USDC.tokenY]))
