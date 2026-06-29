#
#
# 3DE4.script.name: Cleanup UTF-8 Patch Backups
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Deletes .encoding_backup files created by the
# 3DE4.script.comment: UTF-8 exporter patch.  Does not delete disabled
# 3DE4.script.comment: Blender legacy script backups.
#

"""
Cleanup_UTF8_Backups.py
=======================
Deletes known .encoding_backup files created by Fix_Exporters_UTF8.py.

Only deletes these four files (if they exist):
  exportBlender.py.encoding_backup
  export_maya.py.encoding_backup
  calcMainCameraViaPiggybackCamera.py.encoding_backup
  export_flame_LD_3DE4_batch.py.encoding_backup

Does NOT delete:
  py_scripts_disabled/export_blender.py.bak   (disabled legacy script)
  py_scripts/export_blender.py.bak            (legacy in-place backup)

Requires double confirmation before any deletion.
"""

import os
import tde4


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------
SUPPORTED_VERSION_MARKER = "Release 8.1"


def get_3de_version_string():
    try:
        if hasattr(tde4, "get3DEVersion"):
            v = tde4.get3DEVersion()
            if isinstance(v, str) and v.strip():
                return v.strip()
    except Exception:
        pass
    return "UNKNOWN"


def is_supported_3de_version(version_string):
    if not version_string or version_string == "UNKNOWN":
        return False
    return SUPPORTED_VERSION_MARKER in version_string


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
def get_install_path():
    return tde4.get3DEInstallPath()


def get_py_scripts_dir():
    return os.path.join(get_install_path(), "sys_data", "py_scripts")


def get_disabled_dir():
    return os.path.join(get_install_path(), "sys_data", "py_scripts_disabled")


# ---------------------------------------------------------------------------
# Strictly scoped backup targets — only these four files may be deleted
# ---------------------------------------------------------------------------
BACKUP_TARGETS = [
    "exportBlender.py.encoding_backup",
    "export_maya.py.encoding_backup",
    "calcMainCameraViaPiggybackCamera.py.encoding_backup",
    "export_flame_LD_3DE4_batch.py.encoding_backup",
]

# Files that MUST NOT be deleted
PROTECTED_BLENDER_FILES = [
    ("py_scripts_disabled", "export_blender.py.bak"),
    ("py_scripts", "export_blender.py.bak"),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    py_scripts = get_py_scripts_dir()
    disabled_dir = get_disabled_dir()
    version_string = get_3de_version_string()
    version_ok = is_supported_3de_version(version_string)

    log = []

    # --- First confirmation: risk warning ---
    warning_text = (
        "WARNING:\n"
        "\n"
        "This script will DELETE .encoding_backup files\n"
        "created by the UTF-8 exporter patch.\n"
        "\n"
        "After deleting these backups,\n"
        "Rollback_UTF8_Patches.py may NOT be able to\n"
        "restore the original exporter files.\n"
        "\n"
        "Only proceed if:\n"
        "  1. The patch has been verified working.\n"
        "  2. You have a full external backup of your\n"
        "     3DE installation.\n"
        "  3. You accept losing local rollback backups.\n"
        "\n"
        "This cleanup does NOT delete:\n"
        "  py_scripts_disabled/export_blender.py.bak\n"
        "\n"
        "Click Cancel if you are not sure."
    )

    result = tde4.postQuestionRequester(
        "Cleanup UTF-8 Backups - Warning",
        warning_text,
        "Continue", "Cancel",
    )

    # postQuestionRequester returns 1 = first button, 2 = second button
    if result != 1:
        log.append("[ABORT] User cancelled at warning step - no files were deleted.")
        tde4.postQuestionRequester(
            "Cleanup - Cancelled",
            "No files were deleted.",
            "Ok",
        )
        return

    # --- Scan what exists ---
    existing_targets = []
    for bak_name in BACKUP_TARGETS:
        path = os.path.join(py_scripts, bak_name)
        if os.path.isfile(path):
            existing_targets.append((bak_name, path))

    if not existing_targets:
        log.append("[SKIP] No known .encoding_backup files were found.")
        log.append("[INFO] No files were deleted.")

        full = "\n".join(log) + "\n\nFull details were printed to the 3DE Python console."
        print(full)

        tde4.postQuestionRequester(
            "Cleanup - No cleanup needed",
            "No known .encoding_backup files were found.\n"
            "No files were deleted.",
            "Ok",
        )
        return

    # --- Second confirmation: list files to delete ---
    file_list = ""
    for bak_name, _ in existing_targets:
        file_list += "  %s\n" % bak_name

    confirm_text = (
        "The following backup files will be deleted:\n"
        "\n"
        "%s"
        "\n"
        "This action cannot be undone by this script.\n"
        "\n"
        "Click Delete to permanently delete these files.\n"
        "Click Cancel to keep them."
    ) % file_list

    result2 = tde4.postQuestionRequester(
        "Confirm Backup Deletion",
        confirm_text,
        "Delete", "Cancel",
    )

    if result2 != 1:
        log.append("[ABORT] User cancelled at delete confirmation - no files were deleted.")
        tde4.postQuestionRequester(
            "Cleanup - Cancelled",
            "No files were deleted.",
            "Ok",
        )
        return

    # --- Execute deletion ---
    deleted = 0
    failed = 0

    for bak_name, path in existing_targets:
        try:
            os.remove(path)
            log.append("[OK] Deleted: %s" % bak_name)
            deleted += 1
        except Exception as e:
            log.append("[ERROR] Failed to delete %s: %s" % (bak_name, str(e)))
            failed += 1

    # --- Check protected files (informational only) ---
    for dir_name, fname in PROTECTED_BLENDER_FILES:
        if dir_name == "py_scripts_disabled":
            path = os.path.join(disabled_dir, fname)
        else:
            path = os.path.join(py_scripts, fname)
        if os.path.isfile(path):
            log.append("[INFO] Disabled Blender legacy backup exists and was kept:")
            log.append("       %s/%s" % (dir_name, fname))

    # --- Unsupported version warning ---
    if not version_ok:
        log.append("")
        log.append("[WARN] Detected 3DE version: %s" % version_string)
        log.append("       This cleanup tool was designed for 3DEqualizer4 Release 8.1.")
        log.append("       Verify that the deleted files were created by the UTF-8 patch.")

    # --- Print full report to console ---
    full_report_lines = []
    full_report_lines.append("=" * 60)
    full_report_lines.append("Cleanup UTF-8 Backups - Full Report")
    full_report_lines.append("=" * 60)
    full_report_lines.append("")
    full_report_lines.append("Detected 3DE version: %s" % version_string)
    full_report_lines.append("")
    full_report_lines.extend(log)
    full_report_lines.append("")
    full_report_lines.append("=" * 60)
    full_report_lines.append("If you need to inspect current patch status, run:")
    full_report_lines.append("  Scan_Exporters_UTF8_Status.py")
    full_report_lines.append("=" * 60)

    full_report = "\n".join(full_report_lines)
    print(full_report)

    # --- Short popup summary ---
    popup = (
        "Cleanup complete.\n"
        "\n"
        "Deleted:\n"
        "  %d\n"
        "\n"
        "Failed:\n"
        "  %d\n"
        "\n"
        "Kept:\n"
        "  Disabled Blender legacy backup was not deleted.\n"
        "\n"
        "Full details were printed to the 3DE Python console."
    ) % (deleted, failed)

    tde4.postQuestionRequester(
        "Cleanup UTF-8 Backups - Done",
        popup,
        "Ok",
    )


if __name__ == "__main__":
    main()
