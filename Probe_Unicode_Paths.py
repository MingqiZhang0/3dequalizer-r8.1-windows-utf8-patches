#
#
# 3DE4.script.name: Probe Unicode Paths
#
# 3DE4.script.version: v0.1
#
# 3DE4.script.gui: Main Window::Python
#
# 3DE4.script.comment: Read-only diagnostic probe for Unicode path handling in 3DE4 R8.1.
#

"""
Probe_Unicode_Paths.py
======================
Read-only diagnostic tool for investigating Chinese / Unicode path
handling in 3DEqualizer4 R8.1 on Windows.

Does NOT create, modify, move, or delete any files.

Reports:
  - Python runtime encoding settings
  - Path existence and accessibility for a test Unicode path
  - tde4 requester API availability
  - Optional native file requester test
  - Diagnostic classification (Case A/B/C/D)
"""

import os
import sys
import locale
import tde4


# ---------------------------------------------------------------------------
# Fallback test path.
# Normally, run the probe and select a folder or file interactively.
# Set this only if 3DE requesters are unavailable.
# Example:
#   TEST_UNICODE_PATH = r"F:\测试目录"
# ---------------------------------------------------------------------------
TEST_UNICODE_PATH = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_3de_version_string():
    try:
        if hasattr(tde4, "get3DEVersion"):
            v = tde4.get3DEVersion()
            if isinstance(v, str) and v.strip():
                return v.strip()
    except Exception:
        pass
    return "UNKNOWN"


def safe_repr(s):
    """repr() that won't crash on encoding issues."""
    try:
        return repr(s)
    except Exception:
        return "<repr failed>"


def has_mojibake(s):
    """Heuristic: check if string contains common mojibake indicators."""
    if not s:
        return False
    markers = [
        "�",   # Unicode replacement character
        "\x00",     # null byte (truncation)
        "?",        # common replacement (weak signal)
    ]
    for m in markers[:2]:  # only check strong signals
        if m in s:
            return True
    # Check for lone surrogates
    try:
        s.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return True
    return False


# ---------------------------------------------------------------------------
# Probe functions
# ---------------------------------------------------------------------------
def probe_environment():
    """Collect Python / 3DE environment info."""
    lines = []
    lines.append("-" * 60)
    lines.append("Environment")
    lines.append("-" * 60)
    lines.append("Python version:      %s" % sys.version.replace("\n", " "))
    lines.append("sys.defaultencoding:  %s" % safe_repr(sys.getdefaultencoding()))
    lines.append("sys.filesystemencoding: %s" % safe_repr(sys.getfilesystemencoding()))
    lines.append("locale.preferred:     %s" % safe_repr(locale.getpreferredencoding(False)))
    try:
        lines.append("os.getcwd():          %s" % safe_repr(os.getcwd()))
    except Exception:
        lines.append("os.getcwd():          <error>")
    lines.append("3DE version:          %s" % get_3de_version_string())
    try:
        lines.append("3DE install path:     %s" % safe_repr(tde4.get3DEInstallPath()))
    except Exception:
        lines.append("3DE install path:     <error>")
    return lines


