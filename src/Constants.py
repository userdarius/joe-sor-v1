class Constants:
    SCALE_OFFSET = 128

    SCALE = 1 << SCALE_OFFSET

    PRECISION = 10**18
    SQUARED_PRECISION = PRECISION * PRECISION

    MAX_FEE = 0.1 * 10**18  # 10%
    MAX_PROTOCOL_SHARE = 2500  # 25% of the fee

    BASIS_POINT_MAX = 10000
    REAL_ID_SHIFT = 1 << 23
