# time-tracker

Stacy's Time Tracker — installable PWA, hosted on GitHub Pages (main branch, root):
https://runningtarget11.github.io/time-tracker/

- `index.html` holds all UI, CSS and JS. `sw.js` = network-first service worker. `version.json` = update feed read on startup.
- Version rule: every change bumps `APP_VERSION` (index.html) and `version.json` together, with a new entry at the top of `releases`. Bump `CACHE` in sw.js when static assets change.
- Never change localStorage keys (`tt_profile`, `tt_entries`, `tt_settings`) without a migration — users' time entries live there.
- Time is stored in minutes, always multiples of 10.
