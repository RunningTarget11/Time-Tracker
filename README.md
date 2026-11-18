# Stacy's Time Tracker

Installable Android web app (PWA) for a daily time card that totals by pay period.

**Live:** https://runningtarget11.github.io/time-tracker/
On Android, open the link in Chrome → ⋮ menu → **Install app**.

## Features
- Opens on today's date (read from the phone); arrows move between days
- Profile: shift length (stays until changed), extra-hours category, pay-period start day (default 19th), rates, budget codes, employee info
- 10-minute increments everywhere; time over the shift goes to **Extra hours** (OT 1.5 or 2.0)
- Explanation required when extra hours are entered (flagged on the timesheet)
- Timesheet view matching the paper form: Reg / OT 1.5 / OT 2.0 / Uniform Hourly / Sick-Hol-Misc / Explanation, totals, Hours × Rate = $
- Print/PDF laid out like the paper TIME SHEET, CSV export, backup/restore
- Settings → Updates: version check on startup + manual check, release notes

## Releasing an update
1. Make the change in `index.html`.
2. Bump `APP_VERSION` in `index.html` **and** `version` in `version.json`, and add a release entry with notes at the top of `releases`.
3. Bump `CACHE` in `sw.js` if cached assets (images, manifest) changed.
4. Commit and push to `main`. GitHub Pages publishes within a minute or two; installed apps see the update next time they open.

Data lives in the phone's browser storage (localStorage) and is untouched by updates.
