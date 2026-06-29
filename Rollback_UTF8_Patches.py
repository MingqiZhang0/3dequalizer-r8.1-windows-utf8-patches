#
#
# 3DE4.script.name: Rollback UTF-8 Patches
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Restores all .encoding_backup files and moves the
# 3DE4.script.comment: disabled export_blender.py back to py_scripts/.
# 3DE4.script.comment: Run inside 3DEqualizer4, then restart 3DE4.
#

"""
Rollback_UTF8_Patches.py
========================
Restores all changes made by Fix_Exporters_UTF8.py (and the legacy
Fix_Blender_Export.py).

What it does:
  1. Finds all *.encoding_backup files under sys_data/py_scripts/
  2. Restores each backup to its original .py filename
  3. Moves py_scripts_disabled/export_blender.py.bak back to
     py_scripts/export_blender.py
  4. Reports what was restored and what was missing

IDEMPOTENT - running it multiple times is safe.
It will NOT modify anything without user confirmation.
"""

import os
import shutil
import tde4


# ---------------------------------------------------------------------------
# Version detection (same logic as Fix_Exporters_UTF8.py)
# ---------------------------------------------------------------------------
SUPPORTED_VERSION_MARKER = "Release 8.1"


def get_3de_version_string():
    """Return the 3DE version string, or 'UNKNOWN' on any failure."""
    try:
        if hasattr(tde4, "get3DEVersion"):
            v = tde4.get3DEVersion()
            if isinstance(v, str) and v.strip():
                return v.strip()
    except Exception:
        pass
    return "UNKNOWN"


def is_supported_3de_version(version_string):
    """Check if version_string indicates a supported 3DE release."""
    if not version_string or version_string == "UNKNOWN":
        return False
    return SUPPORTED_VERSION_MARKER in version_string


ROLLBACK_LOG = []


def get_install_path():
    return tde4.get3DEInstallPath()


def get_py_scripts_dir():
    return os.path.join(get_install_path(), "sys_data", "py_scripts")


def get_disabled_dir():
    return os.path.join(get_install_path(), "sys_data", "py_scripts_disabled")


def collect_backup_files(py_scripts_dir):
    """Scan for all .encoding_backup files and return {original_path: backup_path}."""
    backups = {}
    if not os.path.isdir(py_scripts_dir):
        return backups

    for entry in os.listdir(py_scripts_dir):
        if entry.endswith(".encoding_backup"):
            backup_path = os.path.join(py_scripts_dir, entry)
            original_name = entry[:-len(".encoding_backup")]
            original_path = os.path.join(py_scripts_dir, original_name)
            backups[original_path] = backup_path

    return backups


def restore_backups(backups):
    """
    Restore each .encoding_backup -> original .py file.

    Strategy: copy the backup over the target (overwrite if exists).
    This is safe because:
      - If the target is the patched version, we're restoring the original.
      - If the target is already the original (e.g. manual restore), this
        is a no-op.
      - The .encoding_backup itself is NOT deleted, so rollback of the
        rollback is always possible.
    """
    if not backups:
        ROLLBACK_LOG.append("[SKIP] No .encoding_backup files found in py_scripts/.")
        return

    for original_path, backup_path in sorted(backups.items()):
        if not os.path.isfile(backup_path):
            ROLLBACK_LOG.append(
                "[WARN] Backup file missing (already restored or deleted): %s"
                % os.path.basename(backup_path)
            )
            continue

        try:
            shutil.copy2(backup_path, original_path)
            ROLLBACK_LOG.append(
                "[OK] Restored: %s  <-  %s"
                % (os.path.basename(original_path), os.path.basename(backup_path))
            )
        except Exception as e:
            ROLLBACK_LOG.append(
                "[ERROR] Failed to restore %s: %s"
                % (os.path.basename(original_path), str(e))
            )


