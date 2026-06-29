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
        FIX_LOG.append("[OK] Blender: moved export_blender.py → py_scripts_disabled/export_blender.py.bak")
    else:
        FIX_LOG.append("[SKIP] Blender: export_blender.py not found (collision already resolved)")


# ---------------------------------------------------------------------------
# Fix 2: Exact-match UTF-8 encoding patch table
# ---------------------------------------------------------------------------
# Each entry: (original_snippet, replacement_snippet)
# - original_snippet MUST match the R8.1 original source exactly.
# - replacement_snippet is the patched version.
# - Idempotent: if replacement_snippet is already present, we skip.
# - If original_snippet is not found and replacement is also absent, we warn.
#
# Risk categories (for documentation / review — not used by the engine):
#   header    — reading script's own header (version/name)
#   prefs     — reading user preferences file
#   log       — reading log output
#   template  — reading 3DE internal XML/HTML templates
#   self-exec — re-executing the script itself
#   user-data — reading user-supplied data files (calibration, etc.)
# ---------------------------------------------------------------------------

PATCH_TABLE = [
    # ================================================================
    # exportBlender.py
    # ================================================================
    {
        "file": "exportBlender.py",
        "label": "Blender: exportBlender.py",
        "replacements": [
            # getScriptVersion() — reads own script header
            ("open(script_path, 'r')",
             "open(script_path, 'r', encoding='utf-8', errors='replace')"),
            # _preferences_editor() + read_preferences_file() — 2 occurrences
            ("open(self.prefs_file, 'r')",
             "open(self.prefs_file, 'r', encoding='utf-8', errors='replace')"),
            # main() — reads log file
            ("open(log, 'r')",
             "open(log, 'r', encoding='utf-8', errors='replace')"),
            # main() — re-executes self (3 occurrences)
            ("exec(open(script_path).read())",
             "exec(open(script_path, encoding='utf-8', errors='replace').read())"),
        ],
    },

    # ================================================================
    # export_maya.py
    # ================================================================
    {
        "file": "export_maya.py",
        "label": "Maya: export_maya.py",
        "replacements": [
            # read_preferences_file() — reads user prefs
            ('open(prefs, "r")',
             'open(prefs, "r", encoding="utf-8", errors="replace")'),
            # _preferences_editor() + main() log read — 2 occurrences
            ('open(log_file, "r")',
             'open(log_file, "r", encoding="utf-8", errors="replace")'),
            # main() — re-executes self (3 occurrences)
            ("exec(open(script_path).read())",
             "exec(open(script_path, encoding='utf-8', errors='replace').read())"),
        ],
    },

    # ================================================================
    # calcMainCameraViaPiggybackCamera.py
    #
    # ⚠️ RISK NOTE: importCalibration() reads USER calibration data.
    # Using strict UTF-8 (encoding='utf-8' WITHOUT errors='replace')
    # so a non-UTF-8 file raises a visible error instead of silently
    # corrupting data.  See Potential_Risks.md.
    # ================================================================
    {
        "file": "calcMainCameraViaPiggybackCamera.py",
        "label": "Piggyback: calcMainCameraViaPiggybackCamera.py",
        "replacements": [
            # importCalibration() — user calibration data (1 occurrence)
            ('open(path,"r")',
             'open(path,"r", encoding="utf-8")'),
        ],
    },

    # ================================================================
    # export_flame_LD_3DE4_batch.py
    # ================================================================
    {
        "file": "export_flame_LD_3DE4_batch.py",
        "label": "Flame: export_flame_LD_3DE4_batch.py",
        "replacements": [
            # create_resize_node_* / create_root_node / batch / fingerprint
            # — reads 3DE internal XML templates (5 occurrences)
            ('open(path,"r")',
             'open(path,"r", encoding="utf-8", errors="replace")'),
        ],
    },
]


# ---------------------------------------------------------------------------
# Helper: backup a file (idempotent — skips if .encoding_backup exists)
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
    Apply every replacement in *entry* to a single target file.

    Idempotency:
      - If *replacement_snippet* is already present → SKIP
      - If *original_snippet* is NOT found AND replacement is absent → WARN
      - Otherwise → apply (all occurrences)

    Backup is created before the first modification.
    Returns a list of report strings.
    """
    target_basename = entry["file"]
    label = entry["label"]
    replacements = entry["replacements"]

    target = os.path.join(get_py_scripts_dir(), target_basename)

    if not os.path.isfile(target):
        return ["[ERROR] %s: file not found — %s" % (label, target)]

    # Ensure backup exists BEFORE we read/modify
    backup_fresh = _backup(target)
    if backup_fresh:
        FIX_LOG.append("[INFO] %s: backup created — %s.encoding_backup"
                       % (label, target_basename))

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    report_lines = []
    changed = False

    for orig_snippet, repl_snippet in replacements:
        # --- Already patched? ---
        if repl_snippet in content:
            report_lines.append(
                "[SKIP] %s: already patched — %s"
                % (label, _truncate(orig_snippet, 60))
            )
            continue

        # --- Original snippet present? ---
        count = content.count(orig_snippet)
        if count == 0:
            report_lines.append(
                "[WARN] %s: expected pattern not found — %s\n"
                "       (file may differ from 3DE4 R8.1 original; "
                "please verify manually)"
                % (label, _truncate(orig_snippet, 60))
            )
            continue

        # --- Apply ---
        content = content.replace(orig_snippet, repl_snippet)
        report_lines.append(
            "[OK] %s: patched %d occurrence(s) — %s"
            % (label, count, _truncate(orig_snippet, 60))
        )
        changed = True

    if changed:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)

    if not report_lines:
        report_lines.append("[SKIP] %s: empty replacement list" % label)

    return report_lines


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
        "    → py_scripts_disabled/export_blender.py.bak\n"
        "\n"
        "  PATCH (exact-match, add UTF-8 encoding):\n"
        "    py_scripts/exportBlender.py\n"
        "    py_scripts/export_maya.py\n"
        "    py_scripts/calcMainCameraViaPiggybackCamera.py\n"
        "      (user-data path — strict UTF-8,\n"
        "       NO errors='replace')\n"
        "    py_scripts/export_flame_LD_3DE4_batch.py\n"
        "\n"
        "Backup files (.encoding_backup) will be\n"
        "created before any modification.\n"
        "\n"
        "Patches are IDEMPOTENT — safe to re-run.\n"
        "\n"
        "After the fix, you MUST fully restart\n"
        "3DEqualizer4 (do NOT just rescan Python dirs).",
        "Proceed", "Cancel",
    )

    # tde4.postQuestionRequester returns 1 for the first button
    # ("Proceed"), 2 for the second ("Cancel").  Anything else is
    # treated as cancel to be safe.
    if result != 1:
        FIX_LOG.append("[ABORT] User cancelled — no changes were made.")
        tde4.postQuestionRequester(
            "Fix Exporters UTF-8 — Cancelled",
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

    tde4.postQuestionRequester("Fix Exporters UTF-8 — Done", report, "Ok")


if __name__ == "__main__":
    main()
