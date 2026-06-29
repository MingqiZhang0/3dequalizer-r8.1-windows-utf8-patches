#
#
# 3DE4.script.name: UTF-8 Patch Manager
#
# 3DE4.script.version: v1.0
#
# 3DE4.script.toolkit.version: 0.5.0
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

# Optional manual override (last-resort fallback).
# Use this only if automatic search fails.  Example:
#   TOOLKIT_ROOT_OVERRIDE = r"E:\3DEqualizer4\3de_utf8_patch_toolkit"
TOOLKIT_ROOT_OVERRIDE = ""

TOOLKIT_VERSION = "0.5.0"

# Tool scripts live under this subdirectory.
SCRIPT_DIR_NAME = "scripts"

# These five files must all be present in root/scripts/ for a
# directory to be considered the new-layout toolkit root.
REQUIRED_TOOL_FILES = [
    os.path.join(SCRIPT_DIR_NAME, "Fix_Exporters_UTF8.py"),
    os.path.join(SCRIPT_DIR_NAME, "Backup_UTF8_Patch_Targets.py"),
    os.path.join(SCRIPT_DIR_NAME, "Scan_Exporters_UTF8_Status.py"),
    os.path.join(SCRIPT_DIR_NAME, "Rollback_UTF8_Patches.py"),
    os.path.join(SCRIPT_DIR_NAME, "Cleanup_UTF8_Backups.py"),
]

# The manager itself must also be present at the root.
MANAGER_FILE = "UTF8_Patch_Manager.py"

# Known toolkit folder names (checked under 3DE install dir and its parent).
COMMON_TOOLKIT_DIR_NAMES = [
    "Manual Patches",
    "manual patches",
    "Manual_Patches",
    "manual_patches",
    "3de_utf8_patch_toolkit",
    "3dequalizer-r8.1-windows-utf8-patches",
    "3dequalizer-r8.1-windows-utf8-patches-main",
    "3dequalizer-r8.1-windows-utf8-patches-master",
]

TOOL_SCRIPTS = {
    "scan":     os.path.join(SCRIPT_DIR_NAME, "Scan_Exporters_UTF8_Status.py"),
    "backup":   os.path.join(SCRIPT_DIR_NAME, "Backup_UTF8_Patch_Targets.py"),
    "fix":      os.path.join(SCRIPT_DIR_NAME, "Fix_Exporters_UTF8.py"),
    "rollback": os.path.join(SCRIPT_DIR_NAME, "Rollback_UTF8_Patches.py"),
    "cleanup":  os.path.join(SCRIPT_DIR_NAME, "Cleanup_UTF8_Backups.py"),
}


def is_toolkit_root(path):
    """
    Return True if *path* is a valid toolkit root.

    New layout (v0.4.0+): root contains UTF8_Patch_Manager.py
    and a scripts/ subdirectory with all five tool scripts.
    """
    if not path:
        return False
    try:
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        # Manager must be at root
        if not os.path.isfile(os.path.join(path, MANAGER_FILE)):
            return False
        # All five tool scripts must be in scripts/
        for name in REQUIRED_TOOL_FILES:
            if not os.path.isfile(os.path.join(path, name)):
                return False
        return True
    except Exception:
        return False


def _add_dir(result, path):
    """Add a path to the candidate list, deduplicating by normcase."""
    if not path:
        return
    try:
        ap = os.path.abspath(path)
        if not os.path.isdir(ap):
            return
        key = os.path.normcase(ap)
        if key not in result["_seen"]:
            result["_seen"].add(key)
            result["dirs"].append(ap)
    except Exception:
        pass


def _add_one_level_subdirs(result, base_dir):
    """
    Add all immediate subdirectories of *base_dir* as candidates.
    Only one level deep — does not recurse.
    Silently ignores permission errors and non-directories.
    """
    if not base_dir:
        return
    try:
        base_dir = os.path.abspath(base_dir)
        if not os.path.isdir(base_dir):
            return
        for name in os.listdir(base_dir):
            path = os.path.join(base_dir, name)
            if os.path.isdir(path):
                _add_dir(result, path)
    except Exception:
        pass


