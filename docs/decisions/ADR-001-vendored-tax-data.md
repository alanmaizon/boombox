# ADR-001: Use vendored irish_tax_rules.json as sole rate source

**Status:** Accepted  
**Date:** 2025-01-01  
**Author:** Alan Maizon / Copilot

## Context

Boombox needs to apply Irish income tax rates, USC bands, PRSI rates, mileage
rates, and VAT thresholds. These values change with each Finance Act.

Options considered:
1. Hardcode rates in agent prompts or tool code
2. Vendor rates from `taxman` repo as a runtime dependency
3. Vendor rates as a local JSON file in this repo

## Decision

**Option 3 — vendored local JSON file.**

Rates live in `backend/data/irish_tax_rules.json`. All agents and tools call
`load_tax_rules()` from `backend/tools/tax_data.py`. No other code path is
permitted to contain tax rate values.

## Rationale

- **Auditability:** Every rate change is a diff in the JSON file, reviewable
  in a PR.
- **Reliability:** No runtime dependency on `taxman` or any external service.
- **Fail-loud behaviour:** `load_tax_rules` raises `FileNotFoundError` if the
  file is missing rather than silently returning a wrong rate.
- **Test coverage:** `test_tax_data.py` validates the file's structure and
  required fields on every test run.

## Consequences

- Future Finance Acts require a manual update to the JSON file and a PR.
- Multi-year support requires additional files (`irish_tax_rules_2026.json`
  etc.) — the loader handles this with fallback to the default file.
