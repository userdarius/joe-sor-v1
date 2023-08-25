import Bin
import Pool
import Params
from math import ceil
from web3 import Web3
from collections import defaultdict, deque

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


def get_bins(pair, active_id, radius):
    bins = Bin.get_bins(BARN_URL, CHAIN, pair.pairAddress, radius, active_id)
    decimalX = 10**pair.tokenX.decimals
    decimalY = 10**pair.tokenY.decimals

    bins_dict = {}
    for bin in bins:
        bins_dict[bin.binId] = [
            int(bin.reserveX * decimalX),
            int(bin.reserveY * decimalY),
        ]
    return bins_dict


# def find_best_path_from_amount_out_multi_path(
#     swap_routes, amount_out, token_in, token_out
# ):
#     all_routes = get_all_routes(swap_routes, token_in, token_out)
#     return get_routes_and_parts(all_routes, amount_out, token_in, token_out)

def path_generator(best_routes):
    for route in best_routes:
        yield route_info["pair"]


def find_best_path_from_amount_in_multi_path(
    swap_routes, amount_in, token_in, token_out
):
    all_routes = get_all_routes(swap_routes, token_in, token_out)
    #filtered_routes = filter_low_liquidity_routes(all_routes, amount_in, token_in)
    return get_routes_and_parts(all_routes, amount_in, token_in, token_out)

def filter_low_liquidity_routes(routes, amount_in, token_in):
    filtered_routes = []
    for route in routes:
        current_route_amount_out = get_amount_out_from_route(
            amount_in, route, token_in, route[-1].tokenY
        )
        if current_route_amount_out > 0:
            filtered_routes.append(route)
    return filtered_routes


def isIn(pair, token):
    return (
        pair.tokenX.tokenAddress == token.tokenAddress
        or pair.tokenY.tokenAddress == token.tokenAddress
    )


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


def fetch_rpc_params(route):
    web3 = Web3(Web3.HTTPProvider(NODE_URL))
    params_fetched_from_rpc = Params.get_params(web3, BACKSTOP_NODE_URL, route)
    return params_fetched_from_rpc


# def get_amount_in(pair, amount_out, token_in, token_out, pair_params, when):
#     amount_in = None
#     virtual_amount_without_slippage = None
#     fees = None

#     swap_for_y = pair.tokenY == token_in
#     fees = 0.003e18
#     # 0.3% feesh
#     try:
#         swap_amount_in = swap_inversed(
#             pair, amount_out, swap_for_y, pair_params, pair.lbBinStep, when
#         )
#         amount_in = swap_amount_in

#         virtual_amount_without_slippage = get_v2_quote(
#             amount_out, pair.activeBinId, pair.lbBinStep, swap_for_y
#         )
#         swap_fees = get_total_fee(pair_params, pair.lbBinStep)
#         fees = get_fee_amount(amount_out, swap_fees)
#     except Exception as error:
#         print(f"An error occurred getting the amount in: {error}")

#     return amount_in, virtual_amount_without_slippage, fees


def get_amount_out(pair, amount_in, token_in, token_out, pair_params, when):
    amount_out = None
    virtual_amount_without_slippage = None
    fees = None

    swap_for_y = pair.tokenY == token_out
    fees = 0.003e18
    # 0.3% feesh
    try:
        swap_amount_out = swap(
            pair, amount_in, swap_for_y, pair_params, pair.lbBinStep, when
        )
        amount_out = swap_amount_out

        virtual_amount_without_slippage = get_v2_quote(
            amount_in, pair.activeBinId, pair.lbBinStep, swap_for_y
        )
        swap_fees = get_total_fee(pair_params, pair.lbBinStep)
        fees = get_fee_amount(amount_in, swap_fees)
    except Exception as error:
        print(f"An error occurred getting the amount out: {error}")

    return amount_out, virtual_amount_without_slippage, fees


