# v0.4.0 - Manager-first Repository Layout

## Summary

v0.4.0 restructures the repository around `UTF8_Patch_Manager.py` as
the single recommended entry point.  Individual tool scripts are moved
into `scripts/` and the legacy Blender-only helper has been removed.

---

## What's New

### Manager-first layout

- `UTF8_Patch_Manager.py` remains at the repository root.
- All five tool scripts moved into `scripts/`:
  - `scripts/Fix_Exporters_UTF8.py`
  - `scripts/Backup_UTF8_Patch_Targets.py`
  - `scripts/Scan_Exporters_UTF8_Status.py`
  - `scripts/Rollback_UTF8_Patches.py`
  - `scripts/Cleanup_UTF8_Backups.py`
- The manager automatically resolves tools from the new layout.

### Legacy helper removed

- `legacy/Fix_Blender_Export.py` has been removed from the active tree.
- The Blender exporter conflict fix is already included in
  `scripts/Fix_Exporters_UTF8.py`.

### Old flat layout no longer supported

- Tools are no longer found in the repository root.
- `is_toolkit_root()` now requires the manager at root and tools in
  `scripts/`.

---

## Upgrade Notes from v0.3.0

- If your toolkit is checked out from Git, `git pull` to get the new
  layout.
- If you manually downloaded files, re-download the repository and
  replace the old flat layout.
- Run `UTF8_Patch_Manager.py` as the entry point.  The manager resolves
  tools from the new `scripts/` layout automatically.

---

## Tested

- Real 3DEqualizer4 R8.1 Manager smoke test passed on Windows
  Chinese/GBK locale: manager launches, finds toolkit root in new
  layout, and starts all five tools from `scripts/`.

---

## Limitations

- Does not support R8.0 / R8.2 / R9.
- Does not support macOS / Linux.
- Does not redistribute original 3DE files.
- Manual 3DE Manager smoke test passed on 3DEqualizer4 Release 8.1
  Windows Chinese/GBK environment.

---

## Legal

MIT License -- applies to the patch scripts and documentation only.