def probe_path(test_path):
    """Test a single Unicode path for filesystem accessibility."""
    lines = []
    lines.append("-" * 60)
    lines.append("Path Test")
    lines.append("-" * 60)
    lines.append("Input:            %s" % safe_repr(test_path))

    if not test_path:
        lines.append("(no test path selected)")
        lines.append("")
        lines.append("To test a Chinese folder:")
        lines.append("  run the probe again and choose File mode,")
        lines.append("  then select any file inside the target folder.")
        lines.append("")
        lines.append("TEST_UNICODE_PATH is only a fallback.")
        return lines

    # Existence
    try:
        exists = os.path.exists(test_path)
    except Exception as e:
        exists = "<error: %s>" % str(e)
    lines.append("os.path.exists:   %s" % exists)

    try:
        isdir = os.path.isdir(test_path)
    except Exception as e:
        isdir = "<error: %s>" % str(e)
    lines.append("os.path.isdir:    %s" % isdir)

    # Absolute path
    try:
        abspath = os.path.abspath(test_path)
        lines.append("os.path.abspath:  %s" % safe_repr(abspath))
    except Exception as e:
        lines.append("os.path.abspath:  <error: %s>" % str(e))

    try:
        basename = os.path.basename(test_path)
        lines.append("basename:         %s" % safe_repr(basename))
    except Exception as e:
        lines.append("basename:         <error: %s>" % str(e))

    # Mojibake check
    if has_mojibake(test_path):
        lines.append("WARNING: path contains mojibake indicators")
    try:
        ab = os.path.abspath(test_path)
        if has_mojibake(ab):
            lines.append("WARNING: abspath contains mojibake indicators")
    except Exception:
        pass

    # Parent dir listdir
    try:
        parent = os.path.dirname(os.path.abspath(test_path))
        if parent and os.path.isdir(parent):
            entries = os.listdir(parent)
            lines.append("")
            lines.append("Parent dir:       %s" % safe_repr(parent))
            lines.append("listdir count:    %d" % len(entries))
            bn = os.path.basename(test_path)
            found = bn in entries
            lines.append("basename in listdir: %s" % found)
            lines.append("")
            lines.append("First 20 entries (repr):")
            for e in entries[:20]:
                lines.append("  %s" % safe_repr(e))
            if len(entries) > 20:
                lines.append("  ... (%d more)" % (len(entries) - 20))
    except Exception as e:
        lines.append("listdir test:     <error: %s>" % str(e))

    # Subdir listing (if test_path is a directory)
    if isinstance(isdir, bool) and isdir:
        try:
            sub = os.listdir(test_path)
            lines.append("")
            lines.append("Subdir entries:   %d" % len(sub))
            for s in sub[:20]:
                lines.append("  %s" % safe_repr(s))
            if len(sub) > 20:
                lines.append("  ... (%d more)" % (len(sub) - 20))
            # Try reading a .txt file if present
            for s in sub:
                if s.lower().endswith(".txt"):
                    fp = os.path.join(test_path, s)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="replace") as f:
                            preview = f.read(200)
                        lines.append("")
                        lines.append("Sample .txt read: %s" % s)
                        lines.append("  %s" % safe_repr(preview[:200]))
                    except Exception as e2:
                        lines.append("  .txt read error: %s" % str(e2))
                    break
        except Exception as e:
            lines.append("subdir listing:   <error: %s>" % str(e))

    return lines


def probe_tde4_api():
    """Check available tde4 requester APIs."""
    lines = []
    lines.append("-" * 60)
    lines.append("tde4 Requester API")
    lines.append("-" * 60)

    apis = [
        "postDirectoryRequester",
        "postFileRequester",
        "postQuestionRequester",
        "postCustomRequester",
        "createCustomRequester",
    ]
    for name in apis:
        available = hasattr(tde4, name)
        lines.append("  %s: %s" % (name, "AVAILABLE" if available else "not found"))

    return lines


def probe_native_requester_return(test_path):
    """
    Check a path that was already obtained from a native 3DE requester
    for mojibake and accessibility issues.
    """
    lines = []
    lines.append("-" * 60)
    lines.append("Requester Return-Value Check")
    lines.append("-" * 60)

    if not test_path:
        lines.append("(no requester path to check)")
        return lines

    lines.append("Return repr:      %s" % safe_repr(test_path))
    lines.append("os.path.exists:   %s" % os.path.exists(test_path))
    lines.append("Mojibake detected: %s" % has_mojibake(test_path))

    return lines


