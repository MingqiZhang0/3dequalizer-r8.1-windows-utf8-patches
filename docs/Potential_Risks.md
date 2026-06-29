# Potential Risks — 3DEqualizer4 R8.1 Read-Only Audit

> **Status**: Audited. No official scripts modified. Recorded for future evaluation.

---

## 1. Script Registration Metadata Issues

### 1.1 Hidden Script Name Collision — `imgw_types`

| File | Name | Version | Hidden |
|------|------|---------|--------|
| `sdv_imgw_gui_image_formats.py` | `imgw_types` | v1.0.1 | true |
| `sdv_imgw_types.py` | `imgw_types` | v1.2.2 | true |

Two hidden library modules register the same `name`, potentially causing shadowing
in the internal script index. Both are referenced by `sdv_image_warp_gui.py`.

### 1.2 Missing Version Tag (9 scripts)

| File | Name |
|------|------|
| `hide_all_points_in_set.py` | Hide All Points in Set... |
| `import_ref_cam_footage.py` | Import Reference Camera Footage... |
| `next_selected_point.py` | Select Next Point |
| `prev_selected_point.py` | Select Previous Point |
| `reset_playback_range.py` | Reset Playback Range... |
| `set_next_camera.py` | Set Next Camera |
| `set_next_enabled_camera.py` | Set Next Enabled Camera |
| `set_next_sequence_camera.py` | Set Next Sequence Camera |
| `show_all_points_in_set.py` | Show All Points in Set... |

Impact: 3DE4's version comparison / upgrade logic may not handle these scripts correctly.

### 1.3 Empty Version String (9 scripts)

| File | Name |
|------|------|
| `deformTrack.py` | Deform Track |
| `deformTrack_autoExtend.py` | Auto Extend |
| `deformTrack_bufferCurve.py` | Buffer Track |
| `deformTrack_buttons.py` | (no name tag) |
| `deformTrack_importKeyframes.py` | Import Keys |
| `deformTrack_removeKey.py` | Remove Key |
| `deformTrack_restoreCurve.py` | Restore Track |
| `deformTrack_setKey.py` | Create Key |
| `insertTrack.py` | Insert Track |

All deformTrack-series scripts are affected.

### 1.4 `deformTrack_buttons.py` — Missing `name` Tag but Has `gui.button`

This file has no `3DE4.script.name` or `hide` tag, yet registers a GUI button:
`Manual Tracking Controls::Deform Track`. It depends on `tde4dtr.py` being loaded
by the host application.

---

## 2. Encoding & Locale Risks

### 2.1 Read-mode `open()` Without `encoding=` (~27 remaining)

The following non-exporter scripts are still at risk of `UnicodeDecodeError`
on Windows with Chinese (GBK) locale:

| File | Approx. Line(s) | Context |
|------|-----------------|---------|
| `ht_xml_functions.py` | 59, 103 | Reads own script header for version/name |
| `ht_xml_merge.py` | 53 | Same as above |
| `import_2d_curves.py` | 38 | Reads imported file |
| `import3alityMetadata.py` | 46 | Reads metadata file |
| `import_csv_files.py` | 18, 77 | Reads CSV |
| `import_kuper.py` | 41 | Reads Kuper file |
| `import_lens.py` | 46 | Reads lens file |
| `import_lidar_scan.py` | 72 | Reads LiDAR scan |
| `import_matrix.py` | 24 | Reads matrix file |
| `import_survey_txt.py` | 34 | Reads survey file |
| `import_tracks.py` | 45 | Reads tracking data |
| `import_zlcf.py` | 182 | Reads ZLCF file |
| `lens_conversion.py` | 55, 89 | Reads lens specifications |
| `optimize_curves_cv_by_cv.py` | 369 | Reads optimization chunk file |
| `python_editor.py` | 533, 854, 828 | Reads / executes Python files |
| `tde4PythonGUIEditor.py` | 721, 724 | Same as above |
| `ImportFootageFromMovieFile.py` | 594 | Reads temporary file |
| `ScriptDB_Installer.py` | 364 | Reads script database |

### 2.2 Write-mode `open()` Without `encoding=` (~71 occurrences)

Writing files on a GBK-locale system may silently produce garbled output
when the data contains non-ASCII characters (e.g., Chinese paths, usernames,
project names).

Affects virtually all `export_*.py`, `import_*.py`, `mhp_connector.py`,
`python_editor.py`, `sdv_image_warp_gui.py`, and others.