def collect_candidate_dirs():
    """
    Gather candidate directories to search for the toolkit root.

    Search sources (in priority order):
      1. TOOLKIT_ROOT_OVERRIDE
      2. __file__ directory
      3. os.getcwd()
      4. 3DE install path + common subdirectory names
      5. Parent of 3DE install path + common subdirectory names
      6. One-level subdirectories under trusted base dirs
      7. Parent directories of all current candidates (up to 4 levels)
    """
    result = {"dirs": [], "_seen": set()}
    add = lambda p: _add_dir(result, p)

    # 1. Manual override
    if TOOLKIT_ROOT_OVERRIDE.strip():
        add(TOOLKIT_ROOT_OVERRIDE.strip())

    # 2. __file__ directory
    file_dir = ""
    try:
        this_file = globals().get("__file__", "")
        if this_file:
            file_dir = os.path.dirname(os.path.abspath(this_file))
            add(file_dir)
    except Exception:
        pass

    # 3. Current working directory
    cwd = ""
    try:
        cwd = os.getcwd()
        add(cwd)
    except Exception:
        pass

    # 4 & 5. 3DE install path and its parent, with common subdirs
    install = ""
    try:
        install = tde4.get3DEInstallPath()
    except Exception:
        pass

    bases = []
    if install:
        try:
            bases.append(os.path.abspath(install))
            parent = os.path.dirname(os.path.abspath(install))
            if parent and parent != os.path.abspath(install):
                bases.append(parent)
        except Exception:
            pass

    for base in bases:
        add(base)
        for name in COMMON_TOOLKIT_DIR_NAMES:
            add(os.path.join(base, name))

    # 6. One-level subdirectories under trusted base dirs.
    #    This catches folders like "Manual Patches" that sit directly
    #    under the 3DE install path but are not in COMMON_TOOLKIT_DIR_NAMES.
    trusted_scan_bases = []
    if file_dir:
        trusted_scan_bases.append(file_dir)
    if cwd:
        trusted_scan_bases.append(cwd)
    for base in bases:
        trusted_scan_bases.append(base)

    for base in trusted_scan_bases:
        _add_one_level_subdirs(result, base)

    # 7. Parent directories of all current candidates (up to 4 levels)
    initial = list(result["dirs"])
    for c in initial:
        try:
            cur = os.path.abspath(c)
            for _ in range(4):
                add(cur)
                parent = os.path.dirname(cur)
                if parent == cur:
                    break
                cur = parent
        except Exception:
            pass

    return result["dirs"]


# Root resolution cache - avoid repeated console spam
_ROOT_CACHE = None
_CANDIDATES_CACHE = None
_ROOT_PRINTED = False


def _maybe_print_root(root):
    """Print the resolved root path once per script execution."""
    global _ROOT_PRINTED
    if not root or _ROOT_PRINTED:
        return
    print("[INFO] Toolkit root resolved:")
    print("       %s" % root)
    _ROOT_PRINTED = True


def resolve_toolkit_root(log_success=False):
    """
    Locate the repository root directory.

    Caches the result after first successful resolution.
    Set log_success=True to allow a one-time console print.

    Returns (root_path, checked_dirs) where root_path may be None.
    """
    global _ROOT_CACHE, _CANDIDATES_CACHE

    # Return cached result if we already resolved successfully.
    if _ROOT_CACHE is not None:
        if log_success:
            _maybe_print_root(_ROOT_CACHE)
        return _ROOT_CACHE, (_CANDIDATES_CACHE or [])

    candidates = collect_candidate_dirs()

    # If override is set but invalid, warn in console and continue search.
    override = TOOLKIT_ROOT_OVERRIDE.strip()
    if override:
        if is_toolkit_root(override):
            _ROOT_CACHE = os.path.abspath(override)
            _CANDIDATES_CACHE = candidates
            if log_success:
                _maybe_print_root(_ROOT_CACHE)
            return _ROOT_CACHE, candidates
        else:
            print("[WARN] TOOLKIT_ROOT_OVERRIDE is set but is not a valid toolkit root:")
            print("       %s" % override)
            print("       Continuing automatic search...")

    for c in candidates:
        if is_toolkit_root(c):
            _ROOT_CACHE = c
            _CANDIDATES_CACHE = candidates
            if log_success:
                _maybe_print_root(_ROOT_CACHE)
            return c, candidates

    # Don't cache failures - allow retry on next call
    _CANDIDATES_CACHE = candidates
    return None, candidates