def classify(env_lines, path_lines, test_path):
    """Classify the issue based on probe results."""
    lines = []
    lines.append("-" * 60)
    lines.append("Diagnostic Classification")
    lines.append("-" * 60)

    # No test path selected - environment-only run
    if not test_path:
        lines.append("RESULT: Environment-only check")
        lines.append("")
        lines.append("No Unicode test path was selected.")
        lines.append("Path-specific classification was not performed.")
        lines.append("")
        lines.append("Use File mode to select any file inside a Chinese")
        lines.append("folder, or set TEST_UNICODE_PATH as a fallback.")
        lines.append("")
        lines.append("Note: Case A (native 3DE UI / requester display")
        lines.append("limitation) can only be confirmed by visual")
        lines.append("inspection of the requester window.")
        return lines

    full_report = "\n".join(env_lines + path_lines)

    path_accessible = "os.path.exists:   True" in full_report
    path_not_accessible = "os.path.exists:   False" in full_report
    requester_mojibake = "Mojibake detected: True" in full_report
    listdir_found = "basename in listdir: True" in full_report

    if path_accessible and listdir_found:
        lines.append("Python can access the Chinese path normally.")
        if requester_mojibake:
            lines.append("")
            lines.append("RESULT: Case D")
            lines.append("  Likely path encoding conversion issue between")
            lines.append("  3DE native UI and Python.  Workaround may require")
            lines.append("  avoiding native requester or using manual path input.")
        else:
            lines.append("")
            lines.append("RESULT: Case C")
            lines.append("  Python and filesystem both handle the Chinese path.")
            lines.append("  Issue may be limited to a specific importer/exporter")
            lines.append("  script.  Investigate the exact import workflow.")
    elif path_not_accessible or not listdir_found:
        lines.append("Python cannot access the Chinese path reliably.")
        lines.append("")
        lines.append("RESULT: Case B")
        lines.append("  Likely Python/runtime/filesystem encoding issue.")
        lines.append("  Further script-level patch may be possible.")
    else:
        lines.append("RESULT: Undetermined")
        lines.append("  Cannot classify the path behavior from probe data.")
        lines.append("  Review the Path Test section above for details.")

    # Always add Case A possibility
    lines.append("")
    lines.append("Note: Case A (native 3DE UI / requester display")
    lines.append("limitation) can only be confirmed by visual")
    lines.append("inspection of the requester window.  The probe")
    lines.append("cannot detect UI rendering issues automatically.")

    return lines


# ---------------------------------------------------------------------------
# Interactive path selection
# ---------------------------------------------------------------------------
def ask_directory_path():
    """Try the native directory requester.  Returns (path, error_string)."""
    if not hasattr(tde4, "postDirectoryRequester"):
        return None, "postDirectoryRequester not available"
    try:
        path = tde4.postDirectoryRequester("Select Unicode Test Folder", "")
        if path:
            return path, None
        return None, "No folder selected"
    except Exception as e:
        return None, str(e)


def ask_file_parent_path():
    """Use file requester, then return the parent folder.  Returns (path, error_string)."""
    if not hasattr(tde4, "postFileRequester"):
        return None, "postFileRequester not available"
    try:
        selected = tde4.postFileRequester(
            "Select any file inside the target folder",
            "*",
            "",
            0,
        )
        if not selected:
            return None, "No file selected"
        # postFileRequester may return a list for multi-selection
        if isinstance(selected, (list, tuple)):
            selected = selected[0] if selected else ""
        parent = os.path.dirname(selected)
        if parent:
            return parent, None
        return None, "Could not determine parent folder"
    except Exception as e:
        return None, str(e)


