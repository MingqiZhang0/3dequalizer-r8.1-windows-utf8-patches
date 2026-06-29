# Changelog

All notable changes to the 3DEqualizer4 R8.1 Windows UTF-8 Patches.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned

- v0.3.0: add `UTF8_Patch_Manager.py` as a single root UI entry point.
- v0.3.0: move individual tools into `scripts/` after the manager is stable.
- Future: document exact-match table maintenance and optional
  expected-count validation.

---

## [0.2.0] - 2026-06-29

### Added

- Runtime 3DEqualizer version detection via `tde4.get3DEVersion()`.
  Main patch aborts safely with an "Unsupported 3DE Version" dialog
  if the detected version is not 3DEqualizer4 Release 8.1.
- `Scan_Exporters_UTF8_Status.py` - read-only diagnostic scanner for
  patch status, version compatibility, Blender legacy script state,
  and backup file presence.
- `Backup_UTF8_Patch_Targets.py` - backup-only preflight tool for
  known UTF-8 patch target files. Refuses to back up files that
  already appear patched.
- `Cleanup_UTF8_Backups.py` - optional guarded cleanup tool for known
  `.encoding_backup` files. Requires double confirmation; does not
  delete disabled Blender legacy backups.
- Rollback now warns clearly when `.encoding_backup` files are missing
  and exporter source files cannot be restored from local backups.
- Scanner console report warns when local rollback backups are missing
  and suggests running the backup tool before patching.

### Changed

- Light repository layout cleanup:
  - runnable tools remain in repository root for easier use from
    3DEqualizer4 `Run Script...`;
  - detailed documentation moved to `docs/`;
  - legacy Blender-only helper moved to `legacy/`.
- Scanner uses compact popup summary + full console report strategy
  to avoid 3DE requester clipping.
- Scanner popup wording: `Backup files` / `Missing files`.
- Runtime report and requester text avoids non-ASCII punctuation
  where it may appear in 3DE4 UI.
- README now lists all five root runnable tools.

### Fixed

- Scanner summary logic: fully patched environments now correctly
  show `FULLY PATCHED` instead of `UNKNOWN`.
- Scanner popup shortened to avoid 3DE requester display clipping.
- Rollback wording spacing fixed (emdash replacements).
- Piggyback Camera documentation corrected to strict UTF-8 without
  `errors='replace'`.

### Safety

- Main patch aborts on non-R8.1 versions; no files are modified.
- Rollback soft-warns on non-R8.1 but allows recovery.
- Cleanup uses double confirmation before deleting any backup file.
- Backup-only tool refuses to back up already-patched files.
- Rollback clearly warns that missing `.encoding_backup` prevents
  restoring exporter source files.
- Full external 3DE installation backup remains required.

### Documentation

- `docs/Potential_Risks.md` Section 8 added: patch-related risks and
  safety notes covering `errors='replace'` tradeoffs, strict Piggyback
  UTF-8, version-locked exact-match table, backup/rollback/cleanup
  limitations, 3DE UI display strategy, admin permissions, and
  restart requirements.
- README warning block updated to reference both original audit
  findings and patch-related safety notes.
- `docs/Fix_README.md` Piggyback Camera strict UTF-8 correction.
- `docs/RELEASE_NOTES_v0.2.0.md` added.

### Tested

- Documentation-only changes were reviewed.
- Real 3DE4 R8.1 smoke tests:
  - scanner runs and reports status;
  - main patch Cancel path works;
  - backup tool Cancel path works;
  - rollback Cancel path works;
  - cleanup first-level Cancel path works.

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
- `Potential_Risks.md` - read-only audit of ~250 scripts in the 3DE4 R8.1
  `sys_data/py_scripts/` directory, cataloguing encoding, robustness, and
  metadata issues.
- `Fix_README.md` - detailed fix notes with root-cause analysis, line-level
  change tables, and rollback steps.
- `README.md` - project overview, warning block, usage instructions, and
  rollback instructions.
- `LICENSE` - MIT License (applies to patch scripts and documentation only).

### Fixed

- Blender exporter menu unresponsive (`Main Window > 3DE4 > Export Project >
  Blender...` does nothing).  Root cause: legacy `export_blender.py` (v1.3)
  and current `exportBlender.py` (v2.2) registered the same `name` + `gui`
  slot.  Fix moves the legacy script to `py_scripts_disabled/`.
- UnicodeDecodeError (`'gbk' codec can't decode byte 0x80 ...`) on Windows
  Chinese/GBK locale for the following exporter scripts:
  - `exportBlender.py` - 6 read-mode `open()` + 3 `exec(open(...).read())` calls
  - `export_maya.py` - 3 read-mode `open()` + 3 `exec(open(...).read())` calls
  - `calcMainCameraViaPiggybackCamera.py` - 1 calibration import `open()` call
  - `export_flame_LD_3DE4_batch.py` - 5 template-loading `open()` calls
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
  detected - all-SKIP runs create zero new backup files.
- Legacy Blender script is moved to `py_scripts_disabled/export_blender.py.bak`
  rather than deleted.
- `Rollback_UTF8_Patches.py` restores all `.encoding_backup` files and moves
  the disabled Blender script back.  Preview-before-execute with Cancel
  handling.  Idempotent - safe to run multiple times.
- All patch scripts require running inside 3DEqualizer4 (they import `tde4`);
  they cannot be run from a system terminal.

### Tested

- **Application:** 3DEqualizer4 Release 8.1
- **OS:** Windows 11 Home
- **Locale:** Chinese / GBK default encoding
- **Smoke test:** Real 3DE4 run - patch application and idempotent re-run
  both passed.
