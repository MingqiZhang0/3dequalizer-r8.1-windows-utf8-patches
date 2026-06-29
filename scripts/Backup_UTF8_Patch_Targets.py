#
#
# 3DE4.script.name: Backup UTF-8 Patch Targets
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Creates .encoding_backup files for known UTF-8 patch targets.
# 3DE4.script.comment: Does not patch, move, or delete files.
#

"""
Backup_UTF8_Patch_Targets.py
============================
Creates .encoding_backup files for known UTF-8 patch target
exporter scripts.  Does NOT apply any patch, move files, or
delete anything.

Only backs up these four target files:
  exportBlender.py
  export_maya.py
  calcMainCameraViaPiggybackCamera.py
  export_flame_LD_3DE4_batch.py

Will NOT back up a file that already appears patched.
"""

import os
import shutil
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


# ---------------------------------------------------------------------------
# Known target files (basenames only - no wildcards)
# ---------------------------------------------------------------------------
BACKUP_TARGETS = [
    "exportBlender.py",
    "export_maya.py",
    "calcMainCameraViaPiggybackCamera.py",
    "export_flame_LD_3DE4_batch.py",
]

# Patterns that indicate a file has already been patched
PATCHED_INDICATORS = [
    "encoding='utf-8'",
    'encoding="utf-8"',
]


def is_already_patched(filepath):
    """Quick check: does the file contain UTF-8 encoding args?"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        for indicator in PATCHED_INDICATORS:
            if indicator in content:
                return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    py_scripts = get_py_scripts_dir()
    version_string = get_3de_version_string()
    version_ok = is_supported_3de_version(version_string)

    log = []

    # --- Unsupported version warning ---
    version_warning = ""
    if not version_ok:
        version_warning = (
            "\n"
            "WARNING:\n"
            "\n"
            "This backup tool was designed for\n"
            "3DEqualizer4 Release 8.1.\n"
            "\n"
            "Detected version:\n"
            "  %s\n"
            "\n"
            "Proceed only if you understand that\n"
            "this tool backs up known R8.1 exporter\n"
            "patch targets.\n"
        ) % version_string

    # --- Confirmation dialog ---
    confirm_text = (
        "This script will create .encoding_backup files\n"
        "for known UTF-8 patch target exporter scripts.\n"
        "\n"
        "It does NOT:\n"
        "  - apply any patch\n"
        "  - move export_blender.py\n"
        "  - delete any file\n"
        "  - replace existing backups\n"
        "\n"
        "Use this if you want to create local backups\n"
        "before running Fix_Exporters_UTF8.py.\n"
        "\n"
        "This is NOT a replacement for a full external\n"
        "backup of your 3DEqualizer4 installation.\n"
        "\n"
        "Detected 3DE version:\n"
        "  %s"
        "%s"
        "\n"
        "Click Proceed to create missing backups.\n"
        "Click Cancel to do nothing."
    ) % (version_string, version_warning)

    result = tde4.postQuestionRequester(
        "Backup UTF-8 Patch Targets",
        confirm_text,
        "Proceed", "Cancel",
    )

    if result != 1:
        log.append("[ABORT] User cancelled - no files were created.")
        tde4.postQuestionRequester(
            "Backup - Cancelled",
            "No files were created.",
            "Ok",
        )
        return

    # --- Execute ---
    created = 0
    skipped_existing = 0
    skipped_patched = 0
    errors = 0

    for fname in BACKUP_TARGETS:
        target_path = os.path.join(py_scripts, fname)
        backup_path = target_path + ".encoding_backup"

        # File must exist
        if not os.path.isfile(target_path):
            log.append("[ERROR] Missing target file: %s" % fname)
            errors += 1
            continue

        # Backup already exists
        if os.path.isfile(backup_path):
            log.append("[SKIP] Backup already exists: %s.encoding_backup" % fname)
            skipped_existing += 1
            continue

        # File appears already patched - don't back up patched content
        if is_already_patched(target_path):
            log.append("[WARN] File appears already patched; backup not created: %s"
                       % fname)
            log.append("       Creating a backup now would save patched content,")
            log.append("       not original content.")
            skipped_patched += 1
            continue

        # Safe to back up
        try:
            shutil.copy2(target_path, backup_path)
            log.append("[OK] Created backup: %s.encoding_backup" % fname)
            created += 1
        except Exception as e:
            log.append("[ERROR] Failed to create backup for %s: %s" % (fname, str(e)))
            errors += 1

    # --- Full report to console ---
    full_lines = []
    full_lines.append("=" * 60)
    full_lines.append("Backup UTF-8 Patch Targets - Full Report")
    full_lines.append("=" * 60)
    full_lines.append("")
    full_lines.append("Detected 3DE version: %s" % version_string)
    full_lines.append("")
    full_lines.extend(log)
    full_lines.append("")
    full_lines.append("=" * 60)
    full_lines.append("This is not a replacement for a full external backup")
    full_lines.append("of your 3DEqualizer4 installation folder.")
    full_lines.append("=" * 60)

    full_report = "\n".join(full_lines)
    print(full_report)

    # --- Short popup summary ---
    popup = (
        "Backup complete.\n"
        "\n"
        "Created:\n"
        "  %d\n"
        "\n"
        "Skipped:\n"
        "  %d\n"
        "\n"
        "Warnings:\n"
        "  %d\n"
        "\n"
        "Errors:\n"
        "  %d\n"
        "\n"
        "Full details were printed to the 3DE Python console."
    ) % (created, skipped_existing + skipped_patched, skipped_patched, errors)

    tde4.postQuestionRequester(
        "Backup UTF-8 Patch Targets - Done",
        popup,
        "Ok",
    )


if __name__ == "__main__":
    main()
