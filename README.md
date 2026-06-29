# 3DEqualizer4 R8.1 Windows UTF-8 Manual Patches

> ⚠️ **UNOFFICIAL PATCH — USE AT YOUR OWN RISK**
>
> - This is an **unofficial, community-maintained** patch. It is NOT
>   affiliated with, endorsed by, or supported by Science-D-Visions.
> - **Tested only on 3DEqualizer4 R8.1 (Windows), Chinese / GBK locale.**
>   Other versions, platforms, and locales have NOT been tested.
> - **Version-locked:** The patcher checks the running 3DE version at
>   startup. If the detected version is not R8.1, it aborts **without
>   modifying any files**. Do not force it.
> - This repository does **NOT** redistribute any proprietary 3DEqualizer
>   files. It only contains patch scripts and documentation.
> - **Always back up** your 3DEqualizer4 installation folder before applying.
> - **Run scripts inside 3DEqualizer4** (Main Window → Python → Run Script…),
>   NOT from a system terminal / standalone Python.
> - **`errors='replace'` caveat:** The patch adds `errors='replace'` to
>   `open()` calls that read script headers, preferences, logs, and
>   internal templates. This prevents crashes but **may silently replace**
>   undecodable bytes with `U+FFFD` (�). For user-data paths (e.g., the
>   Piggyback Camera calibration import), we intentionally use strict UTF-8
>   mode **without** `errors='replace'` so bad data raises a visible error.
> - See [docs/Potential_Risks.md](docs/Potential_Risks.md) for the original
>   R8.1 audit findings and patch-related safety notes.

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

| File | Role | Status |
|------|------|--------|
| `scripts/Fix_Exporters_UTF8.py` | **Main patch** — fixes Blender name collision + UTF-8 encoding in Blender, Maya, Piggyback Camera, and Flame Matchbox exporters (4 files). Uses exact-match replacement table. Run this one. | ✅ **Use this** |
| `scripts/Rollback_UTF8_Patches.py` | **Rollback** — restores all `.encoding_backup` files and moves the disabled `export_blender.py` back. | ↩ Use if needed |
| `scripts/Backup_UTF8_Patch_Targets.py` | **Backup only** — creates local `.encoding_backup` files for known patch targets before applying the patch. Does not patch, move, or delete files. | Optional preflight backup |
| `scripts/Scan_Exporters_UTF8_Status.py` | **Read-only scanner** — checks current patch status, version compatibility, Blender legacy script state, and backup files. Does not modify files. | Optional preflight / diagnosis |
| `scripts/Cleanup_UTF8_Backups.py` | **Optional cleanup** — deletes known `.encoding_backup` files after the patch has been verified and an external backup exists. Does **not** delete the disabled Blender legacy backup. | Optional, use with caution |
## Repository Layout

`UTF8_Patch_Manager.py` is the recommended launcher and is kept in the
repository root.  Run it from 3DEqualizer4's
`Main Window > Python > Run Script...` dialog.

Individual tools live in `scripts/`:

- `scripts/Fix_Exporters_UTF8.py`
- `scripts/Backup_UTF8_Patch_Targets.py`
- `scripts/Scan_Exporters_UTF8_Status.py`
- `scripts/Rollback_UTF8_Patches.py`
- `scripts/Cleanup_UTF8_Backups.py`

Detailed documentation is under `docs/`.

The old Blender-only helper script has been removed from the active
tree.  For normal use, run `UTF8_Patch_Manager.py` from the repository
root.  The Blender exporter conflict fix is included in
`scripts/Fix_Exporters_UTF8.py`.

## Tested Environment

- 3DEqualizer4 Release 8.1 (Windows)
- Windows 11 Home — Chinese locale / GBK default encoding
- Python scripts under `sys_data/py_scripts/`
- Verified: Blender exporter menu conflict, UTF-8 read-path fixes

Other 3DE versions and operating systems are **not** tested.

## Usage

> ⚠️ **These scripts MUST be run INSIDE 3DEqualizer4.**
> They import `tde4` (the 3DE4 Python API) and will **fail** with
> `ModuleNotFoundError: No module named 'tde4'` if run from a system
> terminal or standalone Python.

