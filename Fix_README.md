# Fix: 3DE4 R8.1 — Windows Chinese Locale Exporter Fixes

## Affected Version

3DEqualizer4 R8.1 (Windows, Chinese / GBK locale)

## Symptoms

1. `Main Window > 3DE4 > Export Project > Blender...` — clicking does nothing, no dialog appears
2. `Main Window > 3DE4 > Export Project > Maya...` — potential `UnicodeDecodeError` on re-exec
3. `calcMainCameraViaPiggybackCamera` — potential `UnicodeDecodeError` importing calibration files
4. `Export Distortion as Flame Matchbox Node` — potential `UnicodeDecodeError` reading templates

Underlying error (when triggered):
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x80
```

## Root Causes

### Issue 1: Script Name Collision (Blender only)

Two files registered the exact same menu entry in `py_scripts/`:

| File | Version | Size |
|---|---|---|
| `export_blender.py` | v1.3 | ~10 KB |
| `exportBlender.py` | v2.2 | ~168 KB |

Both declared `name: Blender...` + `gui: Main Window::3DE4::Export Project`. This is the **only** GUI-
visible name collision across all 250+ scripts. The internal menu index became ambiguous.

### Issue 2: Missing UTF-8 Encoding (multiple exporters)

On Windows with Chinese locale, Python's default `open()` encoding is `cp936` (GBK).
When scripts read UTF-8 files (self-referencing for version headers, preferences files, XML
templates, etc.) without explicit `encoding='utf-8'`, a `UnicodeDecodeError` occurs.

Affected files in the `sys_data/py_scripts/` directory.

---

## Fixes Applied — Summary

### Phase 1 — Blender (2026-06-29)

| File | Action |
|---|---|
| `export_blender.py` | Moved to `../py_scripts_disabled/` (eliminates name collision) |
| `exportBlender.py` | Added `encoding='utf-8', errors='replace'` to 6 read-mode `open()` calls and 3 `exec(open(...).read())` calls |

### Phase 2 — Maya + PiggybackCam + Flame (2026-06-29)

| File | Action |
|---|---|
| `export_maya.py` | Added `encoding='utf-8', errors='replace'` to 3 `exec(open(script_path).read())` calls and 3 read-mode `open()` calls |
| `calcMainCameraViaPiggybackCamera.py` | Added `encoding='utf-8', errors='replace'` to `open(path,"r")` at line 1134 |
| `export_flame_LD_3DE4_batch.py` | Added `encoding='utf-8', errors='replace'` to 5 read-mode `open()` calls (template loading) |

### Affected File Details

#### exportBlender.py (v2.2)
| Line (approx) | Function | Change |
|---|---|---|
| 98 | `getScriptVersion()` | `open(..., 'r')` → `open(..., 'r', encoding='utf-8', errors='replace')` |
| 1014 | `_preferences_editor()` | same |
| 1249 | `read_preferences_file()` | same |
| 3834 | `main()` — log read | same |
| 3749, 3862, 3881 | `main()` — re-exec self | `exec(open(path).read())` → `exec(open(path, encoding='utf-8', errors='replace').read())` |

#### export_maya.py (v8.1)
| Line (approx) | Context | Change |
|---|---|---|
| 2309 | `read_preferences_file()` | Added `encoding='utf-8', errors='replace'` |
| 2655 | `_preferences_editor()` | same |
| 3112 | `main()` — log read | same |
| 3031, 3140, 3158 | `main()` — re-exec self | `exec(open(...).read())` → `with open(..., "r", encoding='utf-8', errors='replace') as f: exec(f.read())` |

#### calcMainCameraViaPiggybackCamera.py (v1.5)
| Line (approx) | Context | Change |
|---|---|---|
| 1134 | `importCalibration()` | `open(path,"r")` → `open(path,"r", encoding='utf-8', errors='replace')` |

#### export_flame_LD_3DE4_batch.py (v1.7)
| Line (approx) | Context | Change |
|---|---|---|
| 813, 829, 845 | Template loading (`create_resize_node_*`, `create_root_node`) | `open(path,"r")` → `open(path,"r", encoding='utf-8', errors='replace')` |
| 862 | Batch template loading | same |
| 1038 | Fingerprint check | same |

---

## How to Apply (Automatic)

Run the companion script **inside 3DEqualizer4**:

```
Main Window > Python > Run Script... → Select Fix_Exporters_UTF8.py
```

Then **fully restart 3DE4** (do NOT just use `tde4.rescanPythonDirs()`).

> **Note:** `Fix_Blender_Export.py` is a legacy Blender-only helper kept for
> reference. It is superseded by `Fix_Exporters_UTF8.py`. Do not use it as
> the default entry point.

## Rollback

All modified files have backup copies saved with suffix `.encoding_backup` in the same directory.
To undo:

1. Copy each `.encoding_backup` file back to the original `.py` filename
2. Move `export_blender.py.bak` from `py_scripts_disabled/` back to `py_scripts/` and rename to `export_blender.py`

## Related Audit Findings (Recorded, Not Yet Fixed)

A full read-only audit also identified the following items (not yet patched):

- **36 total read-mode `open()` calls** across all scripts lack `encoding=` — only exporter files patched above
- **71 write-mode `open()` calls** lack `encoding=` — silent data corruption risk on GBK systems
- **60+ bare `except:` clauses** — swallow all exception types including KeyboardInterrupt
- **17 `except: pass` blocks** — completely silent error swallowing
- **2 mutable default arguments** — `mhp_connector.py:356`, `lnscon_browse_lenses.py:219`
- **9 scripts missing version tag**, **8 with empty version string**
- **1 `.bak` file was moved** to `py_scripts_disabled/` to eliminate the Blender name collision

See the audit report for full details.

## Date

2026-06-29
