# EU VAT Rate Lookup API

## Stack
Next.js 14 (app router), TypeScript, Tailwind, Vercel. No DB, no external APIs.

## Files
```
app/api/vat-rates/route.ts       → main endpoint
lib/vat-data.ts                  → imports data/eu_vat_rates_2026.json
data/eu_vat_rates_2026.json      → provided separately, do not modify
app/page.tsx                     → docs landing page
```

## Endpoints

**GET /api/vat-rates**
Returns all 27 countries keyed by ISO code.

**GET /api/vat-rates?country=DE**
Returns single country rates. Strip `notes` field unless `?include_notes=true`.

**GET /api/vat-rates?country=DE&category=digital_services**
Returns applicable rate for category. Categories: `standard`, `digital_services`, `food`, `books`, `medicine`, `transport`, `accommodation`.

Category logic:
- `digital_services` → always `standard` rate
- `food, books, medicine, transport` → `reduced_1` ?? `reduced_2` ?? `standard`
- `accommodation` → `reduced_2` ?? `reduced_1` ?? `standard`

## Response Shape

Country lookup:
```json
{ "success": true, "country": "DE", "name": "Germany", "rates": { "standard": 19, "reduced_1": null, "reduced_2": 7, "super_reduced": null, "parking": null, "zero": 0 }, "last_updated": "2026" }
```

Category lookup:
```json
{ "success": true, "country": "DE", "category": "digital_services", "rate": 19, "rate_type": "standard" }
```

Errors: 404 for bad country, 400 for bad category. Always return JSON.

## Headers (all responses)
```
Content-Type: application/json
X-Data-Version: 2026
Cache-Control: public, max-age=86400
```

## Docs Page
Dark theme, monospace code blocks, Tailwind. Show: all endpoints with example responses, table of all 27 countries + standard rates, note on digital services destination principle.

## Notes
- Omit `notes` field by default, expose via `?include_notes=true`
- No .env needed
- No rate limiting (handled by RapidAPI gateway in prod)

## Data File
The file `data/eu_vat_rates_2026.json` is already present in the repo. Read it carefully before generating code — it is the source of truth for all VAT rates. The structure is:
- `meta` — version, last_updated, source, notes
- `countries` — object keyed by ISO 2-letter code (AT, BE, BG…), each with: name, standard, reduced_1, reduced_2, super_reduced, parking, zero, and optional notes
- `digital_services` — EU-wide rules for digital services
- `eu_rules` — directive info and rate constraints

Do not modify this file. Import it directly in `lib/vat-data.ts`.
