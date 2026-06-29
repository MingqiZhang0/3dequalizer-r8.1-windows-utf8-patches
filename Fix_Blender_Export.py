#
#
# 3DE4.script.name: Fix Blender Export (UTF-8 + Name Collision)
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Fixes: (1) Blender export button not responding due to script name collision,
# 3DE4.script.comment:        (2) UnicodeDecodeError on Windows Chinese locale due to missing UTF-8 encoding.
# 3DE4.script.comment: Run once, then restart 3DE4.
#

import os
import re
import tde4
import shutil
from datetime import datetime


FIX_LOG = []  # Collects what was done for the final report


def get_py_scripts_dir():
    """Return the absolute path to sys_data/py_scripts."""
    install = tde4.get3DEInstallPath()
    return os.path.join(install, "sys_data", "py_scripts")


def fix_name_collision(py_scripts):
    """
    Rename export_blender.py → export_blender.py.bak
    so 3DE4 no longer registers the old v1.3 script.
    """
    old_file = os.path.join(py_scripts, "export_blender.py")
    bak_file = os.path.join(py_scripts, "export_blender.py.bak")

    if os.path.isfile(bak_file):
        FIX_LOG.append("[SKIP] export_blender.py.bak already exists — name collision already resolved.")
        return

    if os.path.isfile(old_file):
        os.rename(old_file, bak_file)
        FIX_LOG.append("[OK] Renamed export_blender.py → export_blender.py.bak (removed name collision).")
    else:
        FIX_LOG.append("[SKIP] export_blender.py not found — name collision may not exist on this installation.")


def fix_utf8_encoding(py_scripts):
    """
    Add encoding='utf-8', errors='replace' to all read-mode open()
    calls in exportBlender.py, plus exec(open(...).read()) calls.
    A backup copy is saved beforehand.
    """
    target = os.path.join(py_scripts, "exportBlender.py")
    if not os.path.isfile(target):
        FIX_LOG.append("[ERROR] exportBlender.py not found — cannot apply encoding fix.")
        return

    # Backup
    bak = target + ".encoding_backup"
    if not os.path.isfile(bak):
        shutil.copy2(target, bak)
        FIX_LOG.append("[INFO] Backup saved: exportBlender.py.encoding_backup")

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content

    # --- Replacement 1 ---
    # open(X, 'r')  →  open(X, 'r', encoding='utf-8', errors='replace')
    #   .+? is non-greedy: matches the shortest span up to the FIRST ", 'r')"
    content = re.sub(
        r"open\((.+?), 'r'\)",
        r"open(\1, 'r', encoding='utf-8', errors='replace')",
        content,
    )

    # --- Replacement 2 ---
    # exec(open(script_path).read())  →  add encoding kwarg
    content = content.replace(
        "exec(open(script_path).read())",
        "exec(open(script_path, encoding='utf-8', errors='replace').read())",
    )

    if content != original:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        FIX_LOG.append("[OK] Added UTF-8 encoding to open() calls in exportBlender.py.")
    else:
        FIX_LOG.append("[SKIP] exportBlender.py already has encoding parameters (or no matches).")


def main():
    py_scripts = get_py_scripts_dir()

    tde4.postQuestionRequester(
        "Fix Blender Export v1.0",
        "This script will:\n\n"
        "  1) Rename export_blender.py → .bak\n"
        "     (eliminates menu name collision)\n\n"
        "  2) Add UTF-8 encoding to open()\n"
        "     calls in exportBlender.py\n"
        "     (fixes UnicodeDecodeError on\n"
        "     Chinese Windows)\n\n"
        "A backup of exportBlender.py will be\n"
        "saved with suffix .encoding_backup\n\n"
        "After the fix, you MUST restart 3DE4.",
        "Proceed", "Cancel",
    )

    # Ask which fixes to apply (user is already committed by clicking Proceed)
    # but we double-check...

    # Apply fixes
    fix_name_collision(py_scripts)
    fix_utf8_encoding(py_scripts)

    # Show report
    report = "\n".join(FIX_LOG)
    report += "\n\n>>> Please RESTART 3DEqualizer4 now. <<<"

    tde4.postQuestionRequester("Fix Blender Export — Done", report, "Ok")


if __name__ == "__main__":
    main()
