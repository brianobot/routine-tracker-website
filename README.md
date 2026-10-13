# Routine

Self-contained, single-file HTML trackers for personal goals — each one a standalone plan/checklist you open directly in a browser, with progress saved locally so it persists across visits.

## Files

- **`nuclear-mphil-study-plan.html`** — 4-month study plan for Nuclear MPhil prep: all 16 math/masters courses in sequence, Nov 2026–Mar 2027, with per-course checkboxes.
- **`bits-to-reactors-plan.html`** — "Bits to Reactors" roadmap/tracker (companion plan to the above, same style of checklist-driven page).
- **`cambridge-scholarship-plan.html`** — Cambridge Scholarship application countdown and checklist.
- **`cambridge-scholarship-server.py`** — tiny stdlib-only local server for the scholarship plan. Serves the HTML plus a small JSON API so checkbox/note state is saved to `cambridge-scholarship-data.json` on disk instead of one browser's local storage, letting any device on the same LAN (e.g. your phone) see the same live progress. The HTML also works fine opened directly, single-device, without the server.
- **`cambridge-scholarship-data.json`** — the server's saved state (checked items + notes). Generated/updated by the server; not meant to be hand-edited.

## Usage

Just open an `.html` file in a browser. For the Cambridge scholarship plan, optionally run:

```
python3 cambridge-scholarship-server.py
```

and use the printed network URL to keep progress in sync across devices.
