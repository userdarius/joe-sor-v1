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
PAIR_ADDRESS_WAVAX_USDC = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
PAIR_ADDRESS_BTC_B_USDC = "0x4224f6F4C9280509724Db2DbAc314621e4465C29"
NB_PART = 5
MAX_UINT256 = (1 << 256) - 1


AVAX_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS_WAVAX_USDC, "v2.1")
BTC_B_USDC = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS_BTC_B_USDC, "v2.1")


def get_bins(pair, active_id, radius):
    print("active_id : " + str(active_id))
    print("radius : " + str(radius))
    bins = Bin.get_bins(BARN_URL, CHAIN, pair.pairAddress, radius, active_id)
    decimalX = pair.tokenX.decimals
    decimalY = pair.tokenY.decimals
    bins_dict = {}
    for bin in bins:
        bins_dict[bin.binId] = [
            int(bin.reserveX * 10**decimalX),
            int(bin.reserveY * 10**decimalY),
        ]
    return bins_dict


def find_best_path_from_amount_in_multi_path(
    swap_routes, amount_in, token_in, token_out
):
    all_routes = get_all_routes(swap_routes, token_in, token_out)
    return get_routes_and_parts(all_routes, amount_in)


def isIn(pair, token):
    return pair.tokenX.name == token.name or pair.tokenY.name == token.name


def get_all_routes(pairs, tokenIn, tokenOut):
    routes = []

    for i, pair in enumerate(pairs):
        other = None

        if pair.tokenX.tokenAddress == tokenIn.tokenAddress:
            other = pair.tokenY
        elif pair.tokenY.tokenAddress == tokenIn.tokenAddress:
            other = pair.tokenX
        else:
            continue

        if other.tokenAddress == tokenOut.tokenAddress:
            routes.append([pair])
            continue

        for j, next_pair in enumerate(pairs[i + 1 :]):
            inner_other = other

            if next_pair.tokenX.tokenAddress == inner_other.tokenAddress:
                inner_other = next_pair.tokenY
            elif next_pair.tokenY.tokenAddress == inner_other.tokenAddress:
                inner_other = next_pair.tokenX
            else:
                continue

            if inner_other.tokenAddress == tokenOut.tokenAddress:
                routes.append([pair, next_pair])
                continue

            for k, third_pair in enumerate(pairs[j + i + 2 :]):
                if isIn(third_pair, inner_other) and isIn(third_pair, tokenOut):
                    routes.append([pair, next_pair, third_pair])

    return routes


def fetch_rpc_params(PAIR_ADDRESS):
    params_fetched_from_rpc = Params.get_params(
        NODE_URL, Web3.to_checksum_address(PAIR_ADDRESS)
    )
    now = params_fetched_from_rpc.time_of_last_update + 25
    return params_fetched_from_rpc, now


def get_amount_out(pair, amount_in, token_in, token_out):
    amount_out = None
    virtual_amount_without_slippage = None
    fees = None
    print("yo")
    print(pair.pairAddress)
    params_fetched_from_rpc, now = fetch_rpc_params(
        Web3.to_checksum_address(pair.pairAddress)
    )
    print("yo")

    swap_for_y = pair.tokenY == token_out
    fees = 0.003e18
    # 0.3% fees
    try:
        swap_amount_out = swap(
            pair, amount_in, swap_for_y, params_fetched_from_rpc, pair.lbBinStep, now
        )
        amount_out = swap_amount_out

        virtual_amount_without_slippage = get_v2_quote(
            amount_in, pair.activeBinId, pair.lbBinStep, swap_for_y
        )

        swap_fees = get_total_fee(params_fetched_from_rpc, pair.lbBinStep)
        fees = get_fee_amount(amount_in, swap_fees)
    except Exception as e:
        print(f"An error occurred getting the amount out: {e}")

    return amount_out, virtual_amount_without_slippage, fees


def get_ordered_tokens(route, token_in, token_out):
    tokens = [token_in]
    current_token = token_in

    for pair in route:
        if current_token.tokenAddress == pair.tokenX.tokenAddress:
            current_token = pair.tokenY
        elif current_token.tokenAddress == pair.tokenY.tokenAddress:
            current_token = pair.tokenX
        else:
            raise Exception("Invalid route")
        tokens.append(current_token)

    if tokens[-1].tokenAddress != token_out.tokenAddress:
        raise Exception("Invalid route")

    return tokens


def get_amount_out_from_route(amount_in, route, token_in, token_out):
    amounts = []
    virtual_amounts_without_slippage = []
    fees = []
    amounts.append(amount_in)
    virtual_amounts_without_slippage.append(amount_in)
    tokens = get_ordered_tokens(route, token_in, token_out)

    try:
        for i in range(len(route)):
            if amount_in > 0:
                token_in = tokens[i]
                token_out = tokens[i + 1]

                print("pair : " + str(route[i].name))
                print("tokenIn : " + token_in.name)
                print("tokenOut : " + token_out.name)
                print("amount in : " + str(amount_in))

                amount_out, virtual_amount_without_slippage, fee = get_amount_out(
                    route[i], amount_in, token_in, token_out
                )
                print("amount out : " + str(amount_out) + " " + str(token_out.name))
                amount_in = amount_out
                fees.append(fee)

                amounts.append(amount_out)
                virtual_amounts_without_slippage.append(virtual_amount_without_slippage)

    except Exception as e:
        print(f"An error occurred getting the amount out from the route: {e}")

    return amounts, virtual_amounts_without_slippage, fees


# Returns the reserves of a pair
# returns reserveA, reserveB. The reserves of the pair in tokenA and tokenB
def get_reserves(pair):
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


# Set the precision for Decimal numbers
# getcontext().prec = 128


# Returns the routes and parts for a given amount in
# @param allRoutes All routes to get the routes and parts for
# @param amountIn The amount of tokenIn to swap
# @return routes, parts The routes and parts for the given amount in
def get_routes_and_parts(all_routes, amount_in):
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


def get_next_non_empty_bin(swap_for_y, active_id, bins_dict):
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


def swap(pair, amount_to_swap, swap_for_y, params, bin_step, block_timestamp):
    amount_in, amount_out = amount_to_swap, 0
    id = params.active_id
    bins_dict = get_bins(pair, id, RADIUS)
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

        id = get_next_non_empty_bin(swap_for_y, id, bins_dict)

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
    USDCAmountTest, AVAX_USDC.activeBinId, AVAX_USDC.lbBinStep, False
)
# # print("quote test 1 USDC to AVAX : " + str(quoteTestUSDCToAVAX / 10**18) + " AVAX")
AVAXAmountTest = 1 * 10**18  # 1 AVAX (18 decimals)
quoteTestAVAXToUSDC = get_v2_quote(
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


# Get all routes


v2pools = Pool.get_pools(BARN_URL, CHAIN, "all", 100)

routesAU = get_all_routes(v2pools, AVAX_USDC.tokenX, AVAX_USDC.tokenY)
routesBU = get_all_routes(v2pools, BTC_B_USDC.tokenX, BTC_B_USDC.tokenY)


tokenInAU = AVAX_USDC.tokenX
tokenOutAU = AVAX_USDC.tokenY
tokenInBU = BTC_B_USDC.tokenX
tokenOutBU = BTC_B_USDC.tokenY

for route in routesBU:
    print("route : ")
    for pair in route:
        print(pair.tokenX.name + " - " + pair.tokenY.name)
    print(" ")

print(get_amount_out_from_route(1*10**8, routesBU[2], tokenInBU, tokenOutBU))
