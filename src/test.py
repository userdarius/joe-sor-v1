import asyncio
import logging

from eth_abi import abi
from eth_utils import to_checksum_address

from joebot.src.abi.fee_bank_abi import FEE_BANK_ABI
from joebot.src.abi.multicall_abi import MULTICALL_ABI
from joebot.src.utils import encode_function


class FeeBank:
    def __init__(self, chain: str, config, w3, fee_manager):
        self.logger = logging.getLogger(f"{__name__}.{chain}")

        self.address = to_checksum_address(config.FEE_BANK_ADDRESS)
        self.contract = w3.eth.contract(address=self.address, abi=FEE_BANK_ABI)

        self.multicall = w3.eth.contract(
            address=to_checksum_address(config.MULTICALL_ADDRESS), abi=MULTICALL_ABI
        )

        self.fee_manager = fee_manager

        self.logger.info(f"Fee converter address: {self.address}")

    async def get_transfer_tax_rate(self, token, dic) -> int:
        if "to" not in dic:
            return 0  # Only the redistributed token will not have a "to" field

        swap_desc = dic["desc"]

        oneinch = to_checksum_address(dic["to"])
        raw_data = dic["raw_data"]

        (_, token_out, _, recipient, amount_in, min_amount_out, _) = swap_desc

        self.logger.info(f"Getting transfer tax rate for {amount_in} {token}")

        data = self.multicall.encodeABI(
            "aggregate",
            [
                [
                    [token_out, encode_function.balance_of(recipient)],
                    [token.address, encode_function.approve(oneinch, amount_in)],
                    [oneinch, f"{raw_data[:394]}{1:064x}{raw_data[458:]}"],
                    [token_out, encode_function.balance_of(recipient)],
                ]
            ],
        )

        loop = asyncio.get_running_loop()

        try:
            result = await loop.run_in_executor(
                None,
                self.contract.functions.delegateCall(self.multicall.address, data).call,
                {"from": self.fee_manager.address},
            )
        except Exception as e:
            self.logger.error(f"Error getting transfer tax rate for {token}: {e}")
            return 100  # 100% tax rate as the transfer is bugged

        (_, return_data) = abi.decode(["uint256", "bytes[]"], result)

        amount_before = abi.decode(["uint256"], return_data[0])[0]
        amount_after = abi.decode(["uint256"], return_data[3])[0]

        amount_received = amount_after - amount_before

        if min_amount_out < amount_received:
            return 0

        return ((min_amount_out - amount_received) / min_amount_out) * 100


def balance_of(address):
    BALANCE_OF = "0x70a08231"
    return f"{BALANCE_OF}{address[2:].zfill(64)}"