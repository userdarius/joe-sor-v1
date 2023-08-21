import json
import requests


class Token:
    def __init__(
        self,
        tokenAddress,
        chain,
        name,
        symbol,
        decimals,
        reserve,
        priceNative,
        priceUsd,
        volume,
        pctChange,
    ):
        self.tokenAddress = tokenAddress
        self.chain = chain
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.reserve = reserve
        self.priceNative = priceNative
        self.priceUsd = priceUsd
        self.volume = volume
        self.pctChange = pctChange

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.tokenAddress == other.tokenAddress
        return False

    def __hash__(self):
        return hash(self.tokenAddress)

    def __repr__(self):
        return self.name


def get_tokens(url: any, chain: any):
    url = f"{url}/v1/tokens/{chain}"
    parameter = {"pageSize": 100}
    response = requests.get(url, params=parameter)
    if response.status_code == 200:
        token_data = json.loads(response.text)
        tokens = [Token(**token) for token in token_data]
        return tokens
    else:
        return []
