import json


def convert_quote_to_dict(quote: dict):
    return json.dumps(quote, sort_keys=True)


def convert_dict_to_quote(quote: str):
    return json.loads(quote)


quote_dict = {
    "route": [],
    "pairs": [],
    "binSteps": [],
    "version": 1,
    "amounts": [],
    "virtualAmountsWithoutSlippage": [],
    "fees": [],
}

quote_json = convert_quote_to_dict(quote_dict)
print(quote_json)

quote_dict_again = convert_dict_to_quote(quote_json)
print(quote_dict_again)
