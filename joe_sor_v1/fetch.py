import requests

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"

AVAX_USDC_20BP = "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1"


# Testing the get


def get(url: str, params=None):
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception("Request failed")
    return response.json()


def get_bins(pair_address: str, id: int, radius: int):
    url = f"{BARN_URL}/v1/bin/{CHAIN}/{pair_address.lower()}/{id}"
    parameter = {"radius": radius}
    return get(url, parameter)


def get_pools(address: str):
    url = f"{BARN_URL}/v1/pools/{CHAIN}/{address}"
    return get(url)


def list_pools(version: any):
    url = f"{BARN_URL}/v1/pools/{CHAIN}"
    parameter = {"version": version}
    return get(url, parameter)


def get_bin_reserveX(pair_address: str, id: int, radius: int):
    url = f"{BARN_URL}/v1/bin/{CHAIN}/{pair_address.lower()}/{id}"
    parameter = {"radius": radius}
    return get(url, parameter)


def get_tokens():
    url = f"{BARN_URL}/v1/tokens/{CHAIN}"
    parameter = {"pageSize": 100}
    return get(url, parameter)


print(get_tokens())
# print(get_bin_reserveX(AVAX_USDC_20BP, 8376042, 10))
# print(get_bins(AVAX_USDC_20BP, 8376042, 10))
# print(list_pools("v2.0"))
