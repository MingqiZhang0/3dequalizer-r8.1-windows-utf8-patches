# 3DEqualizer4 R8.1 Windows UTF-8 Patch Toolkit

Unofficial UTF-8 compatibility and exporter menu patch toolkit for
3DEqualizer4 Release 8.1 on Chinese Windows / GBK locale.

---

## What this fixes

Two confirmed issues in 3DEqualizer4 Release 8.1 on Chinese Windows:

1. **Blender exporter menu does nothing.**
   Legacy `export_blender.py` (v1.3) and current `exportBlender.py` (v2.2)
   register the same menu entry, creating an ambiguous script index.
   The patch moves the legacy script out of `py_scripts/`.

2. **UnicodeDecodeError on Chinese Windows.**
   Python's default `open()` encoding is `cp936` (GBK) on Chinese Windows.
   Several R8.1 exporter scripts read UTF-8 files without an explicit
   `encoding=` argument, causing `'gbk' codec can't decode byte ...`.
   The patch adds explicit UTF-8 encoding to those read paths.

See `docs/Fix_README.md` for detailed root-cause analysis.

---

## Supported environment

Tested on:

- 3DEqualizer4 Release 8.1
- Windows 11
- Chinese / GBK locale
- 3DE scripts under `sys_data/py_scripts/`

Not tested or supported:

- 3DEqualizer4 R8.0, R8.2, R9
- macOS or Linux
- Arbitrarily modified exporter scripts

The patcher checks the running 3DE version at startup and aborts on
unsupported versions.  Do not force it.

---

## Quick start

Normal users should run only one file inside 3DEqualizer4:

**`UTF8_Patch_Manager.py`**

1. Close 3DEqualizer4.
2. Back up your entire 3DEqualizer4 installation folder.
3. Launch 3DEqualizer4 as Administrator if it is installed under
   `Program Files`.
4. Go to **Main Window → Python → Run Script…**
5. Select `UTF8_Patch_Manager.py` from this repository root.
6. Recommended order: **Scan → Backup → Fix → Scan**.
7. Fully restart 3DEqualizer4 after applying Fix.

Do **not** run these scripts with system Python.  They import `tde4`
(the 3DE4 Python API) and will fail with `ModuleNotFoundError` from
a terminal.

---

## Important warnings

- This is an **unofficial** community toolkit.  It is not affiliated
  with, endorsed by, or supported by Science-D-Visions.
- This repository does **not** contain or redistribute proprietary
  3DEqualizer files.
- Always back up your 3DEqualizer4 installation before applying
  patches.
- Run the toolkit inside 3DEqualizer4, not from a system terminal.
- Use at your own risk.

Most patched read paths use `encoding='utf-8', errors='replace'` to
avoid crashes on Chinese Windows.  This may replace undecodable bytes
with `U+FFFD`.  User-data imports such as Piggyback Camera calibration
remain strict UTF-8 so invalid data raises a visible error.  See
`docs/Potential_Risks.md` for details.

---

## Tools

| File | Role | Normal user? |
|------|------|-------------|
| `UTF8_Patch_Manager.py` | Main launcher: Scan, Backup, Fix, Rollback, Cleanup | **Yes, use this** |
| `scripts/Scan_Exporters_UTF8_Status.py` | Read-only status scanner | Advanced / manual |
| `scripts/Backup_UTF8_Patch_Targets.py` | Backup known patch targets only | Advanced / manual |
| `scripts/Fix_Exporters_UTF8.py` | Applies exact-match patch table | Advanced / manual |
| `scripts/Rollback_UTF8_Patches.py` | Restores `.encoding_backup` files and Blender legacy script | Advanced / manual |
| `scripts/Cleanup_UTF8_Backups.py` | Deletes local `.encoding_backup` files after verification | Advanced / manual |

For normal use, run `UTF8_Patch_Manager.py`.  Individual scripts are
kept for advanced and manual workflows.

---

## Repository layout

```text
.
├── UTF8_Patch_Manager.py
├── README.md
├── CHANGELOG.md
├── LICENSE
├── docs/
│   ├── Fix_README.md
│   ├── Potential_Risks.md
│   ├── RELEASE_NOTES_v0.5.0.md
│   └── ...
└── scripts/
    ├── Fix_Exporters_UTF8.py
    ├── Backup_UTF8_Patch_Targets.py
    ├── Scan_Exporters_UTF8_Status.py
    ├── Rollback_UTF8_Patches.py
    └── Cleanup_UTF8_Backups.py
```

The old Blender-only helper script has been removed.  The Blender
exporter conflict fix is included in `scripts/Fix_Exporters_UTF8.py`.

---