def get_ordered_tokens(route, token_in, token_out):
    if not all(hasattr(pair, "tokenX") and hasattr(pair, "tokenY") for pair in route):
        raise Exception(
            "Invalid route structure. Pairs must have 'tokenX' and 'tokenY' attributes."
        )

    tokens = [token_in]
    current_token = token_in
    seen_tokens = set()

    for pair in route:
        if not hasattr(current_token, "tokenAddress"):
            raise AttributeError("Current token lacks 'tokenAddress' attribute.")

        if current_token.tokenAddress == pair.tokenX.tokenAddress:
            current_token = pair.tokenY
        elif current_token.tokenAddress == pair.tokenY.tokenAddress:
            current_token = pair.tokenX
        else:
            print(
                "current token address : "
                + current_token.tokenAddress
                + " "
                + current_token.name
            )
            print(
                "pair tokenX address : "
                + pair.tokenX.tokenAddress
                + " "
                + pair.tokenX.name
            )
            print(
                "pair tokenY address : "
                + pair.tokenY.tokenAddress
                + " "
                + pair.tokenY.name
            )
            print("expected pair : " + pair.name)
            raise Exception(
                f"Invalid route: Token mismatch at {current_token.tokenAddress}"
            )

        if current_token.tokenAddress in seen_tokens:
            raise Exception(
                f"Cyclic route detected at token {current_token.tokenAddress}"
            )
        seen_tokens.add(current_token.tokenAddress)

        tokens.append(current_token)

    if tokens[-1].tokenAddress != token_out.tokenAddress:
        raise Exception(
            f"Invalid route: Expected to end at {token_out.tokenAddress}, but ended at {tokens[-1].tokenAddress}"
        )

    return tokens


def get_amount_out_from_route(amount_in, route, token_in, token_out):
    amounts = []
    virtual_amounts_without_slippage = []
    fees = []
    amounts.append(amount_in)
    virtual_amounts_without_slippage.append(amount_in)
    tokens = get_ordered_tokens(route, token_in, token_out)
    route_params = fetch_rpc_params(route)

    try:
        for i, _ in enumerate(route):
            if amount_in > 0:
                token_in = tokens[i]
                token_out = tokens[i + 1]

                # print("pair : " + str(route[i].name))
                # print("tokenIn : " + token_in.name)
                # print("tokenOut : " + token_out.name)
                # print("amount in : " + str(amount_in) + " " + str(token_in.name))

                now = route_params[i].time_of_last_update + 25
                pair_params = route_params[i]

                amount_out, virtual_amount_without_slippage, fee = get_amount_out(
                    route[i], amount_in, token_in, token_out, pair_params, now
                )
                # print("amount out : " + str(amount_out) + " " + str(token_out.name))
                amount_in = amount_out
                fees.append(fee)
                # print(fees)
                # print("base factor : " + str(pair_params.base_factor))

                amounts.append(amount_out)
                virtual_amounts_without_slippage.append(virtual_amount_without_slippage)

    except Exception as error:
        print(f"An error occurred getting the amount out from the route: {error}")

    return amounts, virtual_amounts_without_slippage, fees


# Returns the reserves of a pair
# returns reserveA, reserveB. The reserves of the pair in tokenA and tokenB
def get_reserves(pair):
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


# Set the precision for Decimal numbers
# getcontext().prec = 128


def get_routes_and_parts(all_routes, amount_in, initial_token_in, initial_token_out):
    route_part = 0
    route_amount = 0
    best_routes = []  # List to store the best routes for each part

    for i in range(NB_PART):
        print("\npart : " + str(i))
        best_index_route = None
        best_index_pairs = None
        best_amount = 0

        for j, route in enumerate(all_routes):
            print("\n")
            for pair in route:
                print(pair.name + " " + str(pair.version) + " " + str(pair.pairAddress))

            # Get the amount out once for the entire route
            (
                amounts,
                virtual_amounts_without_slippage,
                fees,
            ) = get_amount_out_from_route(
                (amount_in * (i + 1)) // NB_PART,
                route,
                initial_token_in,
                initial_token_out,
            )

            amount_out = amounts[len(amounts)-1]
            print("amount out : " + str(amount_out))

            if amount_out is not None and amount_out > route_amount:
                amount_out = amount_out - route_amount
                for k, _ in enumerate(route):
                    if amount_out > best_amount:
                        best_amount = amount_out
                        best_index_pairs = k
                        best_index_route = j

        # Store the best route and amount for this part if they exist
        if best_index_route is not None and best_index_pairs is not None:
            best_routes.append(
                {
                    "part": route_part,
                    "route_index": best_index_route,
                    "pair_index": best_index_pairs,
                    "amount": best_amount,
                }
            )
            route_part += 1
            route_amount = best_amount

    return best_routes


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


