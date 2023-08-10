from web3 import Web3
from abi.lbpair_abi import LBPAIR_ABI
from abi.multicall_abi import MULTICALL_ABI
from web3.middleware import geth_poa_middleware
from eth_abi import abi


MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"


def get_params(web3, node_url, backstop_node_url, pair_address):
    if not web3.is_connected():
        print("Primary node not connected. Trying backstop node.")
        web3 = Web3(Web3.HTTPProvider(backstop_node_url))

        if not web3.is_connected():
            print("Backstop node not connected either.")
            return None

    try:
        multicall = web3.eth.contract(
            address=Web3.to_checksum_address(MULTICALL_ADDRESS), abi=MULTICALL_ABI
        )

        contract = web3.eth.contract(address=pair_address, abi=LBPAIR_ABI)
        print(f"Connected to {node_url}")

        calls = [
            [pair_address, contract.encodeABI(fn_name="getStaticFeeParameters")],
            [pair_address, contract.encodeABI(fn_name="getVariableFeeParameters")],
            [pair_address, contract.encodeABI(fn_name="getActiveId")],
        ]
        data = multicall.encodeABI(fn_name="aggregate", args=[calls])

        result = web3.eth.call({"to": MULTICALL_ADDRESS, "data": data})

        (_, return_data) = abi.decode(["uint256", "bytes[]"], result)

        static_params = abi.decode(
            ["uint16", "uint16", "uint16", "uint16", "uint24", "uint16", "uint24"],
            return_data[0],
        )
        variable_params = abi.decode(
            ["uint24", "uint24", "uint24", "uint40"], return_data[1]
        )
        active_id = abi.decode(["uint24"], return_data[2])

        print(f"Static params: {static_params}")
        print(f"Variable params: {variable_params}")
        print(f"Active ID: {active_id}")

        all_params = static_params + variable_params + (active_id,)
        print(f"All params: {all_params}")

        return Params(*all_params)

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


# param = get_params(NODE_URL, ADDRESS)
# print(param.decay_period)
# print(get_block_timestamp(NODE_URL))
