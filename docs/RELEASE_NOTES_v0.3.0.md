# v0.3.0 - Manager Launcher and Patch Scope Selection

## Summary

v0.3.0 adds a root-level manager launcher and optional patch scope
selection.

Users can now run `UTF8_Patch_Manager.py` inside 3DEqualizer4 and
launch scan, backup, fix, rollback, cleanup, and help from one entry
point.

The patcher also supports selecting which patch scopes to apply.

This release remains **version-locked** to:

- 3DEqualizer4 Release 8.1
- Windows
- Chinese / GBK locale test environment

It remains **unofficial** and unsupported by Science-D-Visions.

---

## What's New

### Manager Launcher

`UTF8_Patch_Manager.py` is a root-level launcher for the toolkit.

It can launch:

- Scan status
- Backup targets
- Apply patch
- Rollback patch (Undo)
- Cleanup backups
- Help / safety notes

The manager does not duplicate patch logic and does not bypass each
tool's own confirmation dialogs.

### Automatic Toolkit Root Search

The manager now searches common toolkit locations, including the
3DE install path and one-level subfolders such as:

```text
Manual Patches
3de_utf8_patch_toolkit
3dequalizer-r8.1-windows-utf8-patches
3dequalizer-r8.1-windows-utf8-patches-main
```

If automatic search fails, users can set `TOOLKIT_ROOT_OVERRIDE` at
the top of `UTF8_Patch_Manager.py`.

### Patch Scope Selection

`Fix_Exporters_UTF8.py` now supports optional patch scope selection.

Available scopes:

| Scope | Target |
|-------|--------|
| Blender exporter UTF-8 | `exportBlender.py` |
| Maya exporter UTF-8 | `export_maya.py` |
| Piggyback Camera UTF-8 | `calcMainCameraViaPiggybackCamera.py` |
| Flame LD batch UTF-8 | `export_flame_LD_3DE4_batch.py` |
| Blender legacy menu fix | `export_blender.py` menu collision |

Unchecked scopes are not modified and do not create backups.

### UI Polish

- Tools menu shortened to avoid narrow requester clipping.
- Help text shortened.
- Root resolved message prints only once per manager script run.

---

## Recommended Toolkit Placement

Keep the downloaded toolkit folder name unchanged when possible.

Recommended placements:

```text
<3DE install path>\3dequalizer-r8.1-windows-utf8-patches\
<3DE install path>\3dequalizer-r8.1-windows-utf8-patches-main\
<3DE install path>\Manual Patches\
<3DE install path>\3de_utf8_patch_toolkit\
```

Keep all toolkit files together. Do not copy only
`UTF8_Patch_Manager.py` by itself.

---

## Recommended Workflow

```text
Run UTF8_Patch_Manager.py
Scan -> Backup -> Fix -> Scan
```

Use rollback only if needed.

Use cleanup only after verifying the patch works and after making
an external full backup.

---

## Tested

Real 3DEqualizer4 R8.1 UI / launcher tests passed:

- manager auto-resolved toolkit root at
  `F:\3DEqualizer4 R8.1\3DEqualizer4\Manual Patches`;
- manager root logging printed only once after logging fix;
- Tools requester buttons displayed without manual resizing;
- Manager -> Scan launched successfully;
- Manager -> Backup launched successfully and refused to back up
  already-patched files;
- Manager -> Fix opened scope selection successfully;
- scope selection dialogs, final summary, and Cancel path behaved
  normally.

## Not Tested

- Actual partial-write behavior on an unpatched 3DE4 R8.1 test copy
  was not performed for this release.
- No macOS / Linux testing.
- No R8.0 / R8.2 / R9 testing.

---

## Limitations

- Does not support R8.0 / R8.2 / R9.
- Does not support macOS / Linux.
- Does not redistribute original 3DE files.
- Does not replace a full external installation backup.
- Rollback requires local `.encoding_backup` files or external
  backups.

---

## Upgrade Notes from v0.2.0

- Existing v0.2.0 users do not need to reapply the patch if scanner
  reports `FULLY PATCHED`.
- Use `UTF8_Patch_Manager.py` as the recommended entry point.
- Advanced users can still run standalone tools directly.
- Use scope selection if only selected patch groups should be
  applied.

---

## Legal

MIT License -- applies to the patch scripts and documentation only.