### 2.3 Hardcoded Windows Path Separators

| File | Approx. Line | Code |
|------|-------------|------|
| `exportBlender.py` | ~1770 | `'%s\\Blender Foundation\\blender\\'` |
| `export_maya.py` | ~2109 | `'%s\\Documents\\maya\\'` |

On macOS/Linux these fall back to `homedir` — no crash, but the path is incorrect.

---

## 3. Python Robustness Issues

### 3.1 Bare `except:` Without Exception Type (~60+ occurrences)

Silently swallows all exceptions, including `KeyboardInterrupt`, `SystemExit`,
and `MemoryError`.

**Highest-density files:**

| Rank | File | Bare excepts | `except: pass` |
|------|------|-------------|-----------------|
| 1 | `calcMainCameraViaPiggybackCamera.py` (158 KB) | 35+ | 3 |
| 2 | `tde4_objects.py` (194 KB) | 25+ | 1 |
| 3 | `ImportFootageFromMovieFile.py` (54 KB) | 8+ | 4 |
| 4 | `mhp_connector.py` (110 KB) | 10+ | 0 |

### 3.2 `except: pass` — Completely Silent Error Suppression (17 occurrences)

| File | Line | Scenario |
|------|------|----------|
| `calcMainCameraViaPiggybackCamera.py` | 1429 | testpointList access failure during calibration loop |
| `calcMainCameraViaPiggybackCamera.py` | 2760 | 3D camera icon rendering failure |
| `adjust_plane_constraint.py` | 49 | Global object deletion failure |
| `convert_to_stereo.py` | 44, 60 | Stereo conversion initialization failure |
| `ImportFootageFromMovieFile.py` | 768, 789, 1133 | 3D viz / slider update / session detection failure |
| `import_usd_class.py` | 461 | USD import error |
| `lnscon_lens_conversion.py` | 281, 438 | 3D area build / update failure |
| `python_editor.py` | 844 | Definition parsing failure |
| `select_constr_points.py` | 30, 45 | Constraint point query failure |
| `tde4_widget_tk.py` | 201, 206 | Widget callback cleanup failure |
| `tde4_objects.py` | 4195 | `setCurveKeySelectionFlag` failure |

---

## 4. Missing None Checks

### 4.1 `getCurrentCamera()` Return Value Not Checked for None

The following large scripts pass `getCurrentCamera()` results directly to
subsequent functions without a None check, risking a crash when no camera
is active:

| File | Affected Lines |
|------|---------------|
| `calcMainCameraViaPiggybackCamera.py` | 773, 801, 3078, 3153 |
| `calc_pgroup_lsf.py` | 600, 817 |
| `rotomation_editor.py` | 25, 673, 711, 828, 874, 922 |
| `export_2d_tracks_ae.py` | 69 |

Most smaller scripts also lack this check.

### 4.2 `getCameraLens()` Return Value Not Checked for None

Virtually all callers pass the result directly to `getLensFBackWidth()` and
similar functions without checking for None.

**Positive examples (correctly checked):** `set_fov.py:94`, `lnscon_lens_conversion.py:1411`

---

## 5. Division-by-Zero Risks

| File | Line(s) | Condition |
|------|---------|-----------|
| `export_maya.py` | 598 | Empty project → `total = 0` |
| `export_maya.py` | 1672 | Point position exactly `(0,0,0)` |
| `exportBlender.py` | 1723, 3180 | Empty point list |
| `exportBlender.py` | 2259, 3345 | Camera FPS = 0 |
| `exportBlender.py` | 2285 | `fback_w = 0` (malformed lens) |
| `rotomation_editor.py` | 900–902 | Ray direction component = 0 |
| `calcMainCameraViaPiggybackCamera.py` | 1756 | `subFrameStep = 0` |
| `calcMainCameraViaPiggybackCamera.py` | 2427 | `avgDist = 0` while `n > 0` |
| `tde4_widget_tk.py` | 788, 1201, 1226, 1249 | `num_cols / total / columns = 0` |
| `lnscon_lens_conversion.py` | 428, 429 | `xd / yd = 0` (degenerate lens) |
| `adjust_plane_constraint.py` | 211, 337 | `scale = 0` |

---

## 6. Mutable Default Arguments

| File | Line | Signature |
|------|------|-----------|
| `mhp_connector.py` | 356 | `def gen_addr(self, const_addr_list, i=0, a=[])` |
| `lnscon_browse_lenses.py` | 219 | `def post_requester_browse_lenses(ids_lens_to_skip=[])` |

