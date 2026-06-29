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
# Script discovery
# ---------------------------------------------------------------------------
def get_manager_dir():
    """Directory containing this manager script."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


TOOL_SCRIPTS = {
    "scan":     "Scan_Exporters_UTF8_Status.py",
    "backup":   "Backup_UTF8_Patch_Targets.py",
    "fix":      "Fix_Exporters_UTF8.py",
    "rollback": "Rollback_UTF8_Patches.py",
    "cleanup":  "Cleanup_UTF8_Backups.py",
}


def get_script_path(name):
    """Return the full path to a tool script, or None if not found."""
    fname = TOOL_SCRIPTS.get(name)
    if fname is None:
        return None
    return os.path.join(get_manager_dir(), fname)


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
    script_path = get_script_path(name)
    fname = TOOL_SCRIPTS.get(name, name)

    if script_path is None or not os.path.isfile(script_path):
        tde4.postQuestionRequester(
            "Manager - Error",
            "Tool script not found:\n"
            "  %s\n"
            "\n"
            "Please verify the repository files are complete."
            % fname,
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

    while True:
        result = tde4.postQuestionRequester(
            "UTF-8 Patch Manager",
            "UTF-8 Patch Manager\n"
            "\n"
            "Detected 3DE version:\n"
            "  %s\n"
            "\n"
            "Choose an action group.\n"
            "\n"
            "Recommended workflow:\n"
            "  Scan -> Backup -> Fix -> Scan\n"
            "\n"
            "This manager only launches existing tools.\n"
            "Each tool keeps its own confirmation dialog."
            % version_string,
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
