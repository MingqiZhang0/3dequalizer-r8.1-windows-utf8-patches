# v0.2.0 - Safety Toolkit and Diagnostics

## Summary

v0.2.0 turns the original patch into a safer toolkit: runtime version
guards, read-only diagnostics, backup-only preflight, guarded cleanup,
and clearer rollback warnings.

This release is still **version-locked** to:

- 3DEqualizer4 Release 8.1
- Windows
- Chinese / GBK locale test environment

It remains **unofficial** and unsupported by Science-D-Visions.

---

## What's New

### Runtime Version Guard

`Fix_Exporters_UTF8.py` now checks the running 3DE version via
`tde4.get3DEVersion()`. If the detected version is not Release 8.1,
the patcher aborts with an "Unsupported 3DE Version" dialog without
modifying any files. The exact-match patch table is built specifically
for R8.1.

### Read-only Scanner

`Scan_Exporters_UTF8_Status.py` inspects the current installation
and reports:

- detected 3DE version and patch compatibility;
- Blender legacy script status;
- patch status for every exporter entry (PATCHED / UNPATCHED / PARTIAL /
  UNKNOWN);
- `.encoding_backup` file presence;
- a summary with recommended action.

It is read-only and does not modify files. Short popup summary + full
console report.

### Backup-only Tool

`Backup_UTF8_Patch_Targets.py` creates local `.encoding_backup` files
for known patch target exporter scripts before applying the patch.
It does not patch, move, or delete anything.

It refuses to back up files that already appear patched, so that
saving patched content as "original" cannot happen.

### Guarded Cleanup Tool

`Cleanup_UTF8_Backups.py` deletes known `.encoding_backup` files with
double confirmation. Does not delete the disabled Blender legacy
backup. Optional only; do not use if you may need rollback.

### Rollback Safety Warnings

`Rollback_UTF8_Patches.py` now explicitly warns when `.encoding_backup`
files are missing and exporter source files cannot be restored from
local backups. Still offers to restore the disabled legacy Blender
script if available.

### Documentation and Risk Notes

`docs/Potential_Risks.md` now includes a full section on patch-related
risks: `errors='replace'` tradeoffs, strict UTF-8 for Piggyback
calibration data, version-locked exact-match table, backup/rollback/
cleanup limitations, 3DE UI display strategy, admin permission
requirements, and restart requirements.

---

## Recommended Workflow

```text
Scan -> Backup -> Fix -> Scan
```

Use rollback only if needed.

Use cleanup only after verifying the patch works and after making an
external full backup.

---

## Included Tools

| Tool | Purpose |
|------|---------|
| `Fix_Exporters_UTF8.py` | Apply the patch |
| `Backup_UTF8_Patch_Targets.py` | Create local `.encoding_backup` files before patching |
| `Scan_Exporters_UTF8_Status.py` | Read-only status scanner |
| `Rollback_UTF8_Patches.py` | Restore from local backups when available |
| `Cleanup_UTF8_Backups.py` | Optional cleanup of known `.encoding_backup` files |
| `legacy/Fix_Blender_Export.py` | Legacy Blender-only helper, kept for reference |

---

## Upgrade Notes from v0.1.0

- Existing v0.1.0 users do not need to reapply the patch if scanner
  reports `FULLY PATCHED`.
- Run `Scan_Exporters_UTF8_Status.py` to inspect current state.
- If local `.encoding_backup` files are missing, rollback cannot
  restore exporter source files.
- Use external full installation backup for complete recovery.

---

## Limitations

- Does not support R8.0 / R8.2 / R9.
- Does not support macOS / Linux.
- Does not redistribute original 3DE files.
- Does not patch all remaining encoding risks listed in
  `docs/Potential_Risks.md`.
- Does not replace a full external installation backup.

---

## Legal / License Note

MIT License -- applies to the patch scripts and documentation in this
repository. It does **not** apply to any proprietary 3DEqualizer files
or the 3DEqualizer4 application itself.