# ---------------------------------------------------------------------------
# Root-not-found error
# ---------------------------------------------------------------------------
def show_root_not_found_error(script_name, candidates):
    try:
        install = tde4.get3DEInstallPath()
    except Exception:
        install = "<3DE install path>"

    lines = []
    lines.append("Toolkit root not found.")
    lines.append("")
    lines.append("The manager could not find all required")
    lines.append("tool scripts.")
    lines.append("")
    lines.append("Recommended fix:")
    lines.append("  Put the whole patch toolkit folder under")
    lines.append("  your 3DE install folder, for example:")
    lines.append("")
    lines.append("  %s\\Manual Patches\\" % install)
    lines.append("  or")
    lines.append("  %s\\3de_utf8_patch_toolkit\\" % install)
    lines.append("")
    lines.append("Alternative:")
    lines.append("  Edit TOOLKIT_ROOT_OVERRIDE at the top of")
    lines.append("  UTF8_Patch_Manager.py and set it to the")
    lines.append("  toolkit folder.")
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
    print("")
    print("Recommended layout:")
    print("  %s\\Manual Patches\\" % install)
    print("  or")
    print("  %s\\3de_utf8_patch_toolkit\\" % install)
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

    root_dir, candidates = resolve_toolkit_root(log_success=True)
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
        "Workflow: Scan -> Backup -> Fix -> Scan\n"
        "\n"
        "- Run inside 3DEqualizer4 only.\n"
        "- Tested only with 3DE4 Release 8.1 on Windows.\n"
        "- Full external backup required before patching.\n"
        "- Fix and Undo need restart afterwards.\n"
        "- Keep toolkit folder name unchanged.\n"
        "\n"
        "See README.md and docs/Potential_Risks.md.",
        "Ok",
    )


def menu_tools():
    """Second-level menu: Backup | Fix | More | Cancel  (4 buttons max)"""
    result = tde4.postQuestionRequester(
        "UTF-8 Patch Manager - Tools",
        "Choose a tool.\n"
        "\n"
        "Backup:\n"
        "  Create local backup files before patching.\n"
        "\n"
        "Fix:\n"
        "  Apply selected UTF-8 patches.\n"
        "\n"
        "More:\n"
        "  Undo, cleanup, and help.",
        "Backup", "Fix", "More", "Cancel",
    )

    if result == 1:
        run_tool_script("backup")
    elif result == 2:
        run_tool_script("fix")
    elif result == 3:
        menu_more()
    # result == 4 or anything else: Cancel -> back to main


def menu_more():
    """Third-level menu: Undo | Cleanup | Help | Back  (4 buttons max)"""
    result = tde4.postQuestionRequester(
        "UTF-8 Patch Manager - More",
        "Undo:\n"
        "  Roll back from local backups if available.\n"
        "\n"
        "Cleanup:\n"
        "  Delete known .encoding_backup files.\n"
        "  Use only after verification and external\n"
        "  backup.",
        "Undo", "Cleanup", "Help", "Back",
    )

    if result == 1:
        run_tool_script("rollback")
    elif result == 2:
        run_tool_script("cleanup")
    elif result == 3:
        show_help()
    # result == 4 or anything else: Back -> Tools menu


def main():
    version_string = get_3de_version_string()
    root_dir, _ = resolve_toolkit_root()
    root_status = "FOUND" if root_dir else "NOT FOUND"

    while True:
        result = tde4.postQuestionRequester(
            "UTF-8 Patch Manager",
            "UTF-8 Patch Manager v%s\n"
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
            % (TOOLKIT_VERSION, version_string, root_status),
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
