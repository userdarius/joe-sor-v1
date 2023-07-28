from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from src.abi.lbpair_abi import LBPAIR_ABI

NODE_URL = "https://endpoints.omniatech.io/v1/avax/mainnet/public"
ADDRESS = "0x4224f6F4C9280509724Db2DbAc314621e4465C29"


def get_params(node_url, pair_address):
    web3 = Web3(Web3.HTTPProvider(node_url))
    contract = web3.eth.contract(address=pair_address, abi=LBPAIR_ABI)
    static_params = contract.functions.getStaticFeeParameters().call()
    variable_params = contract.functions.getVariableFeeParameters().call()
    active_id = contract.functions.getActiveId().call()
    all_params = static_params + variable_params + [active_id]
    return Params(*all_params)

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

param = get_params(NODE_URL, ADDRESS)
print(param.decay_period)
print(get_block_timestamp(NODE_URL))