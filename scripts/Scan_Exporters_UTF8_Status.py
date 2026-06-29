#
#
# 3DE4.script.name: Scan Exporters UTF-8 Patch Status
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Read-only scanner for the 3DE4 R8.1 Windows UTF-8
# 3DE4.script.comment: exporter patches.  Does not modify files.
#

"""
Scan_Exporters_UTF8_Status.py
=============================
Read-only diagnostic scanner.  Reports:

  - detected 3DE version and patch compatibility
  - Blender legacy script status (active / disabled / missing)
  - patch status for each exporter (PATCHED / UNPATCHED / PARTIAL / UNKNOWN)
  - backup file (.encoding_backup) presence
  - summary with recommended action

This script does NOT modify any files.
"""

import os
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
# Status table (mirrors PATCH_TABLE from Fix_Exporters_UTF8.py, read-only)
# ---------------------------------------------------------------------------
STATUS_TABLE = [
    # --- exportBlender.py ---
    {
        "file": "exportBlender.py",
        "label": "Blender: exportBlender.py",
        "entries": [
            {
                "comment": "getScriptVersion() line 98 - reads own script header",
                "patched_patterns": [
                    "open(os.sep.join([dirname, fname]), 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(os.sep.join([dirname, fname]), 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "_preferences_editor() line 1014 - reads user prefs",
                "patched_patterns": [
                    "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(preferences_file, 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "read_preferences_file() line 1249 - reads user prefs",
                "patched_patterns": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "main() line 3834 - reads log file",
                "patched_patterns": [
                    "open(log, 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(log, 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "main() lines 3749,3862,3881 - re-executes self (x3)",
                "patched_patterns": [
                    "open(script_path, encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "exec(open(script_path).read())",
                ],
                "expected_count": 3,
            },
        ],
    },

    # --- export_maya.py ---
    {
        "file": "export_maya.py",
        "label": "Maya: export_maya.py",
        "entries": [
            {
                "comment": "read_preferences_file() line 2309 - reads user prefs",
                "patched_patterns": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(os.sep.join([preferences_dir, file_name]), 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "_preferences_editor() line 2655 - reads user prefs",
                "patched_patterns": [
                    "open(preferences_file, 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(preferences_file, 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "main() line 3112 - reads log file",
                "patched_patterns": [
                    "open(log, 'r', encoding='utf-8', errors='replace')",
                ],
                "original_patterns": [
                    "open(log, 'r')",
                ],
                "expected_count": 1,
            },
            {
                "comment": "main() lines 3031,3140,3158 - re-executes self (x3); "
                           "real R8.1 Maya source uses with-open-as-f",
                "patched_patterns": [
                    'with open(script_path, "r", encoding="utf-8", errors="replace") as f:',
                ],
                "original_patterns": [
                    'with open(script_path) as f:',
                ],
                "expected_count": 3,
            },
        ],
    },

    # --- calcMainCameraViaPiggybackCamera.py ---
    {
        "file": "calcMainCameraViaPiggybackCamera.py",
        "label": "Piggyback: calcMainCameraViaPiggybackCamera.py",
        "entries": [
            {
                "comment": "importCalibration() line 1134 - user calibration data",
                "patched_patterns": [
                    'open(path,"r", encoding=\'utf-8\')',
                ],
                "original_patterns": [
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                    'open(path,"r")',
                ],
                "expected_count": 1,
            },
        ],
    },

    # --- export_flame_LD_3DE4_batch.py ---
    {
        "file": "export_flame_LD_3DE4_batch.py",
        "label": "Flame: export_flame_LD_3DE4_batch.py",
        "entries": [
            {
                "comment": "create_resize_node_add_margin/remove_margin/root_node lines 813,829,845 - XML template",
                "patched_patterns": [
                    'open(path,"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "original_patterns": [
                    'open(path,"r")',
                ],
                "expected_count": 3,
            },
            {
                "comment": "batch export line 862 - batch template",
                "patched_patterns": [
                    'open(os.path.join(self._tde4_flame_path,"pipeline.batch.template.xml"),"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "original_patterns": [
                    'open(os.path.join(self._tde4_flame_path,"pipeline.batch.template.xml"),"r")',
                ],
                "expected_count": 1,
            },
            {
                "comment": "fingerprint check line 1038 - fingerprint file",
                "patched_patterns": [
                    'open(os.path.join(path,"fingerprint"),"r", encoding=\'utf-8\', errors=\'replace\')',
                ],
                "original_patterns": [
                    'open(os.path.join(path,"fingerprint"),"r")',
                ],
                "expected_count": 1,
            },
        ],
    },
]

# Files expected to have patches applied
TARGET_FILES = [
    "exportBlender.py",
    "export_maya.py",
    "calcMainCameraViaPiggybackCamera.py",
    "export_flame_LD_3DE4_batch.py",
]


# ---------------------------------------------------------------------------
# Scanner logic
# ---------------------------------------------------------------------------
def scan_blender_legacy(py_scripts):
    """Check Blender legacy script status.  Returns list of report lines."""
    lines = []
    active = os.path.join(py_scripts, "export_blender.py")
    disabled = os.path.join(get_disabled_dir(), "export_blender.py.bak")
    legacy_bak = os.path.join(py_scripts, "export_blender.py.bak")

    has_active = os.path.isfile(active)
    has_disabled = os.path.isfile(disabled)
    has_legacy = os.path.isfile(legacy_bak)

    if has_disabled and not has_active:
        lines.append("[OK] Blender legacy script disabled - py_scripts_disabled/export_blender.py.bak exists")
    elif has_active and not has_disabled:
        lines.append("[WARN] Blender legacy script still active - py_scripts/export_blender.py exists")
        lines.append("       Blender exporter menu collision may still exist.")
    elif has_active and has_disabled:
        lines.append("[WARN] Both active and disabled legacy Blender scripts exist.")
        lines.append("       Please verify manually.")
    else:
        lines.append("[SKIP] No legacy export_blender.py found (active or disabled).")

    if has_legacy:
        lines.append("[INFO] Legacy in-place backup found - py_scripts/export_blender.py.bak exists")

    return lines


def scan_file_existence(py_scripts):
    """Check that all four target files exist.  Returns list of report lines."""
    lines = []
    for fname in TARGET_FILES:
        path = os.path.join(py_scripts, fname)
        if not os.path.isfile(path):
            lines.append("[ERROR] Missing file: %s" % fname)
    if not lines:
        lines.append("[OK] All 4 target exporter files present.")
    return lines


def scan_patch_points(py_scripts):
    """Check each patch point.  Returns (lines, summary_counts)."""
    lines = []
    total_patched = 0
    total_unpatched = 0
    total_partial = 0
    total_unknown = 0
    total_entries = 0

    for group in STATUS_TABLE:
        fname = group["file"]
        label = group["label"]
        path = os.path.join(py_scripts, fname)

        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        for entry in group["entries"]:
            comment = entry["comment"]
            expected = entry.get("expected_count", 1)
            total_entries += 1

            # Count patched patterns
            patched_count = 0
            for pp in entry["patched_patterns"]:
                patched_count += content.count(pp)

            # Count original (unpatched) patterns
            original_count = 0
            for op in entry["original_patterns"]:
                original_count += content.count(op)

            # --- Classification ---
            # IMPORTANT: patched_count takes priority.  Do NOT check
            # original_count == 0 as a gate for PATCHED — the original
            # snippet is often a substring of the patched version
            # (e.g. open(path,"r") inside open(path,"r", encoding=...)).
            if patched_count >= expected:
                lines.append("[PATCHED] %s - %s (%d/%d)"
                             % (label, comment, patched_count, expected))
                total_patched += 1
            elif patched_count > 0:
                # patched_count < expected — some patched, some not
                if original_count > 0:
                    lines.append("[PARTIAL] %s - %s (patched %d, original %d, expected %d)"
                                 % (label, comment, patched_count, original_count, expected))
                else:
                    lines.append("[PARTIAL] %s - %s (patched %d, expected %d)"
                                 % (label, comment, patched_count, expected))
                total_partial += 1
            elif original_count > 0:
                lines.append("[UNPATCHED] %s - %s (original %d, expected %d)"
                             % (label, comment, original_count, expected))
                total_unpatched += 1
            else:
                lines.append("[UNKNOWN] %s - %s (no patterns matched)"
                             % (label, comment))
                total_unknown += 1

    counts = {
        "patched": total_patched,
        "unpatched": total_unpatched,
        "partial": total_partial,
        "unknown": total_unknown,
        "total_entries": total_entries,
    }
    return lines, counts


def scan_backups(py_scripts):
    """Check for .encoding_backup files.  Returns list of report lines."""
    lines = []
    found = 0
    for fname in TARGET_FILES:
        bak = os.path.join(py_scripts, fname + ".encoding_backup")
        if os.path.isfile(bak):
            lines.append("[INFO] Backup exists: %s.encoding_backup" % fname)
            found += 1
        else:
            lines.append("[INFO] Backup missing: %s.encoding_backup" % fname)
    if found == 0:
        lines.append("       (Missing backups are normal if no files were modified.)")
    return lines, found


def build_full_report(version_string, compat_label, blender_lines, existence_lines,
                      patch_lines, backup_lines, summary_text):
    """Assemble the complete detailed report for console output."""
    lines = []
    lines.append("=" * 60)
    lines.append("Scan Exporters UTF-8 Patch Status")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Detected 3DE version:")
    lines.append("  %s" % version_string)
    lines.append("")
    lines.append("Patch compatibility:")
    lines.append("  %s" % compat_label)
    lines.append("")
    lines.append("Note: this scanner is read-only.")
    lines.append("The patcher should only be applied to 3DEqualizer4 Release 8.1.")
    lines.append("")
    lines.append("-" * 60)
    lines.append("Blender Legacy Script Status:")
    lines.extend(blender_lines)
    lines.append("")
    lines.append("-" * 60)
    lines.append("Target File Existence:")
    lines.extend(existence_lines)
    lines.append("")
    lines.append("-" * 60)
    lines.append("Patch Point Status:")
    lines.extend(patch_lines)
    lines.append("")
    lines.append("-" * 60)
    lines.append("Backup File Status:")
    lines.extend(backup_lines)
    lines.append("")
    lines.append("-" * 60)
    lines.append(summary_text)
    lines.append("=" * 60)
    return "\n".join(lines)


def build_short_summary(version_string, version_ok, blender_status_short, patch_status_short,
                        patch_counts, backup_count, existence_errors, issue_count):
    """Build an ultra-compact popup summary (max ~12 lines for requester)."""
    compat = "SUPPORTED" if version_ok else ("UNSUPPORTED" if version_string != "UNKNOWN" else "UNKNOWN")

    if issue_count > 0:
        footer = "Check console details."
    elif patch_status_short == "FULLY PATCHED":
        footer = "No action needed."
    else:
        footer = "Check console details."

    total = patch_counts.get("total_entries", 0)
    patched = patch_counts.get("patched", 0)

    return (
        "Scan complete.\n"
        "\n"
        "Version: %s\n"
        "Compatibility: %s\n"
        "Blender legacy: %s\n"
        "Patch status: %s\n"
        "Patch points: %d/%d patched\n"
        "Issues: %d\n"
        "Backup files: %d\n"
        "Missing files: %d\n"
        "\n"
        "%s\n"
        "\n"
        "Details printed to console."
    ) % (
        version_string,
        compat,
        blender_status_short,
        patch_status_short,
        patched, total,
        issue_count,
        backup_count,
        existence_errors,
        footer,
    )


def _classify_patch_status(patch_counts, existence_errors):
    """Return a status label from patch point counts."""
    pc = patch_counts
    total = pc.get("total_entries", 0)
    if pc["patched"] == total and pc["unpatched"] == 0 and pc["partial"] == 0 and pc["unknown"] == 0:
        return "FULLY PATCHED"
    if pc["patched"] == 0 and pc["unpatched"] > 0 and pc["partial"] == 0 and pc["unknown"] == 0:
        return "NOT PATCHED"
    if pc["patched"] > 0 and (pc["unpatched"] > 0 or pc["partial"] > 0):
        return "PARTIALLY PATCHED"
    if pc["unknown"] > 0 or existence_errors > 0:
        return "NEEDS REVIEW"
    return "UNKNOWN"


def build_summary(version_string, version_ok, blender_lines, patch_counts,
                  backup_count, existence_errors):
    """Build the detailed summary block for the full console report."""
    compat = "SUPPORTED" if version_ok else ("UNSUPPORTED" if version_string != "UNKNOWN" else "UNKNOWN")

    pc = patch_counts
    total = pc.get("total_entries", 0)
    patch_status = _classify_patch_status(patch_counts, existence_errors)

    has_active_warn = any("still active" in l for l in blender_lines)
    has_disabled_ok = any("legacy script disabled" in l for l in blender_lines)
    if has_disabled_ok and not has_active_warn:
        blender_status = "YES (disabled)"
    elif has_active_warn:
        blender_status = "NO (active - collision risk)"
    else:
        blender_status = "UNKNOWN"

    if patch_status == "FULLY PATCHED" and blender_status.startswith("YES"):
        action = "No action needed. Your installation is fully patched."
    elif not version_ok:
        action = "Unsupported 3DE version. Do NOT run the patcher."
    elif patch_status == "NOT PATCHED":
        action = "Run Fix_Exporters_UTF8.py to apply the patch."
    elif patch_status == "PARTIALLY PATCHED" or patch_status == "NEEDS REVIEW":
        action = "Verify manually, or re-run Fix_Exporters_UTF8.py (idempotent)."
    else:
        action = "Run Fix_Exporters_UTF8.py if on R8.1. Use Rollback_UTF8_Patches.py to undo."

    totals = (
        "Patch point totals:\n"
        "  PATCHED: %d\n"
        "  UNPATCHED: %d\n"
        "  PARTIAL: %d\n"
        "  UNKNOWN: %d\n"
        "  TOTAL: %d"
    ) % (pc["patched"], pc["unpatched"], pc["partial"], pc["unknown"], total)

    return (
        "%s\n"
        "\n"
        "Summary:\n"
        "  3DE version: %s\n"
        "  Compatibility: %s\n"
        "  Blender legacy disabled: %s\n"
        "  Patch status: %s\n"
        "  Backup files found: %d\n"
        "  Missing files: %d\n"
        "\n"
        "Recommended action:\n"
        "  %s"
    ) % (
        totals,
        version_string,
        compat,
        blender_status,
        patch_status,
        backup_count,
        existence_errors,
        action,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    py_scripts = get_py_scripts_dir()

    version_string = get_3de_version_string()
    version_ok = is_supported_3de_version(version_string)
    compat_label = "SUPPORTED" if version_ok else ("UNSUPPORTED" if version_string != "UNKNOWN" else "UNKNOWN")

    # --- Blender legacy ---
    blender_lines = scan_blender_legacy(py_scripts)

    # --- File existence ---
    existence_lines = scan_file_existence(py_scripts)
    existence_errors = sum(1 for l in existence_lines if l.startswith("[ERROR]"))

    # --- Patch points ---
    if existence_errors == len(TARGET_FILES):
        patch_lines = ["[ERROR] All target files missing - cannot scan patch points."]
        patch_counts = {"patched": 0, "unpatched": 0, "partial": 0, "unknown": 0, "total_entries": 0}
    else:
        patch_lines, patch_counts = scan_patch_points(py_scripts)

    # --- Backups ---
    backup_lines, backup_count = scan_backups(py_scripts)

    # --- Determine short status labels ---
    has_active_warn = any("still active" in l for l in blender_lines)
    has_disabled_ok = any("legacy script disabled" in l for l in blender_lines)
    if has_disabled_ok and not has_active_warn:
        blender_status_short = "DISABLED"
    elif has_active_warn:
        blender_status_short = "ACTIVE (collision risk)"
    else:
        blender_status_short = "UNKNOWN"

    patch_status_short = _classify_patch_status(patch_counts, existence_errors)

    issue_count = (patch_counts["unpatched"] + patch_counts["partial"] + patch_counts["unknown"]
                   + existence_errors
                   + (1 if "still active" in " ".join(blender_lines) else 0))

    # --- Add backup warnings for console report ---
    if backup_count == 0:
        backup_lines.append("")
        backup_lines.append("WARNING:")
        backup_lines.append("  No local .encoding_backup files were found.")
        backup_lines.append("  Rollback cannot restore original exporter files")
        backup_lines.append("  without these backups.")
        backup_lines.append("")
        backup_lines.append("Optional:")
        backup_lines.append("  If you have not applied the patch yet, run")
        backup_lines.append("  Backup_UTF8_Patch_Targets.py to create local")
        backup_lines.append("  backups before patching.")
    else:
        backup_lines.append("")
        backup_lines.append("Local rollback backups are present.")

    # --- Build full report for console ---
    summary_text = build_summary(version_string, version_ok, blender_lines,
                                 patch_counts, backup_count, existence_errors)
    full_report = build_full_report(version_string, compat_label, blender_lines,
                                    existence_lines, patch_lines, backup_lines,
                                    summary_text)

    # --- Print full report to 3DE Python console ---
    print(full_report)

    # --- Show short summary in popup ---
    short_summary = build_short_summary(version_string, version_ok, blender_status_short,
                                        patch_status_short, patch_counts, backup_count,
                                        existence_errors, issue_count)

    tde4.postQuestionRequester(
        "Scan Exporters UTF-8 Status - Done",
        short_summary,
        "Ok",
    )


if __name__ == "__main__":
    main()
