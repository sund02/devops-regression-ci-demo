# Demo speaker notes — jafarm's part (~3.5 min)

Topic: **Automated Regression Testing with CI Quality Gates.**
jafarm covers the app and the tests; gaag2 then takes the CI gates.

Total demo budget 6:30–7:30. jafarm's segment is the first ~3.5 minutes,
ending on the failing PR so gaag2 can pick up the CI story.

---

## 0. One-line setup (~15s)

"This is a FastAPI service with one endpoint, `POST /orders/total`. You send it
a cart and an optional discount code, it returns subtotal, discount, and total.
All the money logic lives in four small pure functions in `app/pricing.py`."

## 1. What the app does and what the tests pin down (~50s)

- Show `app/pricing.py`. Point at `order_total`: subtotal, then discount, then
  `total = subtotal − discount`, clamped at zero.
- "The one rule everything hangs on: **a percentage discount reduces the whole
  order total by that percentage.** `SAVE10` on a 150-krona order is 15 off, not
  10% of one item."
- Show `tests/unit/test_pricing.py` — `test_save10_reduces_multi_item_order_by_ten_percent`
  and the `SAVE20` twin. "These assert the discount is 10% / 20% of the *whole*
  subtotal for a multi-item cart. That's the behaviour we're protecting."
- Run `pytest` once: all green, and `pytest --cov=app` shows ≥ 90% on `app/`.

## 2. The regression and the rule it breaks (~50s)

- "Now a plausible-looking change." Apply the diff from `docs/regression.md`:
  `order_total` bases the discount on `items[0].price` — the first line item —
  instead of the subtotal.
- "It still 'applies a discount'. It still works for a cart with one line. But it
  no longer scales with the rest of the order, so it breaks the whole-order
  rule."
- Run `pytest`: the two multi-item unit tests fail, plus the integration
  end-to-end discount test. Three red.

## 3. Why unit and integration tests are separate (~40s)

- "The unit tests just failed in a few milliseconds — no server, no HTTP. That's
  the fast feedback loop while you're editing `pricing.py`."
- "The integration test, `test_discount_applied_end_to_end`, drives the real
  FastAPI app through the test client: request parsing, validation, the pricing
  call, JSON out. Slower, but it's the higher-confidence check that the whole
  path still works — a green unit suite with a broken serializer would still
  ship a bug."
- "Different jobs: unit tests localise *where* the logic is wrong; integration
  tests confirm the *system* still behaves."

## 4. Why the single-item test still passing matters (~35s)

- Point at `test_single_item_cart_with_save10_stays_correct` — still green.
- "A one-line cart is the single case where 'percentage off the first item' and
  'percentage off the whole order' are the same number. So a test that only ever
  checks that case passes while the feature is broken."
- "Line coverage here is still ≥ 90%. The buggy line runs in every test. Coverage
  tells you code *executed*, not that you *asserted the right thing*. That's the
  gap mutation testing closes — which is where gaag2 picks up."

## Hand-off line

"So: tests caught the regression locally in milliseconds. Next, gaag2 shows the
CI quality gate that stops this PR from ever merging."

---

## Commands used (keep visible in a scratch file)

```bash
pytest                     # green on main
# apply regression diff (docs/regression.md)
pytest                     # 3 failures
pytest tests/unit -q       # fast subset
git checkout fix/discount-bug && pytest   # green again
```
