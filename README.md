# devops-regression-ci-demo

A tiny FastAPI "order total" service used to demo automated regression testing with CI quality gates (KTH DevOps course).

## Install

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Test

```bash
pytest                 # unit + integration
pytest --cov=app       # with line coverage on app/
```

## Run

```bash
uvicorn app.main:app --reload
# POST /orders/total  {"items": [{"price": 100.0, "quantity": 1}], "discount_code": "SAVE10"}
```

## Layout

| Path | What |
| --- | --- |
| `app/pricing.py` | Pure pricing functions (subtotal, discount, order total). |
| `app/main.py` | FastAPI app exposing `POST /orders/total`. |
| `tests/unit/` | Fast checks on the pure functions. |
| `tests/integration/` | End-to-end checks through the HTTP app. |
| `docs/regression.md` | The intentional regression used in the demo. |
| `docs/demo-script.md` | Speaker notes. |

## Proposal

Course proposal PR: https://github.com/KTH/devops-course/pull/2964