The list accumulates data across repeated calls, causing unexpected behavior.

---

## 7. Debug Artifacts

| File | Pattern |
|------|---------|
| `adjust_plane_constraint.py:44` | `open("/dev/tty","w")` — Unix-only debug output |
| `flatten_lens_rotation.py:38` | Same as above |
| `lnscon_lens_conversion.py:199` | Same as above |
| `sdv_image_warp_gui.py:111` | `open("CON","w")` — Windows-only debug output |
| `sdv_image_warp_gui.py:115` | `open("/dev/tty","w")` |
| `sdv_image_warp_gui.py:869` | `open("/tmp/out.xml","w")` — hardcoded path |
| `sdv_image_warp_gui.py:3431` | `open("/tmp/warp.il","w")` — hardcoded path |

---

## Risk Level Summary

| Level | Category | Count | Recommendation |
|-------|----------|-------|----------------|
| 🔴 High | Read `open()` without UTF-8 (non-exporter scripts) | ~27 sites | Fix on-demand if users report garbled import/export |
| 🔴 High | Write `open()` without UTF-8 | ~71 sites | May garble CJK characters; fix on-demand |
| 🟠 Medium | Bare `except:` / `except: pass` | ~77 sites | Improve only when debugging specific issues |
| 🟠 Medium | Missing None checks | Widespread | Crash risk when no camera/lens is active — edge case |
| 🟡 Low | Division-by-zero | ~15 sites | Extremely rare edge conditions |
| 🟡 Low | Mutable default arguments | 2 sites | Only triggered in specific re-entrant scenarios |
| 🔵 Info | Debug artifacts | ~7 sites | Harmless but not clean |
| 🔵 Info | Script metadata gaps | ~18 scripts | No functional impact |

---

---

## 8. Patch-related Risks and Safety Notes

This section documents risks introduced by the patch tools themselves,
not by the original 3DE4 R8.1 scripts.

The sections below assume the reader is familiar with the tools listed
in the repository README.

---

### 8.1 `errors='replace'` tradeoff

Most read-mode `open()` fixes in this patch use:

```python
encoding='utf-8', errors='replace'
```

**Benefit:** Prevents `UnicodeDecodeError` on Windows with Chinese / GBK
locale when a UTF-8 file is read without an explicit encoding.

**Risk:** Invalid byte sequences that cannot be decoded as UTF-8 are
silently replaced with the Unicode replacement character `U+FFFD`.
This is a crash-prevention tradeoff, not a perfect decoding strategy.

**Where it is used:** Script header reads (`getScriptVersion`),
preferences file reads, log file reads, and internal XML/template reads
(Flame Matchbox). For these low-risk paths, silent replacement is
generally preferable to a crash that blocks the exporter GUI.

**Where it is NOT used:** See section 8.2.

---

### 8.2 Piggyback Camera exception: strict UTF-8

`calcMainCameraViaPiggybackCamera.py` line 1134 (`importCalibration`)
reads **user-supplied calibration data**.

The patch applies **strict UTF-8** without `errors='replace'`:

```python
open(path,"r", encoding='utf-8')
```

**Reason:** If a user calibration file contains invalid bytes, silently
replacing them could corrupt the calibration result without the user
noticing. A visible `UnicodeDecodeError` is safer than silent data
corruption.

If your calibration files are not valid UTF-8, you will see an error
instead of silently wrong results. This is intentional.

---

### 8.3 Exact-match table is version-locked

`Fix_Exporters_UTF8.py` uses an exact-match replacement table built
from a live scan of 3DEqualizer4 Release 8.1 script files.

- If the official exporter scripts differ in R8.0, R8.2, R9, or other
  platforms, the expected patterns may not match.
- The main patch performs a runtime version check via
  `tde4.get3DEVersion()` and aborts with "Unsupported 3DE Version" if
  the detected version is not Release 8.1.
- Do not bypass the version guard. Applying the patch to a different
  version may silently skip entries (WARN) or, in the worst case,
  produce syntactically incorrect replacements.

The read-only `Scan_Exporters_UTF8_Status.py` scanner does **not**
enforce the version guard and can be run on any version for diagnosis.

---

### 8.4 Backup and rollback limitations

- `Fix_Exporters_UTF8.py` creates `.encoding_backup` files only when
  it actually writes to a target file. An all-SKIP run (files already
  patched) creates no new backups.
