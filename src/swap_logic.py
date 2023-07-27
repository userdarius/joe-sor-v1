from math import log2, ceil

# We're taking LINK/AVAX/10bp (v2.1-> 0xc0dFC065894B20d79AADe34A63b5651061b135Cc) for the example, we use these prices:
AVAX_PRICE_IN_USD = 21
LINK_PRICE_IN_USD = 7
PAIR_BIN_STEP = 10
MAX_UINT256 = (1 << 256) - 1

start_price = (LINK_PRICE_IN_USD * 10**18) / (AVAX_PRICE_IN_USD * 10**18)
active_id = int(log2(start_price) / log2(1 + PAIR_BIN_STEP / 10_000) + 2**23)

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


class Params:
    def __init__(
        self,
        base_factor,
        filter_period,
        decay_period,
        reduction_factor,
        variable_fee_control,
        protocol_share,
        max_volatility_accumulator,
        volatility_accumulator,
        volatility_reference,
        index_reference,
        time_of_last_update,
        oracle_index,
        active_id,
    ):
        self.base_factor = base_factor
        self.filter_period = filter_period
        self.decay_period = decay_period
        self.reduction_factor = reduction_factor
        self.variable_fee_control = variable_fee_control
        self.protocol_share = protocol_share
        self.max_volatility_accumulator = max_volatility_accumulator
        self.volatility_accumulator = volatility_accumulator
        self.volatility_reference = volatility_reference
        self.index_reference = index_reference
        self.time_of_last_update = time_of_last_update
        self.oracle_index = oracle_index
        self.active_id = active_id

    def update_volatility_reference(self):
        self.volatility_reference = int(
            self.volatility_accumulator * self.reduction_factor // 10_000
        )

    def update_volatility_accumulator(self, active_id):
        delta_id = abs(active_id - self.index_reference)
        self.volatility_accumulator = min(
            self.volatility_reference + delta_id * 10_000,
            self.max_volatility_accumulator,
        )

    def update_references(self, block_timestamp):
        dt = block_timestamp - self.time_of_last_update

        if dt >= self.filter_period:
            self.index_reference = self.active_id
            if dt < self.decay_period:
                self.update_volatility_reference()
            else:
                self.volatility_reference = 0

    def update_volatility_parameters(self, active_id, block_timestamp):
        self.update_references(block_timestamp)
        self.update_volatility_accumulator(active_id)


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
        max_amount_in = (bin_reserve_out << 128) // price
    else:
        bin_reserve_out = bin_reserves[0]
        max_amount_in = bin_reserve_out * price >> 128

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

    return amount_in, amount_out, fee_amount


def get_protocol_fees(fee_amount, params):
    return fee_amount * params.protocol_share // 10**18


def get_next_non_empty_bin(swap_for_y, active_id):
    ids = list(bins.keys())
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
        bin_reserves = bins.get(id)
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


# Fetched on the pair itself
params = Params(
    10_000,
    30,
    600,
    5_000,
    40_000,
    1_000,
    350_000,
    35_000,
    15_000,
    8_387_697,
    1_681_321_730,
    0,
    active_id,
)

now = params.time_of_last_update + 25

# Swap x to y
print(swap(10 * 10**18, True, params, PAIR_BIN_STEP, now))

# Swap y to x
print(swap(3 * 10**18, False, params, PAIR_BIN_STEP, now))
