import requests
import json


class Route:
    def __init__(self, part, amount, pairs):
        self.part = part
        self.amount = amount
        self.pairs = pairs


class Routes:
    def __init__(self, tokens, routes):
        self.tokens = tokens
        self.routes = routes


#class Pair:
#    def __init__(self, tokenX, tokenY):
#        self.tokenX = tokenX
#        self.tokenY = tokenY

