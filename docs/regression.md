# The intentional regression

This is the bug the demo introduces on purpose to show that the tests catch it
and (later) that CI blocks the PR.

## The rule being broken

> A percentage discount reduces the **whole order total** by that percentage.

## The change

In `app/pricing.py`, `order_total` currently bases the discount on the order
**subtotal**. The regression bases it on the **first line item's unit price**
instead, so the discount stops scaling with the rest of the cart.

```diff
 def order_total(items: list[Item], code: str | None) -> dict[str, Decimal]:
     sub = subtotal(items)
-    discount = min(discount_amount(sub, code), sub)
+    base = items[0].price if items else Decimal("0")
+    discount = min(discount_amount(base, code), sub)
     total = max(sub - discount, Decimal("0"))
     return {"subtotal": sub, "discount": discount, "total": total}
```

`discount_amount` itself is untouched: it still applies the percentage to
whatever base it is handed. The bug is *which* base `order_total` passes in.

## Expected test results after applying it

Fails (>= 2):

- `tests/unit/test_pricing.py::test_save10_reduces_multi_item_order_by_ten_percent`
- `tests/unit/test_pricing.py::test_save20_reduces_multi_item_order_by_twenty_percent`
- `tests/integration/test_api.py::test_discount_applied_end_to_end`

Still passes (on purpose):

- `tests/integration/test_api.py::test_single_item_cart_with_save10_stays_correct`
- every `subtotal` / unknown-code / `None`-code / empty-cart / never-negative test

A single-line cart is the one case where "percentage off the first line" and
"percentage off the whole order" are the same number, so the narrow test keeps
passing while the real behaviour is broken. That is the coverage-is-not-
correctness point.

## Branch / PR flow

| Branch | PR | State | `pytest` on the branch |
| --- | --- | --- | --- |
| `main` | — | correct code | all pass, coverage >= 90% on `app/` |
| `regression/discount-bug` | PR #2 -> `main` | diff above applied | >= 2 fail (listed above); PR stays open, do not merge |
| `fix/discount-bug` | PR #3 -> `regression/discount-bug` | diff reverted | all pass |

PR #3 targets `regression/discount-bug`, not `main`, on purpose: that is the only
base against which it shows a real "restore the discount" diff and its checks go
red -> green. Against `main` the fix is a no-op diff and there is nothing to show.

## Apply / revert by hand

Apply: make the edit above in `app/pricing.py`.
Revert: change `discount_amount(base, code)` back to `discount_amount(sub, code)`
and drop the `base = ...` line.
