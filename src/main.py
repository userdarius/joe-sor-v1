import Bin
import Pool
import Token
import Quote
from typing import Tuple
import Structs
from decimal import Decimal, getcontext
from typing import List, Union
import Constants

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"
RADIUS = 25
PAIR_ADDRESS = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"
BIN_ID = "8376042"
NB_PART = 5

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


def _getAllRoutes(swapRoutes: Union[][]) -> List[Structs.Routes]:
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


# Returns the reserves of a pair
# @param pair The pair to get the reserves of
# @return reserveA, reserveB The reserves of the pair in tokenA and tokenB
def get_reserves(pair: Pool) -> Tuple[int, int]:
    reserveA = pair.reserveX
    reserveB = pair.reserveY
    return reserveA, reserveB


# Set the precision for Decimal numbers
getcontext().prec = 128

# Calculates a quote for a V2 pair
# @param amountIn The amount of tokenIn to swap
# @param activeId The active bin id of the pair
# @param binStep The bin step of the pair
# @param swapForY True if tokenIn is tokenX, false if tokenIn is tokenY
# @return quote Amount Out if _amount was swapped with no slippage and no fees
def getV2Quote(amount, activeId, binStep, swapForY):
    if swapForY:
        price = getPriceFromId(activeId, binStep)
        # Perform the mulShiftRoundDown operation
        intermediate = (Decimal(amount) * price) / Decimal(2 ** Constants.SCALE_OFFSET)
        # Convert to int and return
        quote = int(intermediate)
    else:
        price = getPriceFromId(activeId, binStep)
        # Perform the shiftDivRoundDown operation
        intermediate = Decimal(amount) / ((Decimal(2) ** Constants.SCALE_OFFSET) * price)
        # Convert to int and return
        quote = int(intermediate)

    return quote


def getPriceFromId(id, binStep):
    REAL_ID_SHIFT = 2 ** 23  # Placeholder for REAL_ID_SHIFT 
    base = getBase(binStep)
    exponent = id - REAL_ID_SHIFT
    price = pow(base, exponent)
    return price


# Helpers for the previous utility functions
def getBase(binStep):
    return Constants.SCALE + (binStep << Constants.SCALE_OFFSET) // Constants.BASIS_POINT_MAX

def pow(base, exponent):
    return Decimal(base) ** Decimal(exponent)

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
