#
#
# 3DE4.script.name: UTF-8 Patch Manager
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Unified launcher for the 3DE4 R8.1 Windows UTF-8 patch toolkit.
# 3DE4.script.comment: Runs existing tools without duplicating patch logic.
#

"""
UTF8_Patch_Manager.py
=====================
Unified menu-based launcher for the 3DE4 R8.1 UTF-8 patch toolkit.

Does not duplicate, rewrite, or inline any tool logic.
Each tool runs as its own script and keeps its own safety
confirmation dialogs.

Menu structure:
  Main Menu  -> Scan | Tools | Help | Cancel
  Tools      -> Backup | Fix | Rollback | More | Cancel
  More       -> Cleanup | Help | Back | Cancel
"""

import os
import sys
import traceback
import tde4


# ---------------------------------------------------------------------------
# Version detection (informational -- does not enforce guard here;
# each sub-script has its own version checks)
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


# ---------------------------------------------------------------------------
# Toolkit root resolution
# ---------------------------------------------------------------------------

# Optional manual override.
# When 3DE does not provide a reliable __file__ for Run Script, set this
# to the repository root directory.  Example:
#   TOOLKIT_ROOT_OVERRIDE = r"E:\path\to\3dequalizer-r8.1-windows-utf8-patches"
TOOLKIT_ROOT_OVERRIDE = ""

# These five files must all be present for a directory to be considered
# the toolkit root.
REQUIRED_TOOL_FILES = [
    "Fix_Exporters_UTF8.py",
    "Backup_UTF8_Patch_Targets.py",
    "Scan_Exporters_UTF8_Status.py",
    "Rollback_UTF8_Patches.py",
    "Cleanup_UTF8_Backups.py",
]

TOOL_SCRIPTS = {
    "scan":     "Scan_Exporters_UTF8_Status.py",
    "backup":   "Backup_UTF8_Patch_Targets.py",
    "fix":      "Fix_Exporters_UTF8.py",
    "rollback": "Rollback_UTF8_Patches.py",
    "cleanup":  "Cleanup_UTF8_Backups.py",
}


def is_toolkit_root(path):
    """Return True if *path* contains all five required tool scripts."""
    if not path:
        return False
    try:
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        for name in REQUIRED_TOOL_FILES:
            if not os.path.isfile(os.path.join(path, name)):
                return False
        return True
    except Exception:
        return False


def unique_existing_dirs(paths):
    """Deduplicate and filter a list of paths to existing directories."""
    result = []
    seen = set()
    for p in paths:
        if not p:
            continue
        try:
            ap = os.path.abspath(p)
        except Exception:
            continue
        key = os.path.normcase(ap)
        if key in seen:
            continue
        seen.add(key)
        if os.path.isdir(ap):
            result.append(ap)
    return result


def resolve_toolkit_root():
    """
    Try to locate the repository root directory.

    Search order:
      1. TOOLKIT_ROOT_OVERRIDE (manual, highest priority)
      2. Directory of __file__ (if reliable)
      3. Current working directory
      4. Parent directories of all candidates (up to 4 levels)

    Returns (root_path, checked_dirs) where root_path may be None.
    """
    candidates = []

    # 1. Manual override first.
    if TOOLKIT_ROOT_OVERRIDE.strip():
        candidates.append(TOOLKIT_ROOT_OVERRIDE.strip())

    # 2. Directory of __file__, if available.
    try:
        this_file = globals().get("__file__", "")
        if this_file:
            candidates.append(os.path.dirname(os.path.abspath(this_file)))
    except Exception:
        pass

    # 3. Current working directory.
    try:
        candidates.append(os.getcwd())
    except Exception:
        pass

    # 4. Parent directories of every candidate.
    expanded = []
    for c in candidates:
        if not c:
            continue
        try:
            cur = os.path.abspath(c)
            for _ in range(4):
                expanded.append(cur)
                parent = os.path.dirname(cur)
                if parent == cur:
                    break
                cur = parent
        except Exception:
            pass

    checked = unique_existing_dirs(candidates + expanded)

    for c in checked:
        if is_toolkit_root(c):
            return c, checked

    return None, checked


# ---------------------------------------------------------------------------
# Root-not-found error
# ---------------------------------------------------------------------------
def show_root_not_found_error(script_name, candidates):
    lines = []
    lines.append("Toolkit root not found.")
    lines.append("")
    lines.append("Could not locate:")
    lines.append("  %s" % script_name)
    lines.append("")
    lines.append("The manager could not find all required")
    lines.append("tool scripts.")
    lines.append("")
    lines.append("Fix:")
    lines.append("  Open UTF8_Patch_Manager.py")
    lines.append("  Set TOOLKIT_ROOT_OVERRIDE to this")
    lines.append("  repository folder.")
    lines.append("")
    lines.append("Example:")
    lines.append('  TOOLKIT_ROOT_OVERRIDE = r"E:\\path\\to\\repo"')
    lines.append("")
    lines.append("Checked directories were printed to console.")

    print("=" * 60)
    print("UTF-8 Patch Manager - root resolution failed")
    print("=" * 60)
    print("Requested tool: %s" % script_name)
    print("")
    print("Checked directories:")
    for c in candidates:
        print("  %s" % c)
    print("")
    print("Required files:")
    for name in REQUIRED_TOOL_FILES:
        print("  %s" % name)
    print("=" * 60)

    tde4.postQuestionRequester(
        "UTF-8 Patch Manager - Root Not Found",
        "\n".join(lines),
        "Ok",
    )


