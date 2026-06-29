# v0.5.0 - Partial patch recovery

## Summary

v0.5.0 improves reliability when a previous patch run left exporter
files in a partial state.  The fixer now uses `expected_count` metadata
and count-based classification to detect and repair partial patches.

---

## Highlights

### Partial patch recovery

The fixer now counts occurrences of patched and original patterns:

- **Fully patched** — skip.
- **Partial and repairable** — continue patching remaining original
  patterns to reach the expected count.
- **Partial but not repairable** — warn and do not write (original
  patterns are missing; manual review needed).
- **Unpatched** — patch normally.
- **Unknown variant** — warn for manual review.

### Flame expected-count cleanup

Three identical Flame LD batch XML template entries were merged into
one `expected_count=3` entry.  Fully patched reports now show a
single `already patched (3/3)` line instead of three `(3/1)` lines.

---

## What Changed

`scripts/Fix_Exporters_UTF8.py`:

- Every patch-table entry now carries `expected_count` (1 or 3).
- `apply_patch_table()` replaced the binary `already_patched in
  content` check with count-based A/B/C/D/E classification.
- Flame XML template `open(path,"r")` entries merged from three
  `expected_count=1` entries to one `expected_count=3` entry.

`scripts/Scan_Exporters_UTF8_Status.py`:

- Flame XML template status entries merged identically.
- Scanner and Fixer expected-count definitions are consistent.

---

## Validation

- `python -m py_compile` on all scripts.
- Static partial-patch logic self-test (7/7 PASS).
- Real 3DE4 R8.1 fully patched Manager Fix test pending.
- Real 3DE4 R8.1 partial repairable scenario test pending.

---

## Recommended Workflow

```text
UTF8_Patch_Manager.py -> Tools -> Fix -> All Scopes -> Proceed
```

If the scanner reports `PARTIAL`, the fixer can complete remaining
occurrences when original patterns are still present.

If the fixer reports `partial patch detected but original pattern
not found`, stop and verify manually.

---

## Limitations

- This is an unofficial patch toolkit.
- Tested only on 3DEqualizer4 Release 8.1 Windows Chinese/GBK locale.
- Run `UTF8_Patch_Manager.py` inside 3DEqualizer4.
- Does not redistribute proprietary 3DEqualizer files.
- Back up your 3DE installation before use.
- Use at your own risk.
- Partial repairable real-environment test is pending.

---

## Legal

MIT License — applies to the patch scripts and documentation only.
