import requests
import json
from Token import Token


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
        activeBinId,
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
        self.tokenX = Token(
            tokenAddress=tokenX["address"],
            chain=chain,
            name=tokenX["name"],
            symbol=tokenX["symbol"],
            decimals=tokenX["decimals"],
            reserve=reserveX,
            priceNative=tokenX["priceNative"],
            priceUsd=tokenX["priceUsd"],
            volume=volumeUsd,
            pctChange=None,
        )
        self.tokenY = Token(
            tokenAddress=tokenY["address"],
            chain=chain,
            name=tokenY["name"],
            symbol=tokenY["symbol"],
            decimals=tokenY["decimals"],
            reserve=reserveY,
            priceNative=tokenY["priceNative"],
            priceUsd=tokenY["priceUsd"],
            volume=volumeUsd,
            pctChange=None,
        )
        self.reserveX = reserveX
        self.reserveY = reserveY
        self.lbBinStep = lbBinStep
        self.lbBaseFeePct = lbBaseFeePct
        self.lbMaxFeePct = lbMaxFeePct
        self.activeBinId = activeBinId
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

def get_pools(url: any, chain: any, version: any, size: int):
    page = 1
    all_pools = []

    while True:
        url_with_page = f"{url}/v1/pools/{chain}/"
        parameters = {
            "version": version,
            "pageSize": size,
            "excludeLowVolumePools": True,
            "pageNum": page
        }

        response = requests.get(url_with_page, parameters)
        if response.status_code == 200:
            pool_data = json.loads(response.text)
            
            # Check if the size of returned pools is less than 100 to break the loop
            if len(pool_data) < 100:
                all_pools.extend([Pool(**pool) for pool in pool_data])
                break

            all_pools.extend([Pool(**pool) for pool in pool_data])
            page += 1  # increment the page number
        else:
            break  # If there's an error, exit the loop

    return all_pools

def get_pools_old(url: any, chain: any, version: any, size: int):
    url = f"{url}/v1/pools/{chain}/"
    parameter = {"version": version, "pageSize": size, "excludeLowVolumePools": False}
    response = requests.get(url, parameter)
    if response.status_code == 200:
        pool_data = json.loads(response.text)
        pools = [Pool(**pool) for pool in pool_data]
        return pools
    else:
        return []
    
def get_all_pools(url: any, chain: any, version: any):
    url = f"{url}/v1/pools/{chain}/"
    parameter = {"version": version}
    response = requests.get(url, parameter)
    if response.status_code == 200:
        pool_data = json.loads(response.text)
        pools = [Pool(**pool) for pool in pool_data]
        return pools
    else:
        return []


def get_pool(url: any, chain: any, address: any, version: any) -> Pool:
    url = f"{url}/v1/pools/{chain}/{address}"
    parameter = {"version": version}
    response = requests.get(url, parameter)
    if response.status_code == 200:
        pool_data = json.loads(response.text)
        pool = Pool(**pool_data)
        return pool
    else:
        return []
