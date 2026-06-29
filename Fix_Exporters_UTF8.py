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
import re
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
# Fix 2: Add UTF-8 encoding to read-mode open() calls in a given file
# ---------------------------------------------------------------------------
def _backup(target):
    bak = target + ".encoding_backup"
    if not os.path.isfile(bak):
        shutil.copy2(target, bak)
        return True
    return False


def fix_utf8_read_opens(target, label):
    """Add encoding='utf-8', errors='replace' to all open(X, 'r') calls."""
    if not os.path.isfile(target):
        FIX_LOG.append("[ERROR] %s: file not found — %s" % (label, target))
        return

    _backup(target)

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content

    # Replace open(X, 'r') → open(X, 'r', encoding='utf-8', errors='replace')
    content = re.sub(
        r"open\((.+?), 'r'\)",
        r"open(\1, 'r', encoding='utf-8', errors='replace')",
        content,
    )

    if content != original:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        FIX_LOG.append("[OK] %s: added UTF-8 encoding to open(..., 'r') calls" % label)
    else:
        FIX_LOG.append("[SKIP] %s: already has encoding or no matches" % label)


def fix_utf8_exec_opens(target, label):
    """Replace exec(open(X).read()) with with open(X, 'r', encoding=...) as f: exec(f.read())."""
    if not os.path.isfile(target):
        FIX_LOG.append("[ERROR] %s: file not found — %s" % (label, target))
        return

    _backup(target)

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Pattern: exec(open(script_path).read())
    # We need to match the indentation to reproduce it with the with-block
    pattern = re.compile(r"([ \t]*)exec\(open\(script_path\)\.read\(\)\)")

    if pattern.search(content):
        def _replace(m):
            indent = m.group(1)
            inner_indent = indent + "    "
            return (
                indent + 'with open(script_path, "r", encoding="utf-8", errors="replace") as f:\n'
                + inner_indent + "exec(f.read())"
            )
        content = pattern.sub(_replace, content)

        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        FIX_LOG.append("[OK] %s: replaced exec(open(script_path).read()) with UTF-8 with-block" % label)
    else:
        FIX_LOG.append("[SKIP] %s: no exec(open(script_path).read()) calls found" % label)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    py_scripts = get_py_scripts_dir()

    # -- Phase 1: Blender --
    fix_blender_name_collision(py_scripts)
    fix_utf8_read_opens(
        os.path.join(py_scripts, "exportBlender.py"),
        "Blender: exportBlender.py",
    )
    fix_utf8_exec_opens(
        os.path.join(py_scripts, "exportBlender.py"),
        "Blender: exportBlender.py",
    )

    # -- Phase 2: Maya --
    fix_utf8_read_opens(
        os.path.join(py_scripts, "export_maya.py"),
        "Maya: export_maya.py",
    )
    fix_utf8_exec_opens(
        os.path.join(py_scripts, "export_maya.py"),
        "Maya: export_maya.py",
    )

    # -- Phase 2: Piggyback Camera --
    fix_utf8_read_opens(
        os.path.join(py_scripts, "calcMainCameraViaPiggybackCamera.py"),
        "Piggyback: calcMainCameraViaPiggybackCamera.py",
    )

    # -- Phase 2: Flame Matchbox --
    fix_utf8_read_opens(
        os.path.join(py_scripts, "export_flame_LD_3DE4_batch.py"),
        "Flame: export_flame_LD_3DE4_batch.py",
    )

    # Report
    report = "\n".join(FIX_LOG)
    report += "\n\n>>> Please RESTART 3DEqualizer4 now. <<<"

    tde4.postQuestionRequester("Fix Exporters UTF-8 — Done", report, "Ok")


if __name__ == "__main__":
    main()
