import requests_mock
from src.Pool import get_pools, Pool


def test_pool_initialization():
    pool = Pool(
        pairAddress="0x1111",
        chain="ethereum",
        name="Pool1",
        status="active",
        version="v1",
        tokenX="ETH",
        tokenY="USDT",
        reserveX=100,
        reserveY=1000,
        lbBinStep=0.01,
        lbBaseFeePct=0.1,
        lbMaxFeePct=0.5,
        activeBinId="0x2222",
        liquidityUsd=1000000,
        liquidityNative=500000,
        liquidityDepthMinus=5000,
        liquidityDepthPlus=5000,
        liquidityDepthTokenX=500,
        liquidityDepthTokenY=5000,
        volumeUsd=2000000,
        volumeNative=1000000,
        feesUsd=20000,
        feesNative=10000,
        protocolSharePct=0.5,
    )

    assert pool.pairAddress == "0x1111"
    assert pool.chain == "ethereum"
    assert pool.name == "Pool1"
    assert pool.status == "active"
    assert pool.version == "v1"
    assert pool.tokenX == "ETH"
    assert pool.tokenY == "USDT"
    assert pool.reserveX == 100
    assert pool.reserveY == 1000
    assert pool.lbBinStep == 0.01
    assert pool.lbBaseFeePct == 0.1
    assert pool.lbMaxFeePct == 0.5
    assert pool.activeBinId == "0x2222"
    assert pool.liquidityUsd == 1000000
    assert pool.liquidityNative == 500000
    assert pool.liquidityDepthMinus == 5000
    assert pool.liquidityDepthPlus == 5000
    assert pool.liquidityDepthTokenX == 500
    assert pool.liquidityDepthTokenY == 5000
    assert pool.volumeUsd == 2000000
    assert pool.volumeNative == 1000000
    assert pool.feesUsd == 20000
    assert pool.feesNative == 10000
    assert pool.protocolSharePct == 0.5


def test_get_pools_success():
    with requests_mock.Mocker() as m:
        m.get(
            "http://test.com/v1/pools/ethereum/",
            text='[{"pairAddress": "0x1111", "chain": "ethereum", "name": "Pool1", "status": "active", "version": "v1", "tokenX": "ETH", "tokenY": "USDT", "reserveX": 100, "reserveY": 1000, "lbBinStep": 0.01, "lbBaseFeePct": 0.1, "lbMaxFeePct": 0.5, "activeBinId": "0x2222", "liquidityUsd": 1000000, "liquidityNative": 500000, "liquidityDepthMinus": 5000, "liquidityDepthPlus": 5000, "liquidityDepthTokenX": 500, "liquidityDepthTokenY": 5000, "volumeUsd": 2000000, "volumeNative": 1000000, "feesUsd": 20000, "feesNative": 10000, "protocolSharePct": 0.5}]',
        )

        pools = get_pools("http://test.com", "ethereum", "v1", 10)

        assert len(pools) == 1
        assert isinstance(pools[0], Pool)
        assert pools[0].pairAddress == "0x1111"
        assert pools[0].chain == "ethereum"
        assert pools[0].name == "Pool1"
        assert pools[0].status == "active"
        assert pools[0].version == "v1"
        assert pools[0].tokenX == "ETH"
        assert pools[0].tokenY == "USDT"
        assert pools[0].reserveX == 100
        assert pools[0].reserveY == 1000
        assert pools[0].lbBinStep == 0.01
        assert pools[0].lbBaseFeePct == 0.1
        assert pools[0].lbMaxFeePct == 0.5
        assert pools[0].activeBinId == "0x2222"
        assert pools[0].liquidityUsd == 1000000
        assert pools[0].liquidityNative == 500000
        assert pools[0].liquidityDepthMinus == 5000
        assert pools[0].liquidityDepthPlus == 5000
        assert pools[0].liquidityDepthTokenX == 500
        assert pools[0].liquidityDepthTokenY == 5000
        assert pools[0].volumeUsd == 2000000
        assert pools[0].volumeNative == 1000000
        assert pools[0].feesUsd == 20000
        assert pools[0].feesNative == 10000
        assert pools[0].protocolSharePct == 0.5


def test_get_pools_failure():
    with requests_mock.Mocker() as m:
        m.get("http://test.com/v1/pools/ethereum/", status_code=500)

        pools = get_pools("http://test.com", "ethereum", "v1", 10)

        assert pools == []
