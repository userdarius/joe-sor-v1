import Bin
import Pool
import Token
import Quote
from typing import Tuple
import Structs
from decimal import Decimal, getcontext
from typing import List, Union
from constants import Constants

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
BIN_ID = "8376042"
NB_PART = 5
MAX_UINT256 = (1 << 256) - 1


avax_usdc = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")
usdc_usdt = Pool.get_pool(
    BARN_URL, CHAIN, "0x9B2Cc8E6a2Bbb56d6bE4682891a91B0e48633c72", "v2.0"
)
print(avax_usdc.name)
print(usdc_usdt.name + " " + str(usdc_usdt.activeBinId))


active_id = usdc_usdt.activeBinId

bins = {
    active_id - 5: [0, 1 * 10**18],
    active_id - 4: [0, 1 * 10**18],
    active_id - 3: [0, 1 * 10**18],
    active_id - 2: [0, 1 * 10**18],
    active_id - 1: [0, 1 * 10**18],
    active_id: [3 * 10**18, 1 * 10**18],
    active_id + 1: [3 * 10**18, 0],
    active_id + 2: [3 * 10**18, 0],
    active_id + 3: [3 * 10**18, 0],
    active_id + 4: [3 * 10**18, 0],
    active_id + 5: [3 * 10**18, 0],
}

print(bins)

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


bins = Bin.get_bin(BARN_URL, CHAIN, PAIR_ADDRESS, RADIUS, BIN_ID)
for bin in bins:
    print(bin.binId)


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
def _get_amount_out(pair, amount_in, token_out):
    amount_out = None
    virtual_amount_without_slippage = None
    fees = None

    swap_for_y = pair.tokenY == token_out

    if pair.version == "v2.0":
        try:
            # TODO : Rewrite using custom swapout function for LB2.0
            swap_amount_out, swap_fees = ILBLegacyRouter(_legacyRouterV2).get_swap_out(
                ILBLegacyPair(pair.pairAddress), amount_in, swap_for_y
            )

            amount_out = swap_amount_out
            # TODO : test _getV2Quote
            virtual_amount_without_slippage = getV2Quote(
                amount_in - fees, pair.activeBinId, pair.lbBinStep, swap_for_y
            )
            fees = (swap_fees * 10**18) / amount_in  # fee percentage in amount_in

        except Exception:
            pass

    elif pair.version == "v2.1":
        try:
            # TODO : Rewrite using custom swapout function for LB2.1
            amount_in_left, swap_amount_out, swap_fees = ILBRouter(
                _routerV2
            ).get_swap_out(ILBPair(pair.pairAddress), amount_in, swap_for_y)

            if amount_in_left == 0:
                amount_out = swap_amount_out
                # TODO : test _getV2Quote
                virtual_amount_without_slippage = getV2Quote(
                    amount_in - swap_fees, pair.activeBinId, pair.lbBinStep, swap_for_y
                )
                fees = (swap_fees * 10**18) / amount_in  # fee percentage in amount_in

        except Exception:
            pass

    return amount_out, virtual_amount_without_slippage, fees


# Returns the reserves of a pair
# @param pair The pair to get the reserves of
# @return reserveA, reserveB The reserves of the pair in tokenA and tokenB
def get_reserves(pair: Pool) -> Tuple[int, int]:
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


# Set the precision for Decimal numbers
getcontext().prec = 128


def getV2Quote(amount, activeId, binStep, swapForY):
    if swapForY:
        price = getPriceFromId(activeId, binStep)
        intermediate = (Decimal(amount) * price) / Decimal(2**Constants.SCALE_OFFSET)
        quote = int(intermediate)
    else:
        price = getPriceFromId(activeId, binStep)
        intermediate = Decimal(amount) / (
            (Decimal(2) ** Constants.SCALE_OFFSET) * price
        )
        quote = int(intermediate)

    return quote


def getPriceFromId(id, binStep):
    base = getBase(binStep)
    exponent = id - Constants.REAL_ID_SHIFT
    price = pow(base, exponent)
    return price


# Helpers for the previous utility functions
def getBase(binStep):
    return (
        Constants.SCALE
        + (binStep << Constants.SCALE_OFFSET) // Constants.BASIS_POINT_MAX
    )


def pow(x, y):
    invert = False
    if y == 0:
        return 1 << 128

    if y < 0:
        invert = True
        abs_y = -y

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


poolTest = Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")
idTest = poolTest.activeBinId
binStepTest = poolTest.lbBinStep
swapForYTest = True
amountTest = 1000000000000
quoteTest = getV2Quote(amountTest, idTest, binStepTest, swapForYTest)
print(quoteTest)  # weird returns 0 always

print(
    "Pool : "
    + str(pools[0].name)
    + " - (reserveA, reserveB) : "
    + str(get_reserves(pools[0]))
)
print(
    "reserveA and reserveB for the WAVAX/ USDC pool on avalanche : "
    + str(get_reserves(Pool.get_pool(BARN_URL, CHAIN, PAIR_ADDRESS, "v2.0")))
)