def interactive_select_path():
    """
    Let the user pick a test path interactively.
    Returns (test_path, path_source, error_message).
    path_source is one of: "TEST_UNICODE_PATH", "Directory requester",
    "File requester parent folder", "Skip", "Cancelled", "Error".
    """
    # If hardcoded path is set, use it directly
    if TEST_UNICODE_PATH.strip():
        return TEST_UNICODE_PATH.strip(), "TEST_UNICODE_PATH", None

    # Interactive selection
    r = tde4.postQuestionRequester(
        "Probe Unicode Paths",
        "Choose how to select a Unicode path test target.\n"
        "\n"
        "Folder:\n"
        "  Select a folder directly, if supported\n"
        "  by this 3DE build.\n"
        "\n"
        "File:\n"
        "  Select any file inside the target folder.\n"
        "  The probe will test that file's parent\n"
        "  folder.\n"
        "\n"
        "Skip:\n"
        "  Run environment checks only.",
        "Folder", "File", "Skip", "Cancel",
    )

    if r == 4 or r < 1:
        return "", "Cancelled", "User cancelled"

    if r == 3:
        return "", "Skip", "User chose environment checks only"

    if r == 1:
        # Folder
        path, err = ask_directory_path()
        if path:
            return path, "Directory requester", None
        # Directory requester failed or unavailable - offer File fallback
        if err:
            print("[INFO] Directory requester: %s" % err)
        r2 = tde4.postQuestionRequester(
            "Probe Unicode Paths",
            "Directory requester is not available or failed.\n"
            "\n"
            "Please use File mode:\n"
            "select any file inside the target folder.\n"
            "\n"
            "The probe will test the selected file's\n"
            "parent folder.",
            "File", "Skip", "Cancel",
        )
        if r2 == 1:
            path, err2 = ask_file_parent_path()
            if path:
                return path, "File requester parent folder (dir fallback)", None
            return "", "Error", err2 or "File requester failed"
        if r2 == 2:
            return "", "Skip", "User chose environment checks only"
        return "", "Cancelled", "User cancelled"

    # r == 2: File
    path, err = ask_file_parent_path()
    if path:
        return path, "File requester parent folder", None
    return "", "Error", err or "File requester failed"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # -- Interactive path selection --
    test_path, path_source, path_error = interactive_select_path()

    if path_source == "Cancelled":
        tde4.postQuestionRequester(
            "Probe Unicode Paths - Cancelled",
            "No checks were performed.",
            "Ok",
        )
        return

    if path_source == "Error":
        tde4.postQuestionRequester(
            "Probe Unicode Paths - Error",
            "Path selection failed:\n"
            "  %s\n"
            "\n"
            "Try setting TEST_UNICODE_PATH manually\n"
            "or use Skip for environment checks only."
            % (path_error or "unknown"),
            "Ok",
        )
        return

    # -- Build report --
    report = []
    report.append("=" * 60)
    report.append("Probe Unicode Paths - Full Report")
    report.append("=" * 60)
    report.append("")

    # Path source info
    report.append("-" * 60)
    report.append("Path Source")
    report.append("-" * 60)
    report.append("Source:        %s" % path_source)
    report.append("Selected path: %s" % safe_repr(test_path if test_path else "(none)"))
    if path_error:
        report.append("Error:         %s" % path_error)
    report.append("")

    # 1. Environment
    env_lines = probe_environment()
    report.extend(env_lines)
    report.append("")

    # 2. Path test
    path_lines = probe_path(test_path)
    report.extend(path_lines)
    report.append("")

    # 3. tde4 API availability
    api_lines = probe_tde4_api()
    report.extend(api_lines)
    report.append("")

    # 4. Optional requester return-value test (only if we have a path from a requester)
    if "requester" in path_source.lower():
        req_lines = probe_native_requester_return(test_path)
        report.extend(req_lines)
        report.append("")

    # 5. Classification
    class_lines = classify(env_lines, path_lines, test_path)
    report.extend(class_lines)
    report.append("")
    report.append("=" * 60)

    full_report = "\n".join(report)
    print(full_report)

    # Short popup
    if test_path:
        path_status = safe_repr(test_path)
        if len(path_status) > 60:
            path_status = path_status[:57] + "..."
        popup_text = (
            "Probe complete.\n"
            "\n"
            "Path source: %s\n"
            "Test path: %s\n"
            "\n"
            "Full report printed to console."
            % (path_source, path_status)
        )
    else:
        popup_text = (
            "Environment check completed.\n"
            "\n"
            "No Unicode path was selected.\n"
            "Use File mode to test a Chinese folder.\n"
            "\n"
            "Full report printed to console."
        )

    tde4.postQuestionRequester(
        "Probe Unicode Paths - Done",
        popup_text,
        "Ok",
    )


if __name__ == "__main__":
    main()
