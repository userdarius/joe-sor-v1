class Route:
    def __init__(self, part, amount, pairs):
        self.part = part
        self.amount = amount
        self.pairs = pairs


class Routes:
    def __init__(self, tokens, routes):
        self.tokens = tokens
        self.routes = routes


class Pair:
    def __init__(
        self,
        tokenY,
        version,
        bin_step,
        activeId,
    ):
        self.tokenY = tokenY
        self.version = version
        self.bin_step = bin_step
        self.activeId = activeId
