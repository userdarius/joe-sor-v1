import requests
import json


class Bin:
    def __init__(
        self,
        binId,
        priceXY,
        priceYX,
        reserveX,
        reserveY,
        reserveXRaw,
        reserveYRaw,
        totalSupply,
        volumeX,
        volumeY,
        volumeUsd,
        volumeNative,
        feesUsd,
        feesNative,
    ):
        self.binId = binId
        self.priceXY = priceXY
        self.priceYX = priceYX
        self.reserveX = reserveX
        self.reserveY = reserveY
        self.reserveXRaw = reserveXRaw
        self.reserveYRaw = reserveYRaw
        self.totalSupply = totalSupply
        self.volumeX = volumeX
        self.volumeY = volumeY
        self.volumeUsd = volumeUsd
        self.volumeNative = volumeNative
        self.feesUsd = feesUsd
        self.feesNative = feesNative


# review
def get_bin(url: any, chain: any, pair_address: any, radius: int, bin_id: any):
    url = f"{url}/v1/bin/{chain}/{pair_address}/{bin_id}"
    radius = {"radius": radius}
    response = requests.get(url, params=radius)
    if response.status_code == 200:
        bin_data = json.loads(response.text)
        bins = [Bin(**bin) for bin in bin_data]
        return bins
    else:
        return []