# def get_required_amount_in(
#     bin_reserves, params, bin_step, swap_for_y, active_id, desired_amount_out
# ):
#     price = get_price(bin_step, active_id)

#     if swap_for_y:
#         bin_reserve_out = bin_reserves[1]
#         amount_in_without_fees = (desired_amount_out << 128) // price

#         if desired_amount_out > bin_reserve_out:
#             print("desired amount out is more than the reserve")
#             return None, None

#     else:
#         bin_reserve_out = bin_reserves[0]
#         # Calculate the amount_in without fees based on desired output
#         amount_in_without_fees = (desired_amount_out << 128) / price

#         # Check if the desired output is more than the reserve; if so, it's not possible
#         if desired_amount_out > bin_reserve_out:
#             return None, None

#     # Now, determine the fee for this raw amount_in
#     total_fee = get_total_fee(params, bin_step)
#     fee_amount = get_fee_amount_from(amount_in_without_fees, total_fee)

#     # Add the fee to the raw cost to get the total amount_in
#     amount_in = amount_in_without_fees + fee_amount

#     return int(amount_in), int(desired_amount_out), int(fee_amount)


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
    print("swapping through : " + pair.name)
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
        print(
            f"Warning: Only {amount_to_swap - amount_in} was swapped due to insufficient liquidity"
        )

    params.active_id = id

    return amount_out


# def swap_inversed(pair, amount_swapped, swap_for_y, params, bin_step, block_timestamp):
#     amount_in, amount_out = 0, amount_swapped
#     id = params.active_id
#     bins_dict = get_bins(pair, id, RADIUS)
#     params.update_references(block_timestamp)
#     print("swapping through : " + pair.name)
#     while amount_out > 0:
#         bin_reserves = bins_dict.get(id)
#         if bin_reserves is None:
#             break

#         params.update_volatility_accumulator(id)
#         amount_in, desired_amount_out, fee_amount = get_required_amount_in(
#             bin_reserves, params, bin_step, swap_for_y, id, amount_out
#         )


v2pools = Pool.get_pools(BARN_URL, CHAIN, "all", 100)
print("Amount of pools : " + str(len(v2pools)))

routesAU = get_all_routes(v2pools, AVAX_USDC.tokenX, AVAX_USDC.tokenY)
routesBU = get_all_routes(v2pools, BTC_B_USDC.tokenX, BTC_B_USDC.tokenY)

tokenInAU = AVAX_USDC.tokenX  # AVAX
tokenOutAU = AVAX_USDC.tokenY  # USDC
tokenInBU = BTC_B_USDC.tokenX  # BTC.b
tokenOutBU = BTC_B_USDC.tokenY  # USDC

print("Amount of routes : " + str(len(routesBU)))
print(" ")

# Avax to USDC
for i, route in enumerate(routesBU):
    print(f"route {i} : ")
    for pair in route:
        print(pair.name + " " + pair.version)
    print(" ")

# filtered_routes = filter_low_liquidity_routes(routesBU, 1 * 10**18, tokenInBU)



path = find_best_path_from_amount_in_multi_path(
    v2pools, 1 * 10**6, tokenInBU, tokenOutBU
)

print(" ")
for route_info in path:
    print(f"Part : {route_info['part']}")
    print(f"Route Index: {route_info['route_index']}")
    print(f"Pair Index: {route_info['pair_index']}")
    print(f"Amount: {route_info['amount']}")
    print("-" * 50)  # print a separator for clarity
