#
#
# 3DE4.script.name: Fix Exporters UTF-8 (Blender+Maya+Piggy+Flame)
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Fixes: (1) Blender export menu collision + UnicodeDecodeError,
# 3DE4.script.comment:        (2) Maya export exec/open UnicodeDecodeError,
# 3DE4.script.comment:        (3) Piggyback Camera calibration import UnicodeDecodeError,
# 3DE4.script.comment:        (4) Flame Matchbox template loading UnicodeDecodeError.
# 3DE4.script.comment: Run once, then restart 3DE4.
#

import os
import shutil
import tde4


FIX_LOG = []


def get_py_scripts_dir():
    install = tde4.get3DEInstallPath()
    return os.path.join(install, "sys_data", "py_scripts")


def get_disabled_dir():
    install = tde4.get3DEInstallPath()
    return os.path.join(install, "sys_data", "py_scripts_disabled")


# ---------------------------------------------------------------------------
# Fix 1: Blender name collision — move old export_blender.py out of py_scripts
# ---------------------------------------------------------------------------
def fix_blender_name_collision(py_scripts):
    disabled = get_disabled_dir()
    old_file = os.path.join(py_scripts, "export_blender.py")
    bak_file = os.path.join(disabled, "export_blender.py.bak")

    if os.path.isfile(bak_file):
        FIX_LOG.append("[SKIP] Blender: export_blender.py.bak already in py_scripts_disabled/")
        return

    if os.path.isfile(old_file):
        os.makedirs(disabled, exist_ok=True)
        shutil.move(old_file, bak_file)
        FIX_LOG.append("[OK] Blender: moved export_blender.py -> py_scripts_disabled/export_blender.py.bak")
    else:
        FIX_LOG.append("[SKIP] Blender: export_blender.py not found (collision already resolved)")


# ---------------------------------------------------------------------------
# Fix 2: Exact-match UTF-8 encoding patch table (based on real R8.1 scan)
# ---------------------------------------------------------------------------
#
# Each entry has:
#   comment         — human explanation of which function / what data
#   already_patched — list of patterns; if ANY is found in file → SKIP
#   originals       — list of original unpatched patterns (checked in order,
#                     most-specific first to avoid substring false positives)
#   replacement     — what to substitute for the matched original
#
# Risk categories (documentation only, not used by the engine):
#   header    — reading script's own header (version/name)
#   prefs     — reading user preferences file
#   log       — reading log output
#   template  — reading 3DE internal XML/HTML templates
#   self-exec — re-executing the script itself
#   user-data — reading user-supplied data files (calibration, etc.)
# ---------------------------------------------------------------------------

