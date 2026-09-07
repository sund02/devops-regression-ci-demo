"""FastAPI wrapper around the pure pricing logic in :mod:`app.pricing`.

Run locally with::

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel

from app.pricing import Item, order_total

app = FastAPI(title="Order Total Service")


class ItemIn(BaseModel):
    price: float
    quantity: int


class OrderIn(BaseModel):
    items: list[ItemIn]
    discount_code: str | None = None


@app.post("/orders/total")
def orders_total(order: OrderIn) -> dict[str, float]:
    """Compute an order's subtotal, discount and total.

    A body that does not match :class:`OrderIn` yields FastAPI's default 422.
    """
    items = [Item(price=Decimal(str(line.price)), quantity=line.quantity) for line in order.items]
    result = order_total(items, order.discount_code)
    return {key: float(value) for key, value in result.items()}
