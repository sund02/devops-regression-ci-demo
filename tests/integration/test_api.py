"""Integration tests: the FastAPI app end to end via the test client.

Slower and broader than the unit tests -- they exercise request parsing,
validation, the pricing call and JSON serialisation together.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post_order(items: list[tuple[float, int]], discount_code: str | None = None) -> httpx.Response:
    body: dict = {"items": [{"price": price, "quantity": qty} for price, qty in items]}
    if discount_code is not None:
        body["discount_code"] = discount_code
    return client.post("/orders/total", json=body)


def test_happy_path_multi_item_no_code() -> None:
    resp = post_order([(19.99, 2), (5.00, 1)])
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtotal"] == 44.98
    assert data["discount"] == 0
    assert data["total"] == 44.98


def test_discount_applied_end_to_end() -> None:
    resp = post_order([(100.00, 1), (50.00, 1)], discount_code="SAVE10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtotal"] == 150.0
    assert data["total"] == 135.0
    assert data["total"] == pytest.approx(data["subtotal"] * 0.9)


def test_single_item_cart_with_save10_stays_correct() -> None:
    # Must KEEP passing after the regression: a one-line cart is the one case
    # where "discount off the first line" and "discount off the whole order"
    # give the same answer.
    resp = post_order([(100.00, 1)], discount_code="SAVE10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtotal"] == 100.0
    assert data["discount"] == 10.0
    assert data["total"] == 90.0


def test_malformed_body_returns_422() -> None:
    resp = client.post("/orders/total", json={"items": "not-a-list"})
    assert resp.status_code == 422
