from web3 import Web3
from abi.lb_v2_1_pair_abi import LBP_V2_1_PAIR_ABI
from abi.lb_v2_0_pair_abi import LBP_V2_0_PAIR_ABI
from abi.multicall_abi import MULTICALL_ABI
from web3.middleware import geth_poa_middleware
from eth_abi import abi
from web3.exceptions import ContractLogicError


MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"


def connect_to_web3(web3, backstop_node_url):
    if not web3.is_connected():
        print("Primary node not connected. Trying backstop node.")
        web3 = Web3(Web3.HTTPProvider(backstop_node_url))

        if not web3.is_connected():
            print("Backstop node not connected either.")
            return None
    return web3


def initialize_multicall_contract(web3):
    return web3.eth.contract(
        address=Web3.to_checksum_address(MULTICALL_ADDRESS), abi=MULTICALL_ABI
    )


def prepare_calls(web3, route):
    calls = []
    for pair in route:
        if pair.version == "v2.1":
            calls.extend(prepare_v2_1_calls(web3, pair))
        elif pair.version == "v2.0":
            calls.extend(prepare_v2_0_calls(web3, pair))
    return calls


def prepare_v2_1_calls(web3, pair):
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(pair.pairAddress),
        abi=LBP_V2_1_PAIR_ABI,
    )
    return [
        [
            Web3.to_checksum_address(pair.pairAddress),
            contract.encodeABI(fn_name="getStaticFeeParameters"),
        ],
        [
            Web3.to_checksum_address(pair.pairAddress),
            contract.encodeABI(fn_name="getVariableFeeParameters"),
        ],
        [
            Web3.to_checksum_address(pair.pairAddress),
            contract.encodeABI(fn_name="getActiveId"),
        ],
    ]


def prepare_v2_0_calls(web3, pair):
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(pair.pairAddress),
        abi=LBP_V2_0_PAIR_ABI,
    )
    return [
        [
            Web3.to_checksum_address(pair.pairAddress),
            contract.encodeABI(fn_name="feeParameters"),
        ],
        [
            Web3.to_checksum_address(pair.pairAddress),
            contract.encodeABI(fn_name="getReservesAndId"),
        ],
    ]


def aggregate_with_retry(multicall, calls, web3, backstop_node_url, MAX_RETRIES=3):
    for _ in range(MAX_RETRIES):
        try:
            (_, return_data) = multicall.functions.aggregate(calls).call()
            return return_data
        except ContractLogicError as e:
            if "Multicall3: call failed" in str(e):
                web3 = connect_to_web3(web3, backstop_node_url)
                multicall = initialize_multicall_contract(web3)
    raise Exception("Max retries reached without a successful call")


def process_v2_1_data(return_data, start_index):
    pairs_params = []
    # Here, start_index is the starting point in return_data from which we should process data for the current pair
    static_params = abi.decode(
        ["uint16", "uint16", "uint16", "uint16", "uint24", "uint16", "uint24"],
        return_data[start_index],
    )

    variable_params = abi.decode(
        ["uint24", "uint24", "uint24", "uint40"], return_data[start_index + 1]
    )
    active_id = abi.decode(["uint24"], return_data[start_index + 2])
    print("static_params : " + str(static_params))
    print("variable_params : " + str(variable_params))
    print("active_id : " + str(active_id))
    all_params = static_params + variable_params + active_id
    params_instance = Params(*all_params)
    pairs_params.append(params_instance)

    return pairs_params


def process_v2_0_data(return_data, start_index):
    pairs_params = []
    # Here, start_index is the starting point in return_data from which we should process data for the current pair
    (
        binStep,
        baseFactor,
        filterPeriod,
        decayPeriod,
        reductionFactor,
        variableFeeControl,
        protocolShare,
        maxVolatilityAccumulated,
        volatilityAccumulated,
        volatilityReference,
        indexRef,
        time,
    ) = abi.decode(
        [
            "uint16",
            "uint16",
            "uint16",
            "uint16",
            "uint16",
            "uint24",
            "uint16",
            "uint24",
            "uint24",
            "uint24",
            "uint24",
            "uint40",
        ],
        return_data[start_index],
    )
    # print("fee_params : " + str(fee_params))

    reservesX, reservesY, active_id = abi.decode(
        ["uint256", "uint256", "uint256"], return_data[start_index + 1]
    )
    print("reservesX : " + str(reservesX))
    print("reservesY : " + str(reservesY))
    print("active_id : " + str(active_id))
    all_params = (
        baseFactor,
        filterPeriod,
        decayPeriod,
        reductionFactor,
        variableFeeControl,
        protocolShare,
        maxVolatilityAccumulated,
        volatilityAccumulated,
        volatilityReference,
        indexRef,
        time,
        active_id,
    )
    params_instance = Params(*all_params)
    pairs_params.append(params_instance)

    return pairs_params


def process_return_data(return_data, route):
    all_pairs_params = []
    index = 0
    for pair in route:
        if pair.version == "v2.1":
            all_pairs_params.extend(process_v2_1_data(return_data, index))
            index += 3  # because there are 3 data points for each pair in v2.1
        elif pair.version == "v2.0":
            all_pairs_params.extend(process_v2_0_data(return_data, index))
            index += 2  # because there are 2 data points for each pair in v2.0
    return all_pairs_params


def get_params(web3, backstop_node_url, route):
    web3 = connect_to_web3(web3, backstop_node_url)
    if web3 is None:
        return None
    multicall = initialize_multicall_contract(web3)
    calls = prepare_calls(web3, route)
    try:
        return_data = aggregate_with_retry(multicall, calls, web3, backstop_node_url)
        return process_return_data(
            return_data, route
        )  # Passing the entire route for dynamic processing
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_block_timestamp(node_url):
    web3 = Web3(Web3.HTTPProvider(node_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3.eth.get_block("latest").timestamp


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
