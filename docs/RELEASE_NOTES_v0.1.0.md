# v0.1.0 - Initial public patch release

**Unofficial patch for 3DEqualizer4 R8.1 on Windows Chinese / GBK locale.**

---

## What this release fixes

### 1. Blender Export Menu Unresponsive

**Symptom:** `Main Window > 3DE4 > Export Project > Blender...` does nothing.

**Root cause:** Two scripts register the same menu entry:
- `export_blender.py` (v1.3, legacy)
- `exportBlender.py` (v2.2, current)

Both declare `name: Blender...` + `gui: Main Window::3DE4::Export Project`,
creating an ambiguous script index.

**Fix:** Moves the legacy `export_blender.py` to `py_scripts_disabled/`.

### 2. UnicodeDecodeError on Chinese Windows

**Symptom:**
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x80 ...
```

**Root cause:** Python's default `open()` encoding is `cp936` (GBK) on
Chinese Windows, but exporter scripts read UTF-8 files without an explicit
`encoding=` argument.

**Fix:** Adds `encoding='utf-8'` to read-mode `open()` and
`exec(open(...).read())` calls in 4 exporter scripts:
- `exportBlender.py`
- `export_maya.py`
- `calcMainCameraViaPiggybackCamera.py` (strict UTF-8, no `errors='replace'`
  for user-data safety)
- `export_flame_LD_3DE4_batch.py`

---

## Included scripts

| File | Role |
|------|------|
| `Fix_Exporters_UTF8.py` | Main patch entry point. Run this inside 3DE4. |
| `Rollback_UTF8_Patches.py` | Undo all changes. Preview-before-execute. |
| `Fix_Blender_Export.py` | Legacy Blender-only helper. Superseded. |
| `README.md` | Full documentation. |
| `Fix_README.md` | Detailed fix notes with root-cause analysis. |
| `Potential_Risks.md` | Read-only audit of ~250 scripts in R8.1. |
| `CHANGELOG.md` | Version history. |
| `LICENSE` | MIT License. |

---

## Tested environment

- **Application:** 3DEqualizer4 Release 8.1
- **OS:** Windows 11 Home
- **Locale:** Chinese / GBK default encoding
- **Smoke test:** Real 3DE4 run passed for patch application and idempotent
  re-run.

Other 3DE versions, platforms, and locales are **NOT** tested.

---

## How to use

1. **Back up** your 3DEqualizer4 installation folder.
2. Launch 3DEqualizer4 **as Administrator** (if installed under `Program Files`).
3. Go to **Main Window > Python > Run Script...**
4. Select **`Fix_Exporters_UTF8.py`**.
5. Click **Proceed** on the confirmation dialog.
6. **Fully exit** 3DEqualizer4 (do NOT just rescan Python dirs).
7. Restart 3DEqualizer4.

**Do NOT** run `python Fix_Exporters_UTF8.py` from a terminal — the scripts
import `tde4` (the 3DE4 Python API) and will fail with `ModuleNotFoundError`.

---

## Rollback

Run **`Rollback_UTF8_Patches.py`** inside 3DEqualizer4 (same method as above),
then restart.  All `.encoding_backup` files are restored and the disabled
Blender script is moved back.

Rollback is idempotent — safe to run multiple times.

Still, a full installation backup is recommended before applying any patch.

---

## Important limitations

- **Unofficial patch.** Not affiliated with or endorsed by Science-D-Visions.
- **Version-specific.** The exact-match replacement table was built against
  a specific 3DEqualizer4 R8.1 installation. If your local script files
  differ (e.g. different release build, already modified, or custom scripts),
  the patcher will report `WARN expected pattern not found`. Stop and verify
  manually if this occurs.
- **`errors='replace'` caveat.** Most `open()` fixes use `errors='replace'`,
  which silently substitutes undecodable bytes with U+FFFD. This prevents
  crashes but may hide data issues. The Piggyback Camera calibration import
  path uses strict UTF-8 as an exception.
- **Windows / Chinese GBK locale only.** Other locales and platforms have
  not been tested.
- **Does NOT redistribute** any proprietary 3DEqualizer files. This
  repository contains only patch scripts and documentation.
- **Use at your own risk.** Always back up your installation first.

---

## Legal / license note

MIT License — applies to the patch scripts and documentation in this
repository. It does **not** apply to any proprietary 3DEqualizer files
or the 3DEqualizer4 application itself.
