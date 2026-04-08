# Task: Build a Cron Expression Parser API

## Endpoint
POST /api/parse-cron

## Request
{ "expression": "0 23 * * *" }

## Success Response
{
  "valid": true,
  "expression": "0 23 * * *",
  "description": "Every day at 11:00 PM",
  "next_runs": [
    "2026-04-09T23:00:00.000Z",
    "2026-04-10T23:00:00.000Z",
    "2026-04-11T23:00:00.000Z",
    "2026-04-12T23:00:00.000Z",
    "2026-04-13T23:00:00.000Z"
  ],
  "schedule": {
    "minute": "0",
    "hour": "23",
    "day_of_month": "*",
    "month": "*",
    "day_of_week": "*"
  },
  "timezone": "UTC"
}

## Error Response
{ "valid": false, "expression": "99 25 * * *", "error": "Hour value 25 is out of range (0-23)" }

## Implementation Rules
- No external npm packages — implement the parser from scratch using plain JS
- Calculate next_runs using plain JavaScript Date objects, no date libraries
- Always return exactly 5 next run times
- Support standard 5-field cron format only: minute hour day-of-month month day-of-week
- Support these field formats: wildcard (*), single value (5), range (1-5), step (*/5 or 1-5/2), list (1,2,3)

## Validation Rules
- Minute: 0-59
- Hour: 0-23
- Day of month: 1-31
- Month: 1-12
- Day of week: 0-6 (0 = Sunday)
- Reject expressions with fewer or more than 5 fields
- Reject out of range values
- Reject malformed step or range syntax

## Human Readable Descriptions
- "* * * * *"   → "Every minute"
- "0 * * * *"   → "Every hour"
- "0 9 * * *"   → "Every day at 9:00 AM"
- "0 9 * * 1"   → "Every Monday at 9:00 AM"
- "0 9 1 * *"   → "At 9:00 AM on the 1st of every month"
- "*/15 * * * *" → "Every 15 minutes"
- "0 9 * * 1-5" → "Every weekday at 9:00 AM"
- "0 0 1 1 *"   → "At midnight on January 1st"

## Tests to Write
Write a Jest test file at __tests__/parse-cron.test.ts covering:
- Valid standard expressions (* * * * *, 0 9 * * *, 0 9 * * 1)
- Steps (*/15 * * * *, 0 */2 * * *)
- Ranges (0 9 * * 1-5)
- Lists (0 9 * * 1,3,5)
- next_runs always returns exactly 5 future dates
- next_runs are all in the future relative to now
- next_runs are in ascending order
- Invalid: too few fields ("* * * *")
- Invalid: too many fields ("* * * * * *")
- Invalid: out of range minute ("60 * * * *")
- Invalid: out of range hour ("* 25 * * *")
- Invalid: out of range day ("* * 32 * *")
- Invalid: out of range month ("* * * 13 *")
- Invalid: out of range dow ("* * * * 7")
- Invalid: bad range syntax ("* * * * 1-")
- Invalid: bad step syntax ("* * * * */")
- Invalid: empty string
- Invalid: non-numeric values ("abc * * * *")

## Definition of Done
- All Jest tests pass
- No external dependencies added to package.json
- API returns correct HTTP status codes (200 for valid, 400 for invalid)
- Code is TypeScript with proper types throughout
