# 3DEqualizer4 R8.1 Windows UTF-8 Manual Patches

Manual compatibility patches for 3DEqualizer4 R8.1 exporters on Chinese Windows locale.

## Overview

This repository addresses two issues with 3DEqualizer4 R8.1 on Chinese Windows
(where the system default encoding is GBK / cp936):

1. **Blender exporter menu does nothing** —
   `Main Window > 3DE4 > Export Project > Blender...` produces no response.
   Root cause: the legacy `export_blender.py` (v1.3) and the current
   `exportBlender.py` (v2.2) both declare the same `name` + `gui` menu slot,
   creating an ambiguous script index.  The patch moves the legacy script
   out of `py_scripts/`.

2. **UnicodeDecodeError on Chinese Windows** —
   Python's default `open()` encoding on Chinese Windows is `cp936` (GBK).
   Several R8.1 exporter scripts read UTF-8 files (their own headers,
   preferences files, XML templates) without an explicit `encoding=` argument.
   When these files contain characters outside the GBK code page,
   `UnicodeDecodeError: 'gbk' codec can't decode byte …` is raised.
   The patch adds `encoding='utf-8', errors='replace'` to high-risk
   read-mode `open()` and `exec(open(…).read())` calls.

## Included Patches

| Patch | Purpose |
|-------|---------|
| `Fix_Blender_Export.py` | Moves `export_blender.py` out of `py_scripts/` and adds UTF-8 encoding to `exportBlender.py` read calls. |
| `Fix_Exporters_UTF8.py` | Adds explicit UTF-8 encoding to read-mode `open()` / `exec(open(…).read())` in 4 exporter scripts. |

## Tested Environment

- 3DEqualizer4 Release 8.1 (Windows)
- Windows 11 Home — Chinese locale / GBK default encoding
- Python scripts under `sys_data/py_scripts/`
- Verified: Blender exporter menu conflict, UTF-8 read-path fixes

Other 3DE versions and operating systems are **not** tested.

## Usage

1. **Close 3DEqualizer4 completely.**
2. Back up your 3DEqualizer4 installation folder.
3. Run the desired patch script with Python 3:
   ```bash
   python Fix_Blender_Export.py
   python Fix_Exporters_UTF8.py
   ```
4. When prompted, select or input your 3DEqualizer4 installation directory.
5. Restart 3DEqualizer4.
6. Verify:
   - `Main Window > 3DE4 > Export Project > Blender...`
   - `Main Window > 3DE4 > Export Project > Maya...`

If the installation directory is in a protected location (e.g. `Program Files`),
run the terminal as Administrator so the script can write to `sys_data/`.

## Affected Local Files

These files in the user's **local** 3DEqualizer4 installation are modified:

| File | Change |
|------|--------|
| `sys_data/py_scripts/exportBlender.py` | `encoding='utf-8'` added to read opens |
| `sys_data/py_scripts/export_maya.py` | `encoding='utf-8'` added to read opens + `exec(open(…))` rewritten |
| `sys_data/py_scripts/calcMainCameraViaPiggybackCamera.py` | `encoding='utf-8'` added to 1 read open |
| `sys_data/py_scripts/export_flame_LD_3DE4_batch.py` | `encoding='utf-8'` added to 5 read opens |
| `sys_data/py_scripts/export_blender.py` | Moved to `sys_data/py_scripts_disabled/export_blender.py.bak` |

Original files are backed up with a `.encoding_backup` suffix before modification.

## Important Notice

- This repository **does not** contain or redistribute any original 3DEqualizer
  files. It only contains patch scripts and documentation.
- The patch scripts **modify only your local** 3DEqualizer4 installation.
- **Back up** your 3DEqualizer4 installation before applying any patch.
- Tested on **3DEqualizer4 R8.1** under **Chinese Windows locale** only.
- **Use at your own risk.**

## Documentation

| File | Content |
|------|---------|
| `Fix_README.md` | Detailed fix notes — root causes, symptoms, rollback |
| `Potential_Risks.md` | Audit findings — ~200 items catalogued, not yet patched |

## Development Note

This project was developed with AI-assisted coding support.
All patch logic was manually reviewed and tested on 3DEqualizer4 R8.1
under Chinese Windows locale.

## License

MIT License — applies only to the patch scripts and documentation in this
repository. It does **not** apply to any proprietary 3DEqualizer files.
