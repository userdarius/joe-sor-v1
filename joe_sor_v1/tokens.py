import requests
import json


BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"


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


def get_tokens():
    url = f"{BARN_URL}/v1/tokens/{CHAIN}"
    parameter = {"pageSize": 100}
    response = requests.get(url, params=parameter)
    if response.status_code == 200:
        token_data = json.loads(response.text)
        tokens = [Token(**token) for token in token_data]
        return tokens
    else:
        return []


tokens = get_tokens()
for token in tokens:
    print(token.name)  # Or manipulate token properties however you want