- If `.encoding_backup` files are missing, `Rollback_UTF8_Patches.py`
  **cannot** restore the original exporter source files.
- Rollback may still restore the disabled legacy Blender script
  (`py_scripts_disabled/export_blender.py.bak`) if it exists.
- The only reliable recovery method remains a full external backup of
  the 3DEqualizer4 installation directory made before applying any
  patch.

Recommended safe workflow:

```text
Scan -> Backup -> Fix -> Scan
```

Or, at minimum:

```text
Backup -> Fix -> Scan
```

Running `Backup_UTF8_Patch_Targets.py` before `Fix_Exporters_UTF8.py`
ensures local `.encoding_backup` files exist regardless of whether the
main patch's deferred backup logic triggers.

---

### 8.5 Backup-only script limitations

`Backup_UTF8_Patch_Targets.py` is a preflight tool.

- It only creates `.encoding_backup` for four known target files.
- It refuses to back up a file that already contains `encoding='utf-8'`
  or `encoding="utf-8"`, because saving patched content as "original"
  would make rollback meaningless.
- It is **not** a replacement for a full external backup of the
  3DEqualizer4 installation folder.
- Running it **after** applying the patch provides no benefit and will
  produce warnings.

---

### 8.6 Cleanup tool limitations

`Cleanup_UTF8_Backups.py` deletes known `.encoding_backup` files.

- After cleanup, `Rollback_UTF8_Patches.py` cannot restore exporter
  source files from local backups.
- Cleanup is optional and requires double confirmation.
- Cleanup does **not** delete `py_scripts_disabled/export_blender.py.bak`
  or `py_scripts/export_blender.py.bak`.
- If you may need to roll back, do not run cleanup.

---

### 8.7 Requester / UI display limitations

3DEqualizer4's `tde4.postQuestionRequester()` dialog has limited
display capacity for long text and may render certain Unicode
characters incorrectly (mojibake).

All tools in this repository use the following strategy:

- **Popup:** short summary only (max ~12-14 lines, ASCII text).
- **Full report:** printed to the 3DE Python console via `print()`.

Users should check the 3DE Script Editor output for complete details.
Do not rely on the popup alone for diagnostic information.

Custom requesters (`tde4.createCustomRequester`,
`tde4.addTextAreaWidget`) were tested and found to display text content
unreliably in 3DE4 R8.1. They are not used.

---

### 8.8 Administrator permission and Program Files

If 3DEqualizer4 is installed under `C:\Program Files\` or another
protected directory:

- Writing to `sys_data/py_scripts/` requires administrator privileges.
- Launch 3DEqualizer4 as Administrator before running any tool that
  modifies files (`Fix`, `Rollback`, `Backup`, `Cleanup`).
- The read-only `Scan_Exporters_UTF8_Status.py` scanner does not
  require write access and can generally run without elevation.
- Permission failures during patch, rollback, backup, or cleanup may
  leave the installation in an inconsistent state.

---

### 8.9 Restart requirement

3DEqualizer4 caches Python scripts at startup.

After applying the patch or performing a rollback:

- **Fully exit** 3DEqualizer4.
- Restart 3DEqualizer4 normally.
- "Rescan Python Directories" is **not** sufficient.

Do not apply the patch or perform a rollback while 3DEqualizer4 has
unsaved project work open.

---

### 8.10 Risk summary table

| Area | Risk | Mitigation |
|------|------|------------|
| `errors='replace'` | Invalid bytes silently replaced | Used only for low-risk header/prefs/log/template reads |
| User calibration data | Silent replacement could corrupt data | Piggyback import uses strict UTF-8, no `errors='replace'` |
| Version mismatch | Exact-match table may not match other 3DE versions | Main patch aborts unless R8.1 is detected |
| Missing backups | Rollback cannot restore exporter source files | Keep external full installation backup |
| Backup after patch | Would save patched content as original | `Backup_UTF8_Patch_Targets.py` refuses to back up patched files |
| Cleanup | Deletes local rollback backups | Optional only, double confirmation, does not delete Blender backup |
| 3DE requester UI | Long text may be clipped; Unicode may render incorrectly | Short popup + full console report |
| Admin permissions | Write to `Program Files` may fail | Run 3DE as Administrator |
| Restart | 3DE caches scripts at startup | Full exit and restart after patch/rollback |

---

## Audit Date

2026-06-29