def restore_disabled_blender_script(py_scripts_dir):
    """
    Move export_blender.py.bak from py_scripts_disabled/ back to py_scripts/.

    Also checks the legacy location (py_scripts/export_blender.py.bak)
    in case the user ran the old Fix_Blender_Export.py.
    """
    disabled_dir = get_disabled_dir()
    bak_file = os.path.join(disabled_dir, "export_blender.py.bak")
    target_file = os.path.join(py_scripts_dir, "export_blender.py")

    # Case 1: target already exists -nothing to do
    if os.path.isfile(target_file):
        ROLLBACK_LOG.append(
            "[SKIP] export_blender.py already exists in py_scripts/ -"
            "no need to restore from disabled."
        )
        return

    # Case 2: standard location (from Fix_Exporters_UTF8.py or latest
    #          Fix_Blender_Export.py)
    if os.path.isfile(bak_file):
        try:
            shutil.move(bak_file, target_file)
            ROLLBACK_LOG.append(
                "[OK] Restored: py_scripts_disabled/export_blender.py.bak\n"
                "     -> py_scripts/export_blender.py"
            )
        except Exception as e:
            ROLLBACK_LOG.append(
                "[ERROR] Failed to restore export_blender.py: %s" % str(e)
            )
        return

    # Case 3: legacy location -py_scripts/export_blender.py.bak
    #          (from the very first version of Fix_Blender_Export.py
    #           that renamed in-place)
    legacy_bak = os.path.join(py_scripts_dir, "export_blender.py.bak")
    if os.path.isfile(legacy_bak):
        try:
            os.rename(legacy_bak, target_file)
            ROLLBACK_LOG.append(
                "[OK] Restored from legacy location:\n"
                "     export_blender.py.bak -> export_blender.py"
            )
        except Exception as e:
            ROLLBACK_LOG.append(
                "[ERROR] Failed to restore legacy backup: %s" % str(e)
            )
        return

    # Case 4: nothing found
    ROLLBACK_LOG.append(
        "[SKIP] No disabled export_blender.py found -"
        "name-collision fix was not applied (or was already rolled back)."
    )


def main():
    py_scripts = get_py_scripts_dir()

    # --- Version info ---
    version_string = get_3de_version_string()
    version_ok = is_supported_3de_version(version_string)

    # --- Collect what will be restored for the preview ---
    backups = collect_backup_files(py_scripts)

    disabled_dir = get_disabled_dir()
    bak_file = os.path.join(disabled_dir, "export_blender.py.bak")
    legacy_bak = os.path.join(py_scripts, "export_blender.py.bak")
    target_blender = os.path.join(py_scripts, "export_blender.py")

    has_disabled_blender = (
        os.path.isfile(bak_file)
        or (os.path.isfile(legacy_bak) and not os.path.isfile(target_blender))
    )

    # --- Preview message ---
    preview_lines = [
        "Detected 3DE version:\n"
        "  %s" % version_string,
    ]

    if not version_ok:
        preview_lines.append(
            "\n"
            "WARNING: This rollback script was designed for\n"
            "3DEqualizer4 Release 8.1.\n"
            "\n"
            "Proceed only if you are undoing a previous run\n"
            "of the UTF-8 patch on this installation.\n"
        )

    preview_lines.append("\nThis rollback will restore:\n")

    if backups:
        preview_lines.append("  Backup files to restore:")
        for original_path in sorted(backups.keys()):
            preview_lines.append(
                "    %s  <-  %s.encoding_backup"
                % (os.path.basename(original_path), os.path.basename(original_path))
            )
    else:
        preview_lines.append("  (No .encoding_backup files found)")

    if has_disabled_blender:
        preview_lines.append(
            "\n  Restore export_blender.py\n"
            "  from disabled location"
        )

    if not backups and not has_disabled_blender:
        preview_lines.append(
            "\nNothing to roll back -your installation\n"
            "appears to be in its original state."
        )

    preview_lines.append("\nAfter rollback, you MUST restart 3DEqualizer4.")

    preview = "\n".join(preview_lines)

    # --- User confirmation ---
    result = tde4.postQuestionRequester(
        "Rollback UTF-8 Patches v1.0",
        preview,
        "Proceed", "Cancel",
    )

    # tde4.postQuestionRequester returns 1 for the first button ("Proceed"),
    # 2 for the second ("Cancel").  Anything else is treated as cancel.
    if result != 1:
        ROLLBACK_LOG.append("[ABORT] Rollback cancelled by user -no changes were made.")
        tde4.postQuestionRequester(
            "Rollback - Cancelled",
            "No changes were made.",
            "Ok",
        )
        return

    # --- Execute ---
    restore_backups(backups)
    restore_disabled_blender_script(py_scripts)

    # --- Report ---
    report = "\n".join(ROLLBACK_LOG)
    report += "\n\n>>> Please RESTART 3DEqualizer4 now. <<<"

    tde4.postQuestionRequester("Rollback UTF-8 Patches - Done", report, "Ok")


if __name__ == "__main__":
    main()
