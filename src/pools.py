import requests
import json

BARN_URL = "https://barn.traderjoexyz.com"
CHAIN = "avalanche"


class Pool:
    def __init__(
        self,
        pairAddress,
        chain,
        name,
        status,
        version,
        tokenX,
        tokenY,
        reserveX,
        reserveY,
        lbBinStep,
        lbBaseFeePct,
        lbMaxFeePct,
        liquidityUsd,
        liquidityNative,
        liquidityDepthMinus,
        liquidityDepthPlus,
        liquidityDepthTokenX,
        liquidityDepthTokenY,
        volumeUsd,
        volumeNative,
        feesUsd,
        feesNative,
        protocolSharePct,
    ):
        self.pairAddress = pairAddress
        self.chain = chain
        self.name = name
        self.status = status
        self.version = version
        self.tokenX = tokenX
        self.tokenY = tokenY
        self.reserveX = reserveX
        self.reserveY = reserveY
        self.lbBinStep = lbBinStep
        self.lbBaseFeePct = lbBaseFeePct
        self.lbMaxFeePct = lbMaxFeePct
        self.liquidityUsd = liquidityUsd
        self.liquidityNative = liquidityNative
        self.liquidityDepthMinus = liquidityDepthMinus
        self.liquidityDepthPlus = liquidityDepthPlus
        self.liquidityDepthTokenX = liquidityDepthTokenX
        self.liquidityDepthTokenY = liquidityDepthTokenY
        self.volumeUsd = volumeUsd
        self.volumeNative = volumeNative
        self.feesUsd = feesUsd
        self.feesNative = feesNative
        self.protocolSharePct = protocolSharePct


def get_pools(version: any, size: int):
    url = f"{BARN_URL}/v1/pools/{CHAIN}/"
    parameter = {"version": version, "pageSize": size}
    response = requests.get(url, parameter)
    if response.status_code == 200:
        pool_data = json.loads(response.text)
        pools = [Pool(**pool) for pool in pool_data]
        return pools
    else:
        return []


poolsv2 = get_pools("v2.0", 100)
for pool in poolsv2:
    print(pool.name)  # Or manipulate token properties however you want
poolsv21 = get_pools("v2.1", 100)
for pool in poolsv21:
    print(pool.name)  # Or manipulate token properties however you want
