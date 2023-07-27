import pytest
from src.main import getV2Quote  


def test_getV2Quote_swapForY_true():
    amount = 100
    activeId = 1
    binStep = 10
    swapForY = True
    expected_quote = ...  
    actual_quote = getV2Quote(amount, activeId, binStep, swapForY)
    assert expected_quote == actual_quote


def test_getV2Quote_swapForY_false():
    amount = 100
    activeId = 1
    binStep = 10
    swapForY = False
    expected_quote = ...  
    actual_quote = getV2Quote(amount, activeId, binStep, swapForY)
    assert expected_quote == actual_quote
