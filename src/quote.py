from dataclasses import dataclass
import json


# Using solidity structure as a reference
# struct Quote {
#        address[] route;
#        address[] pairs;
#        uint256[] binSteps;
#        ILBRouter.Version[] versions;
#        uint128[] amounts;
#        uint128[] virtualAmountsWithoutSlippage;
#        uint128[] fees;
#    }
@dataclass
class quote:
    route: list
    pairs: list
    binSteps: list
    version: int
    amounts: list
    virtualAmountsWithoutSlippage: list
    fees: list


def convert_quote_to_json(quote: quote):
    return json.dumps(quote, default=lambda o: o.__dict__, sort_keys=True)


def convert_json_to_quote(json: str):
    return quote(**json.loads(json))
