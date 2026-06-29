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

## Audit Date

2026-06-29