PATCH_TABLE = [
    # ================================================================
    # exportBlender.py  (scanned from real 3DE4 R8.1 install)
    # ================================================================
    {
        "file": "exportBlender.py",
        "label": "Blender: exportBlender.py",
        "entries": [
            {
                "comment": "getScriptVersion() line 98 — reads own script header",
                "already_patched": [
                    "open(os.sep.join([dirname, fname]), 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(os.sep.join([dirname, fname]), 'r')",
                ],
                "replacement": "open(os.sep.join([dirname, fname]), 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "_preferences_editor() line 1014 — reads user prefs",
                "already_patched": [
                    "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(preferences_file, 'r')",
                ],
                "replacement": "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "read_preferences_file() line 1249 — reads user prefs",
                "already_patched": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r')",
                ],
                "replacement": "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "main() line 3834 — reads log file",
                "already_patched": [
                    "open(log, 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(log, 'r')",
                ],
                "replacement": "open(log, 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "main() lines 3749,3862,3881 — re-executes self (3 occurrences)",
                "already_patched": [
                    "open(script_path, encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "exec(open(script_path).read())",
                ],
                "replacement": "exec(open(script_path, encoding='utf-8', errors='replace').read())",
            },
        ],
    },

    # ================================================================
    # export_maya.py  (scanned from real 3DE4 R8.1 install)
    # ================================================================
    {
        "file": "export_maya.py",
        "label": "Maya: export_maya.py",
        "entries": [
            {
                "comment": "read_preferences_file() line 2309 — reads user prefs",
                "already_patched": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r')",
                ],
                "replacement": "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "_preferences_editor() line 2655 — reads user prefs",
                "already_patched": [
                    "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(preferences_file, 'r')",
                ],
                "replacement": "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "main() line 3112 — reads log file",
                "already_patched": [
                    "open(log, 'r', encoding='utf-8', errors='replace')",
                ],
                "originals": [
                    "open(log, 'r')",
                ],
                "replacement": "open(log, 'r', encoding='utf-8', errors='replace')",
            },
            {
                "comment": "main() lines 3031,3140,3158 — re-executes self (3 occurrences); "
                           "accepts both single-line inline encoding and multi-line with-block",
                "already_patched": [
                    "open(script_path, encoding='utf-8', errors='replace')",
                    'open(script_path, "r", encoding="utf-8", errors="replace")',
                ],
                "originals": [
                    "exec(open(script_path).read())",
                ],
                "replacement": "exec(open(script_path, encoding='utf-8', errors='replace').read())",
            },
        ],
    },

    # ================================================================
    # calcMainCameraViaPiggybackCamera.py  (scanned from real R8.1)
    #
    # RISK NOTE: importCalibration() line 1134 reads USER calibration data.
    # Using strict UTF-8 WITHOUT errors='replace' so bad data raises a
    # visible error instead of silently corrupting content.
    #
    # If the file was patched by a previous version of this script (which
    # used errors='replace'), we UPGRADE it to strict UTF-8.
    # ================================================================
    {
        "file": "calcMainCameraViaPiggybackCamera.py",
        "label": "Piggyback: calcMainCameraViaPiggybackCamera.py",
        "entries": [
            {
                "comment": "importCalibration() line 1134 — USER calibration data; strict UTF-8",
                "already_patched": [
                    # Already strict (ideal state) — both quote variants
                    'open(path,"r", encoding=\'utf-8\')',
                ],
                "originals": [
                    # Most-specific first: old patch with errors='replace' → upgrade
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                    # Unpatched original
                    'open(path,"r")',
                ],
                "replacement": 'open(path,"r", encoding=\'utf-8\')',
            },
        ],
    },

    # ================================================================
    # export_flame_LD_3DE4_batch.py  (scanned from real R8.1 install)
    # ================================================================
    {
        "file": "export_flame_LD_3DE4_batch.py",
        "label": "Flame: export_flame_LD_3DE4_batch.py",
        "entries": [
            {
                "comment": "create_resize_node_add_margin() line 813 — XML template",
                "already_patched": [
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "originals": [
                    'open(path,"r")',
                ],
                "replacement": 'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
            },
            {
                "comment": "create_resize_node_remove_margin() line 829 — XML template",
                "already_patched": [
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "originals": [
                    'open(path,"r")',
                ],
                "replacement": 'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
            },
            {
                "comment": "create_root_node() line 845 — XML template",
                "already_patched": [
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "originals": [
                    'open(path,"r")',
                ],
                "replacement": 'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
            },
            {
                "comment": "batch export line 862 — batch template (different path arg)",
                "already_patched": [
                    'open(os.path.join(self._tde4_flame_path,"pipeline.batch.template.xml"),"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "originals": [
                    'open(os.path.join(self._tde4_flame_path,"pipeline.batch.template.xml"),"r")',
                ],
                "replacement": 'open(os.path.join(self._tde4_flame_path,"pipeline.batch.template.xml"),"r", encoding=\'utf-8\', errors=\'replace\')',
            },
            {
                "comment": "fingerprint check line 1038 — fingerprint file (different path arg)",
                "already_patched": [
                    'open(os.path.join(path,"fingerprint"),"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "originals": [
                    'open(os.path.join(path,"fingerprint"),"r")',
                ],
                "replacement": 'open(os.path.join(path,"fingerprint"),"r", encoding=\'utf-8\', errors=\'replace\')',
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Helper: backup a file (idempotent - skips if .encoding_backup exists)
# ---------------------------------------------------------------------------
def _backup(target):
    """Create .encoding_backup copy.  Returns True if a new backup was made."""
    bak = target + ".encoding_backup"
    if not os.path.isfile(bak):
        shutil.copy2(target, bak)
        return True
    return False


def _truncate(s, max_len):
    """Shorten a snippet for log lines."""
    s = s.replace("\n", "\\n")
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."


def apply_patch_table(entry):
    """
    Apply every fix-entry in *entry* to a single target file.

    For each fix-entry:
      1. Check already_patched patterns — if ANY is in content → SKIP
      2. Check originals (in order, most-specific first) — first match wins
      3. Replace matched original with replacement → OK
      4. If nothing matched → WARN

    Backup is deferred until the first actual write (no backup if all SKIP).

    Returns a list of report strings.
    """
    target_basename = entry["file"]
    label = entry["label"]
    entries = entry["entries"]

    target = os.path.join(get_py_scripts_dir(), target_basename)

    if not os.path.isfile(target):
        return ["[ERROR] %s: file not found - %s" % (label, target)]

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    report_lines = []
    changed = False
    backup_done = False

    for e in entries:
        comment = e.get("comment", "")
        already_patched = e.get("already_patched", [])
        originals = e.get("originals", [])
        replacement = e["replacement"]

        # --- 1. Check if already patched (any variant) ---
        already = False
        for ap in already_patched:
            if ap in content:
                report_lines.append(
                    "[SKIP] %s: already patched - %s"
                    % (label, _truncate(comment, 60))
                )
                already = True
                break
        if already:
            continue

        # --- 2. Find a matching original (most-specific first) ---
        matched_original = None
        for orig in originals:
            if orig in content:
                matched_original = orig
                break

        if matched_original is None:
            # Build a hint: search for nearby open/exec lines
            hint = _find_nearby_hint(content, originals)
            report_lines.append(
                "[WARN] %s: expected pattern not found - %s\n"
                "       (file may differ from 3DE4 R8.1 original; "
                "please verify manually)%s"
                % (label, _truncate(comment, 50), hint)
            )
            continue

        # --- 3. Defer backup until first actual write ---
        if not backup_done:
            backup_fresh = _backup(target)
            if backup_fresh:
                report_lines.append(
                    "[INFO] %s: backup created - %s.encoding_backup"
                    % (label, target_basename)
                )
            backup_done = True

        # --- 4. Apply replacement ---
        count = content.count(matched_original)
        content = content.replace(matched_original, replacement)
        report_lines.append(
            "[OK] %s: patched %d occurrence(s) - %s"
            % (label, count, _truncate(comment, 50))
        )
        changed = True

    if changed:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)

    if not report_lines:
        report_lines.append("[SKIP] %s: empty entry list" % label)

    return report_lines


def _find_nearby_hint(content, originals):
    """Try to find a line near any of the originals for diagnostic purposes."""
    # Use the first original as a probe — look for a partial match
    probe = originals[0] if originals else ""
    # Take a short distinctive part of the probe
    short = probe[:min(30, len(probe))]
    if not short:
        return ""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if short in line:
            return "\n       nearby line %d: %s" % (i + 1, line.strip()[:120])
    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    py_scripts = get_py_scripts_dir()

    # -- Confirmation dialog --
    result = tde4.postQuestionRequester(
        "Fix Exporters UTF-8 v1.0",
        "This script will modify the following files\n"
        "under your 3DEqualizer4 installation:\n"
        "\n"
        "  MOVE:\n"
        "    py_scripts/export_blender.py\n"
        "    -> py_scripts_disabled/export_blender.py.bak\n"
        "\n"
        "  PATCH (exact-match, add UTF-8 encoding):\n"
        "    py_scripts/exportBlender.py\n"
        "    py_scripts/export_maya.py\n"
        "    py_scripts/calcMainCameraViaPiggybackCamera.py\n"
        "      (user-data path - strict UTF-8,\n"
        "       NO errors='replace')\n"
        "    py_scripts/export_flame_LD_3DE4_batch.py\n"
        "\n"
        "Backup files (.encoding_backup) will be\n"
        "created only if a file actually changes.\n"
        "\n"
        "Patches are IDEMPOTENT - safe to re-run.\n"
        "\n"
        "After the fix, you MUST fully restart\n"
        "3DEqualizer4 (do NOT just rescan Python dirs).",
        "Proceed", "Cancel",
    )

    # tde4.postQuestionRequester returns 1 for the first button
    # ("Proceed"), 2 for the second ("Cancel").  Anything else is
    # treated as cancel to be safe.
    if result != 1:
        FIX_LOG.append("[ABORT] User cancelled - no changes were made.")
        tde4.postQuestionRequester(
            "Fix Exporters UTF-8 - Cancelled",
            "No changes were made.",
            "Ok",
        )
        return

    # -- Phase 1: Blender name collision (unchanged logic) --
    fix_blender_name_collision(py_scripts)

    # -- Phase 2: Apply encoding patches from the exact-match table --
    for entry in PATCH_TABLE:
        report_lines = apply_patch_table(entry)
        FIX_LOG.extend(report_lines)

    # Report
    report = "\n".join(FIX_LOG)
    report += "\n\n>>> Please RESTART 3DEqualizer4 now. <<<"

    tde4.postQuestionRequester("Fix Exporters UTF-8 - Done", report, "Ok")


if __name__ == "__main__":
    main()