### Before You Apply

1. **Completely close 3DEqualizer4.**
2. **Back up your entire 3DEqualizer4 installation folder** (e.g., copy
   `C:\Program Files\3DEqualizer4` to a safe location).
3. If 3DE4 is installed under `Program Files` or another protected directory,
   you **must launch 3DEqualizer4 as Administrator** so the script can
   write to `sys_data/`.

### Applying the Patch

1. Launch 3DEqualizer4 (right-click → **Run as administrator** if needed).
2. Go to **Main Window → Python → Run Script…**
3. Select **`UTF8_Patch_Manager.py`** from the repository root.
4. From the Manager main menu, choose **Tools → Fix**.
5. Select patch scopes (default: all), confirm, then read the backup
   warning carefully.  Click **Proceed** to apply or **Cancel** to abort.
6. After the script completes and shows its report, **fully exit
   3DEqualizer4** (do NOT just use "Rescan Python Directories").
7. Restart 3DEqualizer4 normally.
8. Verify the exporter menus work:
   - **Main Window → 3DE4 → Export Project → Blender…** (dialog should appear)
   - **Main Window → 3DE4 → Export Project → Maya…** (dialog should appear)

Advanced users can run `scripts/Fix_Exporters_UTF8.py` directly.

### What NOT to Do

- ❌ Do **NOT** run `python Fix_Exporters_UTF8.py` from a terminal.
- ❌ Do **NOT** skip Step 5 — 3DE4 caches scripts at startup, and a simple
  "Rescan Python Directories" is not enough.
- ❌ Do **NOT** apply the patch while 3DE4 has unsaved project work open.

### Rollback

If something goes wrong, or you want to undo all changes:

1. Launch 3DEqualizer4 (as Administrator if needed).
2. Go to **Main Window → Python → Run Script…**
3. Select **`UTF8_Patch_Manager.py`** from the repository root.
4. Choose **Tools → More → Undo**.
5. Review the preview of files to be restored. Click **Proceed**.
6. **Fully exit** 3DEqualizer4, then restart it.

Advanced users can run `scripts/Rollback_UTF8_Patches.py` directly.

The rollback script restores all `.encoding_backup` files and moves the
disabled `export_blender.py` back to `py_scripts/`. It is **idempotent**
— safe to run multiple times.

Rollback requires `.encoding_backup` files to restore the original
exporter source files. If those backup files are missing, rollback can
still restore the disabled legacy Blender script if available, but it
cannot restore modified exporter files. In that case, restore from
your external full 3DE installation backup.

### Unsupported 3DE Version

If the script reports **"Unsupported 3DE Version"**, do not force it.

This patch uses an exact-match replacement table built for 3DEqualizer4
Release 8.1. Other versions (R8.0, R8.2, R9, etc.) may have different
script contents. Applying to a different version may corrupt your files.

If you need to undo a previous patch run on a non-R8.1 installation,
use `Rollback_UTF8_Patches.py` instead — it displays a warning but allows
you to proceed.

### Optional: Backup Patch Targets Only

If you want to create local `.encoding_backup` files before applying
the patch, run `Backup_UTF8_Patch_Targets.py` inside 3DEqualizer4
(Main Window > Python > Run Script...).

This script only copies the known patch target exporter files to
`.encoding_backup` files. It does not apply the patch, move
`export_blender.py`, or delete anything.

Use this if:

- you want an explicit backup-only step before patching;
- you only need local backups of the patch target files;
- you suspect the main patch's automatic backup may not run or
  may be skipped (e.g., if all patch points are already patched).

Do **not** run it after the files have already been patched. If a
file appears already patched, the backup script refuses to create a
`.encoding_backup`, because doing so would save patched content
instead of original content.

This is **not** a replacement for a full external backup of your
3DEqualizer4 installation folder.

### Optional: Scan Current Status

Before or after applying the patch, you can run
`Scan_Exporters_UTF8_Status.py` inside 3DEqualizer4
(Main Window > Python > Run Script...).

