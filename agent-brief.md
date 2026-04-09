### GET /api/vat-rates
Returns all 27 EU countries with their rates.

Response:
{
  "success": true,
  "count": 27,
  "data": { ...all countries keyed by ISO 2-letter code... }
}

### GET /api/vat-rates?country=DE
Returns a single country by ISO 2-letter code (case-insensitive).

Response:
{
  "success": true,
  "country": "DE",
  "name": "Germany",
  "rates": {
    "standard": 19,
    "reduced_1": null,
    "reduced_2": 7,
    "super_reduced": null,
    "parking": null,
    "zero": 0
  },
  "last_updated": "2026"
}

### GET /api/vat-rates?country=DE&include_notes=true
Same as above but includes the "notes" field if one exists for that country.

### GET /api/vat-rates?country=DE&category=digital_services
Returns the applicable rate for a given category. Supported categories:
- standard (default)
- digital_services → always returns the standard rate (destination principle)
- food
- books
- medicine
- transport
- accommodation

For categories, apply this logic:
- digital_services → always standard rate (EU destination principle)
- food, books, medicine, transport → return reduced_1 if exists, else reduced_2, else standard
- accommodation → return reduced_2 if exists, else reduced_1, else standard
- If no reduced rate exists for the category, fall back to standard

Response:
{
  "success": true,
  "country": "DE",
  "name": "Germany",
  "category": "digital_services",
  "rate": 19,
  "rate_type": "standard",
  "note": "Digital services are always taxed at the buyer's country standard rate under EU VAT Directive (destination principle)"
}

## Error Handling
- Invalid country code → 404 with { "success": false, "error": "Country code not found", "valid_codes": [...] }
- Invalid category → 400 with { "success": false, "error": "Invalid category", "valid_categories": [...] }
- Always return JSON, never throw unhandled errors

## Response Headers
Add these headers to all API responses:
- Content-Type: application/json
- X-Data-Version: 2026
- X-Last-Updated: 2026-04-09
- Cache-Control: public, max-age=86400

## Docs Landing Page (app/page.tsx)
Build a clean, professional API documentation page that shows:
- Title: EU VAT Rate Lookup API
- Short description
- All endpoints with example requests and responses shown in code blocks
- A table of all 27 countries with their standard rates
- A note about the digital services destination principle
- Built with Tailwind, dark theme, monospace font for code blocks

## The Data File
Place this JSON at data/eu_vat_rates_2026.json:

[PASTE THE JSON DATA BELOW]

## Notes field behaviour
- Notes are NOT included in API responses by default
- Only include notes when ?include_notes=true is passed
- This allows notes to be a premium/pro tier feature later

## Environment
- No .env needed — fully static data
- Compatible with Vercel free tier
- No rate limiting needed for local dev (add via RapidAPI gateway in production)