# ---------------------------------------------------------------------------
# Sub-script runner
# ---------------------------------------------------------------------------
def run_tool_script(name):
    """
    Execute a named tool script in its own namespace.
    The sub-script's `if __name__ == "__main__": main()` will fire.

    Returns True if the script ran without unhandled exceptions,
    False if an error occurred.
    """
    fname = TOOL_SCRIPTS.get(name, name)

    root_dir, candidates = resolve_toolkit_root()
    if not root_dir:
        show_root_not_found_error(fname, candidates)
        return False

    script_path = os.path.join(root_dir, fname)

    if not os.path.isfile(script_path):
        tde4.postQuestionRequester(
            "Manager - Error",
            "Tool script not found:\n"
            "  %s\n"
            "\n"
            "Expected at:\n"
            "  %s\n"
            "\n"
            "Please verify the repository files are complete."
            % (fname, script_path),
            "Ok",
        )
        return False

    try:
        with open(script_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except Exception as e:
        tde4.postQuestionRequester(
            "Manager - Error",
            "Failed to read tool script:\n"
            "  %s\n"
            "\n"
            "Error: %s" % (fname, str(e)),
            "Ok",
        )
        return False

    namespace = {
        "__name__": "__main__",
        "__file__": script_path,
    }

    try:
        code = compile(source, script_path, "exec")
        exec(code, namespace)
        return True
    except Exception:
        print("=" * 60)
        print("Manager: error running %s" % fname)
        print("-" * 60)
        traceback.print_exc()
        print("=" * 60)

        tde4.postQuestionRequester(
            "Manager - Error",
            "Failed to run tool:\n"
            "  %s\n"
            "\n"
            "Full traceback was printed to the 3DE Python console."
            % fname,
            "Ok",
        )
        return False


# ---------------------------------------------------------------------------
# Menu screens
# ---------------------------------------------------------------------------
def show_help():
    tde4.postQuestionRequester(
        "UTF-8 Patch Manager - Help",
        "Recommended workflow:\n"
        "\n"
        "  Scan -> Backup -> Fix -> Scan\n"
        "\n"
        "Important notes:\n"
        "\n"
        "- Run inside 3DEqualizer4 only.\n"
        "- Tested only with 3DEqualizer4 Release 8.1\n"
        "  on Windows.\n"
        "- Always make a full external backup of your\n"
        "  3DE installation before patching.\n"
        "- Backup tool is most useful before patching.\n"
        "- Rollback needs .encoding_backup files to\n"
        "  restore exporter source files.\n"
        "- Cleanup deletes local .encoding_backup files\n"
        "  and reduces rollback ability.\n"
        "- After Fix or Rollback, fully restart\n"
        "  3DEqualizer4.\n"
        "\n"
        "If the manager cannot find tool scripts,\n"
        "edit TOOLKIT_ROOT_OVERRIDE at the top of\n"
        "UTF8_Patch_Manager.py and set it to this\n"
        "repository folder.\n"
        "\n"
        "See README.md and docs/Potential_Risks.md\n"
        "for details.",
        "Ok",
    )


def menu_tools():
    """Second-level menu: Backup | Fix | Rollback | More | Cancel"""
    result = tde4.postQuestionRequester(
        "UTF-8 Patch Manager - Tools",
        "Choose a tool to run.\n"
        "\n"
        "Backup:\n"
        "  Create local .encoding_backup files before\n"
        "  patching.\n"
        "\n"
        "Fix:\n"
        "  Apply the UTF-8 exporter patch.\n"
        "\n"
        "Rollback:\n"
        "  Restore from local backups when available.\n"
        "\n"
        "More:\n"
        "  Additional tools and help.",
        "Backup", "Fix", "Rollback", "More", "Cancel",
    )

    if result == 1:
        run_tool_script("backup")
    elif result == 2:
        run_tool_script("fix")
    elif result == 3:
        run_tool_script("rollback")
    elif result == 4:
        menu_more()
    # result == 5 or anything else: Cancel -> back to main


def menu_more():
    """Third-level menu: Cleanup | Help | Back | Cancel"""
    result = tde4.postQuestionRequester(
        "UTF-8 Patch Manager - More Tools",
        "Additional tools.\n"
        "\n"
        "Cleanup:\n"
        "  Delete known .encoding_backup files.\n"
        "  This reduces local rollback ability.\n"
        "  Use only after verification and external\n"
        "  backup.\n"
        "\n"
        "Help:\n"
        "  Show safety notes.",
        "Cleanup", "Help", "Back", "Cancel",
    )

    if result == 1:
        run_tool_script("cleanup")
    elif result == 2:
        show_help()
    elif result == 3:
        return  # back to Tools menu
    # result == 4 or anything else: Cancel -> back to main


def main():
    version_string = get_3de_version_string()
    root_dir, _ = resolve_toolkit_root()
    root_status = "FOUND" if root_dir else "NOT FOUND"

    while True:
        result = tde4.postQuestionRequester(
            "UTF-8 Patch Manager",
            "UTF-8 Patch Manager\n"
            "\n"
            "Detected 3DE version:\n"
            "  %s\n"
            "\n"
            "Toolkit root:\n"
            "  %s\n"
            "\n"
            "Choose an action group.\n"
            "\n"
            "Recommended workflow:\n"
            "  Scan -> Backup -> Fix -> Scan\n"
            "\n"
            "This manager only launches existing tools.\n"
            "Each tool keeps its own confirmation dialog."
            % (version_string, root_status),
            "Scan", "Tools", "Help", "Cancel",
        )

        if result == 1:
            run_tool_script("scan")
        elif result == 2:
            menu_tools()
        elif result == 3:
            show_help()
        else:
            # Cancel or anything else
            break


if __name__ == "__main__":
    main()