It is **read-only** and does not modify files. It reports:

- detected 3DE version and patch compatibility;
- whether the Blender legacy script is disabled;
- whether each exporter patch point is patched, unpatched,
  partial, or unknown;
- whether `.encoding_backup` files exist;
- a summary with recommended action.

### Optional: Cleanup Backup Files

After verifying that the patch works and after making an external full
backup of your 3DEqualizer4 installation, you may run
`Cleanup_UTF8_Backups.py` inside 3DEqualizer4 to delete known
`.encoding_backup` files.

This is **optional** and requires double confirmation.

Do **not** run it if you still want `Rollback_UTF8_Patches.py` to restore
the original exporter files from local backups.

The cleanup tool does **not** delete
`py_scripts_disabled/export_blender.py.bak`, because that file keeps the
legacy Blender exporter disabled and is needed for rollback.

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

## Validation / Smoke Test

Validated manually on:

- 3DEqualizer4 Release 8.1
- Windows 11 Home
- Chinese locale / GBK default encoding

v0.4.0 Manager smoke test (manual):

1. Run `UTF8_Patch_Manager.py` inside 3DEqualizer4
   (Main Window > Python > Run Script...).
2. Confirm main menu displays **UTF-8 Patch Manager v0.4.0**.
3. Confirm **Toolkit root: FOUND**.
4. Run **Scan** — scanner completes normally.
5. Open **Tools → Backup**, confirm requester appears, **Cancel**.
6. Open **Tools → Fix**, confirm scope selection appears, **Cancel**.
7. Open **Tools → More → Undo**, confirm rollback preview appears,
   **Cancel**.
8. Open **Tools → More → Cleanup**, confirm warning appears, **Cancel**.
9. Confirm no `script not found` / `FileNotFoundError` /
   requester title mojibake.

**Known limitation:** The patch is version-specific. The exact-match
replacement table was built against a specific 3DEqualizer4 R8.1 build.
If your local script files differ from the tested build, the patcher will
report `WARN expected pattern not found`. Stop and verify manually if
this occurs.

## Documentation

| File | Content |
|------|---------|
| `docs/Fix_README.md` | Detailed fix notes — root causes, symptoms, rollback |
| `docs/Potential_Risks.md` | Original R8.1 audit findings and patch-related safety notes |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `docs/RELEASE_NOTES_v0.4.0.md` | v0.4.0 GitHub Release notes |
| `docs/RELEASE_NOTES_v0.3.0.md` | v0.3.0 GitHub Release notes |
| `docs/RELEASE_NOTES_v0.2.0.md` | v0.2.0 GitHub Release notes |
| `docs/RELEASE_NOTES_v0.1.0.md` | v0.1.0 GitHub Release notes |

## Manager Toolkit Folder Notes

`UTF8_Patch_Manager.py` is a unified launcher (main menu: Scan |
Tools | Help | Cancel).  Run it inside 3DEqualizer4 instead of
launching each tool script individually.

### Toolkit folder name

For the manager's automatic search, keep the downloaded toolkit
folder name unchanged when possible.  Recommended folder names
include:

```text
3dequalizer-r8.1-windows-utf8-patches
3dequalizer-r8.1-windows-utf8-patches-main
Manual Patches
3de_utf8_patch_toolkit
```

Recommended placement:

```text
<3DE install path>\3dequalizer-r8.1-windows-utf8-patches\
```

or:

```text
<3DE install path>\Manual Patches\
```

Keep all toolkit files together.  Do not copy only the manager
script by itself.  The manager searches one level of subdirectories
under the 3DE install path automatically.

If automatic search still fails, edit `TOOLKIT_ROOT_OVERRIDE` at
the top of `UTF8_Patch_Manager.py` and set it to the toolkit folder.

## Development Note

This project was developed with AI-assisted coding support.
All patch logic was manually reviewed and tested on 3DEqualizer4 R8.1
under Chinese Windows locale.

## License

MIT License — applies only to the patch scripts and documentation in this
repository. It does **not** apply to any proprietary 3DEqualizer files.