Data File — data/eu_vat_rates_2026.json
Paste this into data/eu_vat_rates_2026.json in your project:
json{
  "meta": {
    "version": "2026",
    "last_updated": "2026-04-09",
    "source": "European Commission VAT Directive / Fiscalead 2026",
    "notes": "Rates as of January 2026. Belgium reduced_1 increases from 6% to 12% from March 2026. Ireland reduced_1 of 9% applies to restaurants from July 2026. Always verify against official EC TEDB before production use."
  },
  "countries": {
    "AT": {
      "name": "Austria",
      "standard": 20,
      "reduced_1": 10,
      "reduced_2": 13,
      "super_reduced": null,
      "parking": 13,
      "zero": 0
    },
    "BE": {
      "name": "Belgium",
      "standard": 21,
      "reduced_1": 6,
      "reduced_2": 12,
      "super_reduced": null,
      "parking": 12,
      "zero": 0,
      "notes": "reduced_1 increases to 12% from 1 March 2026 for hotels, takeaway meals, leisure and entertainment"
    },
    "BG": {
      "name": "Bulgaria",
      "standard": 20,
      "reduced_1": null,
      "reduced_2": 9,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "CY": {
      "name": "Cyprus",
      "standard": 19,
      "reduced_1": 5,
      "reduced_2": 9,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "CZ": {
      "name": "Czech Republic",
      "standard": 21,
      "reduced_1": 12,
      "reduced_2": 0,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "0% rate on prescription medicines from 2026. Single 12% rate for restaurants and non-alcoholic beverages."
    },
    "DE": {
      "name": "Germany",
      "standard": 19,
      "reduced_1": null,
      "reduced_2": 7,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Reduced 7% rate reintroduced for restaurant and catering services from 1 January 2026"
    },
    "DK": {
      "name": "Denmark",
      "standard": 25,
      "reduced_1": null,
      "reduced_2": null,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Denmark applies only a single standard rate with no reduced rates"
    },
    "EE": {
      "name": "Estonia",
      "standard": 24,
      "reduced_1": null,
      "reduced_2": 9,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Standard rate increased from 22% to 24% in July 2025"
    },
    "GR": {
      "name": "Greece",
      "standard": 24,
      "reduced_1": 6,
      "reduced_2": 13,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "ES": {
      "name": "Spain",
      "standard": 21,
      "reduced_1": null,
      "reduced_2": 10,
      "super_reduced": 4,
      "parking": null,
      "zero": 0
    },
    "FI": {
      "name": "Finland",
      "standard": 25.5,
      "reduced_1": 10,
      "reduced_2": 13.5,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Reduced rate lowered from 14% to 13.5% in 2026"
    },
    "FR": {
      "name": "France",
      "standard": 20,
      "reduced_1": 5.5,
      "reduced_2": 10,
      "super_reduced": 2.1,
      "parking": null,
      "zero": 0,
      "notes": "Super-reduced 2.1% applies to certain medicines and press publications"
    },
    "HR": {
      "name": "Croatia",
      "standard": 25,
      "reduced_1": 5,
      "reduced_2": 13,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "HU": {
      "name": "Hungary",
      "standard": 27,
      "reduced_1": 5,
      "reduced_2": 18,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Highest standard VAT rate in the EU"
    },
    "IE": {
      "name": "Ireland",
      "standard": 23,
      "reduced_1": 9,
      "reduced_2": 13.5,
      "super_reduced": 4.8,
      "parking": 13.5,
      "zero": 0,
      "notes": "9% rate applies to restaurants from 1 July 2026. Super-reduced 4.8% applies to agriculture."
    },
    "IT": {
      "name": "Italy",
      "standard": 22,
      "reduced_1": 5,
      "reduced_2": 10,
      "super_reduced": 4,
      "parking": null,
      "zero": 0
    },
    "LT": {
      "name": "Lithuania",
      "standard": 21,
      "reduced_1": 5,
      "reduced_2": 9,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "From 1 Jan 2026: accommodation, transport, cultural events move from 9% to 12%. Books reduced from 9% to 5%."
    },
    "LU": {
      "name": "Luxembourg",
      "standard": 16,
      "reduced_1": 8,
      "reduced_2": null,
      "super_reduced": 3,
      "parking": 14,
      "zero": 0,
      "notes": "Lowest standard VAT rate in the EU"
    },
    "LV": {
      "name": "Latvia",
      "standard": 21,
      "reduced_1": 5,
      "reduced_2": 12,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "MT": {
      "name": "Malta",
      "standard": 18,
      "reduced_1": 5,
      "reduced_2": 7,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "NL": {
      "name": "Netherlands",
      "standard": 21,
      "reduced_1": 9,
      "reduced_2": null,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Accommodation services moved from 9% to 21% standard rate from 1 January 2026"
    },
    "PL": {
      "name": "Poland",
      "standard": 23,
      "reduced_1": 5,
      "reduced_2": 8,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "PT": {
      "name": "Portugal",
      "standard": 23,
      "reduced_1": 6,
      "reduced_2": 13,
      "super_reduced": null,
      "parking": 13,
      "zero": 0
    },
    "RO": {
      "name": "Romania",
      "standard": 21,
      "reduced_1": 11,
      "reduced_2": null,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Standard rate increased from 19% to 21% in August 2025. 5% and 9% brackets consolidated into single 11% reduced rate."
    },
    "SE": {
      "name": "Sweden",
      "standard": 25,
      "reduced_1": 6,
      "reduced_2": 12,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "SI": {
      "name": "Slovenia",
      "standard": 22,
      "reduced_1": 5,
      "reduced_2": 9.5,
      "super_reduced": null,
      "parking": null,
      "zero": 0
    },
    "SK": {
      "name": "Slovakia",
      "standard": 23,
      "reduced_1": 5,
      "reduced_2": 19,
      "super_reduced": null,
      "parking": null,
      "zero": 0,
      "notes": "Standard rate increased from 20% to 23% from 2026. Products high in sugar/salt taxed at 23% (exceptions: baby food, pure juices, certain dairy)."
    }
  },
  "digital_services": {
    "note": "Since 2015 EU VAT Directive, digital services are taxed at the BUYER's country rate (destination principle). The standard rate of each country applies unless a specific reduced rate exists for electronic services.",
    "applies_standard_rate": true,
    "oss_threshold_eur": 10000
  },
  "eu_rules": {
    "minimum_standard_rate": 15,
    "maximum_standard_rate": null,
    "minimum_reduced_rate": 5,
    "max_reduced_rates_per_country": 2,
    "super_reduced_allowed": true,
    "zero_rate_allowed": true,
    "directive": "Council Directive 2006/112/EC amended by EU Directive 2022/542"
  }
}
