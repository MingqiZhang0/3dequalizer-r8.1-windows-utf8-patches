# Changelog

All notable changes to the 3DEqualizer4 R8.1 Windows UTF-8 Patches.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.0] - 2026-06-29

### Added

- Initial unofficial 3DEqualizer4 R8.1 Windows Chinese/GBK UTF-8 manual patch
  scripts.
- `Fix_Exporters_UTF8.py` as the main patch entry point.  Handles Blender
  menu name collision + UTF-8 encoding fixes for Blender, Maya, Piggyback
  Camera, and Flame Matchbox exporters.
- `Rollback_UTF8_Patches.py` for safe, preview-before-execute rollback of
  all patch changes.
- `Fix_Blender_Export.py` legacy Blender-only helper (superseded by the
  main script; kept for reference).
- `Potential_Risks.md` — read-only audit of ~250 scripts in the 3DE4 R8.1
  `sys_data/py_scripts/` directory, cataloguing encoding, robustness, and
  metadata issues.
- `Fix_README.md` — detailed fix notes with root-cause analysis, line-level
  change tables, and rollback steps.
- `README.md` — project overview, warning block, usage instructions, and
  rollback instructions.
- `LICENSE` — MIT License (applies to patch scripts and documentation only).

### Fixed

- Blender exporter menu unresponsive (`Main Window > 3DE4 > Export Project >
  Blender...` does nothing).  Root cause: legacy `export_blender.py` (v1.3)
  and current `exportBlender.py` (v2.2) registered the same `name` + `gui`
  slot.  Fix moves the legacy script to `py_scripts_disabled/`.
- UnicodeDecodeError (`'gbk' codec can't decode byte 0x80 ...`) on Windows
  Chinese/GBK locale for the following exporter scripts:
  - `exportBlender.py` — 6 read-mode `open()` + 3 `exec(open(...).read())` calls
  - `export_maya.py` — 3 read-mode `open()` + 3 `exec(open(...).read())` calls
  - `calcMainCameraViaPiggybackCamera.py` — 1 calibration import `open()` call
  - `export_flame_LD_3DE4_batch.py` — 5 template-loading `open()` calls
- Replaced regex-based `re.sub()` / `re.compile()` patching with an
  exact-match replacement table built from a live 3DE4 R8.1 file scan.
- Patches are now idempotent: re-running the script reports `SKIP already
  patched` for every entry instead of silently re-applying or breaking.
- Confirmation dialog (`tde4.postQuestionRequester`) return value is now
  checked; clicking Cancel aborts before any file modification.
- Non-ASCII characters removed from all `tde4` requester titles, button
  labels, and log messages to prevent mojibake on Windows/3DE4 UI.
- Piggyback Camera user-data path (`importCalibration`) now uses strict
  UTF-8 (`encoding='utf-8'` **without** `errors='replace'`) so bad input
  data raises a visible error rather than silently corrupting content.

### Safety

- Modified files are backed up with a `.encoding_backup` suffix before the
  first write.  Backup creation is deferred until an actual change is
  detected — all-SKIP runs create zero new backup files.
- Legacy Blender script is moved to `py_scripts_disabled/export_blender.py.bak`
  rather than deleted.
- `Rollback_UTF8_Patches.py` restores all `.encoding_backup` files and moves
  the disabled Blender script back.  Preview-before-execute with Cancel
  handling.  Idempotent — safe to run multiple times.
- All patch scripts require running inside 3DEqualizer4 (they import `tde4`);
  they cannot be run from a system terminal.

### Tested

- **Application:** 3DEqualizer4 Release 8.1
- **OS:** Windows 11 Home
- **Locale:** Chinese / GBK default encoding
- **Smoke test:** Real 3DE4 run — patch application and idempotent re-run
  both passed.

---

## [Unreleased] — planned for v0.2.0

### Added
- Runtime 3DEqualizer version detection via `tde4.get3DEVersion()`.
- Main patch (`Fix_Exporters_UTF8.py`) aborts safely with an
  "Unsupported 3DE Version" dialog if the detected version is not
  3DEqualizer4 Release 8.1. No files are modified.
- Rollback script (`Rollback_UTF8_Patches.py`) displays the detected
  version and shows a warning on non-R8.1 environments, but still
  allows the user to proceed (for undoing a previous patch run).
- Confirmation dialog now shows the detected 3DE version and
  supported status.
- `Scan_Exporters_UTF8_Status.py` — a read-only diagnostic scanner
  for patch status, version compatibility, Blender legacy script
  state, and backup file presence.
- `Cleanup_UTF8_Backups.py` — an optional guarded cleanup tool for
  known `.encoding_backup` files.  Requires double confirmation;
  does not delete disabled Blender legacy backups.
- Scanner wording updated from "Backups found" to "Backup files found".

### Planned
- Directory restructuring (`scripts/`, `legacy/`, `docs/`).
- `errors='replace'` risk documentation in `Potential_Risks.md`.
- Exact-match table documented in `Fix_README.md`.
- Expected-count validation for each `PATCH_TABLE` entry.
