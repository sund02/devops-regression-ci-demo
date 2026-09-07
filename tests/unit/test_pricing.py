"""Unit tests for the pure pricing functions.

These are the fast checks: no HTTP, no app, just the functions in
:mod:`app.pricing`. They pin down one rule above all others -- *a percentage
discount reduces the whole order total by that percentage*.
"""

from decimal import Decimal

from app.pricing import Item, discount_amount, order_total, subtotal


def cart(*pairs: tuple[float, int]) -> list[Item]:
    """Build a cart from ``(price, quantity)`` pairs."""
    return [Item(price=Decimal(str(price)), quantity=qty) for price, qty in pairs]


def test_subtotal_of_multi_item_cart() -> None:
    items = cart((10.00, 2), (5.50, 1), (2.25, 4))
    assert subtotal(items) == Decimal("34.50")


def test_subtotal_accepts_decimal_prices() -> None:
    assert subtotal([Item(Decimal("2.5"), 4)]) == Decimal("10.00")


def test_item_accepts_plain_float_price() -> None:
    # JSON numbers arrive as float; Item must coerce them exactly.
    assert subtotal([Item(2.5, 4)]) == Decimal("10.00")


def test_save10_reduces_multi_item_order_by_ten_percent() -> None:
    items = cart((100.00, 1), (50.00, 1))
    result = order_total(items, "SAVE10")
    assert result["subtotal"] == Decimal("150.00")
    assert result["discount"] == Decimal("15.00")
    assert result["total"] == Decimal("135.00")
    assert result["total"] == result["subtotal"] * Decimal("0.90")


def test_save20_reduces_multi_item_order_by_twenty_percent() -> None:
    items = cart((100.00, 1), (50.00, 1), (25.00, 2))
    result = order_total(items, "SAVE20")
    assert result["subtotal"] == Decimal("200.00")
    assert result["discount"] == Decimal("40.00")
    assert result["total"] == Decimal("160.00")
    assert result["total"] == result["subtotal"] * Decimal("0.80")


def test_unknown_code_gives_zero_discount() -> None:
    items = cart((10.00, 3))
    result = order_total(items, "NOT_A_CODE")
    assert result["discount"] == Decimal("0.00")
    assert result["total"] == result["subtotal"] == Decimal("30.00")
    assert discount_amount(Decimal("30.00"), "NOT_A_CODE") == Decimal("0.00")


def test_none_code_gives_zero_discount() -> None:
    items = cart((10.00, 3))
    result = order_total(items, None)
    assert result["discount"] == Decimal("0.00")
    assert result["total"] == Decimal("30.00")
    assert discount_amount(Decimal("30.00"), None) == Decimal("0.00")


def test_empty_cart_is_all_zeros() -> None:
    result = order_total([], None)
    assert result["subtotal"] == Decimal("0.00")
    assert result["discount"] == Decimal("0.00")
    assert result["total"] == Decimal("0.00")


def test_discount_never_pushes_total_below_zero() -> None:
    for code in (None, "SAVE10", "SAVE20", "NOPE"):
        for items in (cart((0.00, 1)), cart((10.00, 1), (0.00, 5)), cart((3.33, 3))):
            result = order_total(items, code)
            assert result["total"] >= Decimal("0")
            assert result["total"] == result["subtotal"] - result["discount"]
            assert result["discount"] <= result["subtotal"]


def test_percentage_discount_rounds_half_up() -> None:
    # subtotal 0.15 -> 10% = 0.015 -> half-up -> 0.02
    assert discount_amount(Decimal("0.15"), "SAVE10") == Decimal("0.02")