## What gets changed locally

| Local 3DE file | Change |
|------|--------|
| `sys_data/py_scripts/exportBlender.py` | Adds explicit UTF-8 handling to selected read paths |
| `sys_data/py_scripts/export_maya.py` | Adds explicit UTF-8 handling to preference/log reads and self-exec `with open(script_path)` calls |
| `sys_data/py_scripts/calcMainCameraViaPiggybackCamera.py` | Adds strict UTF-8 handling to calibration file import (no `errors='replace'`) |
| `sys_data/py_scripts/export_flame_LD_3DE4_batch.py` | Adds explicit UTF-8 handling to XML/template/fingerprint reads |
| `sys_data/py_scripts/export_blender.py` | Moved to `sys_data/py_scripts_disabled/export_blender.py.bak` |

Original modified files are backed up with `.encoding_backup` before
the first actual write.

---

## Rollback

Run:

**`UTF8_Patch_Manager.py → Tools → More → Undo`**

1. Launch 3DEqualizer4 as Administrator if needed.
2. Run `UTF8_Patch_Manager.py`.
3. Choose **Tools → More → Undo**.
4. Review the preview.
5. Click **Proceed** only if you want to restore backups.
6. Fully restart 3DEqualizer4.

Rollback requires `.encoding_backup` files to restore original
exporter source files.  If those backups are missing, restore from
your external full 3DE installation backup.  Rollback also restores
the disabled Blender legacy script if available.

---

## Partial patch recovery

Starting with v0.5.0, Fix uses expected-count validation for each
patch point.

If Scanner reports `PARTIAL`, run:

**`UTF8_Patch_Manager.py → Tools → Fix`**

If original unpatched patterns are still present, Fix can complete
the remaining occurrences.

Real R8.1 test passed for a Maya self-exec state:

```text
patched_count = 1
original_count = 2
expected_count = 3
```

Fix repaired it to `(3/3)`, and Scanner then reported `FULLY PATCHED`.

If Fix reports `partial patch detected but original pattern not
found`, stop and inspect manually.  The local file may differ from
the tested R8.1 source or may have been manually edited.

---

## Validation

Validated manually on:

- 3DEqualizer4 Release 8.1
- Windows 11 Home
- Chinese / GBK default locale

v0.5.0 real 3DE Manager tests passed:

- Manager starts and shows `UTF-8 Patch Manager v0.5.0`.
- Scanner reports `Compatibility: SUPPORTED`.
- Scanner reports `Patch status: FULLY PATCHED`.
- Scanner reports `Patch points: 13/13 patched`.
- Scanner reports `Issues: 0`.
- Flame LD batch XML template reports a single `(3/3)` entry.
- Maya partial repairable state `patched 1/3, original 2` was
  repaired to `(3/3)`.
- No requester title mojibake was observed.
- `python -m py_compile UTF8_Patch_Manager.py scripts/*.py` passed.

**Known limitation:** The exact-match replacement table is
version-specific.  If your local R8.1 script files differ from the
tested build, the patcher may report `WARN expected pattern not
found` or `partial patch detected but original pattern not found`.
Stop and verify manually.

---

## Manager toolkit folder notes

Keep all toolkit files together.  Do not copy only
`UTF8_Patch_Manager.py` by itself.

Recommended folder names (auto-detected by the manager):

```text
3dequalizer-r8.1-windows-utf8-patches
3dequalizer-r8.1-windows-utf8-patches-main
Manual Patches
3de_utf8_patch_toolkit
```

Recommended placement:

```text
<3DE install path>\3dequalizer-r8.1-windows-utf8-patches\
<3DE install path>\Manual Patches\
```

If automatic search fails, edit `TOOLKIT_ROOT_OVERRIDE` at the top
of `UTF8_Patch_Manager.py` and set it to the toolkit folder.

---

## Documentation

| File | Content |
|------|---------|
| `docs/Fix_README.md` | Detailed root cause and patch notes |
| `docs/Potential_Risks.md` | Original R8.1 audit findings and safety notes |
| `CHANGELOG.md` | Version history |
| `docs/RELEASE_NOTES_v0.5.0.md` | v0.5.0 release notes |
| `docs/RELEASE_NOTES_v0.4.0.md` | v0.4.0 release notes |
| `docs/RELEASE_NOTES_v0.3.0.md` | v0.3.0 release notes |

---

## Development note

This project was developed with AI-assisted coding support.  All
patch logic was manually reviewed and tested on 3DEqualizer4 R8.1
under Chinese Windows / GBK locale.

---

## License

MIT License — applies only to the patch scripts and documentation in
this repository.  It does **not** apply to any proprietary
3DEqualizer files.
