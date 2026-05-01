# Data Schema — irish_tax_rules.json

## Overview

`backend/data/irish_tax_rules.json` is the single source of truth for all
Irish tax rates, bands, thresholds, and reliefs used by Boombox.

**Never hardcode tax values in agent prompts, tool code, or business logic.**
If a value isn't in this file, fail loudly.

## Top-level schema

```json
{
  "tax_year": 2025,
  "effective_date": "2025-01-01",
  "legislation": "Finance Act 2025",
  "budget": "Budget 2026",
  "source_primary": "<url>",
  "income_tax": { ... },
  "usc": { ... },
  "prsi": { ... },
  "mileage": { ... },
  "vat": { ... },
  "deadlines": { ... },
  "expense_categories": { ... },
  "earned_income_credit": { ... }
}
```

## Income Tax (`income_tax`)

| Field | Type | Description |
|---|---|---|
| `description` | string | Human-readable description |
| `source` | string | URL source |
| `statute` | string | Statute reference |
| `bands[]` | array | Progressive rate bands |
| `bands[].label` | string | Band name |
| `bands[].lower` | number | Lower bound (EUR) |
| `bands[].upper` | number\|null | Upper bound; null = unbounded |
| `bands[].rate` | number | Decimal rate (e.g. 0.20) |
| `bands[].source` | string | URL source |
| `credits` | object | Tax credits |
| `credits.personal_credit.amount` | number | Personal credit (EUR) |
| `credits.earned_income_credit.amount` | number | Earned income credit (EUR) |

## USC (`usc`)

Same band structure as income_tax. Additional fields:
- `exemption_threshold`: Income below which USC is zero (currently €13,000)
- `reduced_rate`: Reduced rate for medical card holders / 70+

## PRSI (`prsi`)

| Field | Description |
|---|---|
| `class_s.rate` | Class S rate (4%) |
| `class_s.minimum_annual` | Minimum PRSI payable (€500) |
| `class_s.source` | Citizens Information URL |

## Mileage (`mileage`)

| Field | Description |
|---|---|
| `avaso_rate_per_km` | AVASO reimbursement rate (€0.44/km) |
| `avaso_minimum_round_trip_km` | Minimum round-trip km for AVASO reimbursement (40km) |
| `rates[]` | Civil service progressive rate bands |

## VAT (`vat`)

| Field | Description |
|---|---|
| `thresholds.services.amount` | VAT registration threshold — services (€40,000) |
| `thresholds.goods.amount` | VAT registration threshold — goods (€80,000) |
| `standard_rate.rate` | 23% |
| `reduced_rate.rate` | 13.5% |

## Deadlines (`deadlines`)

| Key | Description |
|---|---|
| `form11_filing` | 31 October deadline for Form 11 via ROS |
| `preliminary_tax` | 31 October — 90% of current year or 100% of prior |
| `income_tax_balance` | Balance due 31 October |

## Updating the file

1. Source changes from Revenue.ie, Citizens Information, or the Finance Act
2. Add/update the relevant section with the new values
3. Update the `tax_year` and `effective_date` fields
4. Update `source` and `statute` references
5. Run `pytest backend/tests/test_tax_data.py` to validate
6. Commit with message: `chore(data): update irish_tax_rules.json for <year>`
