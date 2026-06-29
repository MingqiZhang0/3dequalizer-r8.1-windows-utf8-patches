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
# Optional test path - set this to a folder containing Chinese characters.
# Example:
#   TEST_UNICODE_PATH = r"F:\测试目录"
# Leave empty to skip path-specific tests.
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
        lines.append("(no test path provided - set TEST_UNICODE_PATH)")
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
        "postFileRequester",
        "postQuestionRequester",
        "postCustomRequester",
        "createCustomRequester",
    ]
    for name in apis:
        available = hasattr(tde4, name)
        lines.append("  %s: %s" % (name, "AVAILABLE" if available else "not found"))

    return lines


def probe_native_requester():
    """
    Optional: let user pick a file/folder via native 3DE requester
    and check the returned path.
    """
    lines = []
    lines.append("-" * 60)
    lines.append("Native Requester Test")
    lines.append("-" * 60)

    if not hasattr(tde4, "postFileRequester"):
        lines.append("postFileRequester not available - skipping.")
        return lines

    # Ask if user wants to test
    r = tde4.postQuestionRequester(
        "Probe Unicode Paths",
        "Optional: test native 3DE file requester?\n"
        "\n"
        "A file picker will open.\n"
        "Select a file or folder with a Chinese name\n"
        "if available.\n"
        "\n"
        "No files will be opened or modified.",
        "Test", "Skip",
    )

    if r != 1:
        lines.append("Native requester test skipped by user.")
        return lines

    try:
        result = tde4.postFileRequester(
            "Select a Chinese-named file or folder",
            "*",
            "",
            0,
        )

        lines.append("Return type:      %s" % type(result).__name__)
        lines.append("Return repr:      %s" % safe_repr(result))

        if isinstance(result, str) and result:
            lines.append("os.path.exists:   %s" % os.path.exists(result))
            lines.append("Mojibake detected: %s" % has_mojibake(result))
        elif isinstance(result, (list, tuple)) and result:
            for i, p in enumerate(result[:5]):
                lines.append("Path %d:           %s" % (i, safe_repr(p)))
                lines.append("  exists:          %s" % os.path.exists(p))
                lines.append("  mojibake:        %s" % has_mojibake(p))
        else:
            lines.append("(no path returned or cancelled)")

    except Exception as e:
        lines.append("postFileRequester error: %s" % str(e))

    return lines


def classify(env_lines, path_lines):
    """Classify the issue based on probe results."""
    lines = []
    lines.append("-" * 60)
    lines.append("Diagnostic Classification")
    lines.append("-" * 60)

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
        lines.append("No path test was performed.")
        lines.append("Set TEST_UNICODE_PATH to a Chinese-named folder")
        lines.append("and re-run to get a specific classification.")
        lines.append("")
        lines.append("RESULT: Undetermined")
        lines.append("  Cannot classify without a test path.")

    # Always add Case A possibility
    lines.append("")
    lines.append("Note: Case A (native 3DE UI / requester display")
    lines.append("limitation) can only be confirmed by visual")
    lines.append("inspection of the requester window.  The probe")
    lines.append("cannot detect UI rendering issues automatically.")

    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    report = []
    report.append("=" * 60)
    report.append("Probe Unicode Paths - Full Report")
    report.append("=" * 60)
    report.append("")

    # 1. Environment
    env_lines = probe_environment()
    report.extend(env_lines)
    report.append("")

    # 2. Path test
    path_lines = probe_path(TEST_UNICODE_PATH)
    report.extend(path_lines)
    report.append("")

    # 3. tde4 API availability
    api_lines = probe_tde4_api()
    report.extend(api_lines)
    report.append("")

    # 4. Optional native requester test
    req_lines = probe_native_requester()
    report.extend(req_lines)
    report.append("")

    # 5. Classification
    class_lines = classify(env_lines, path_lines)
    report.extend(class_lines)
    report.append("")
    report.append("=" * 60)

    full_report = "\n".join(report)
    print(full_report)

    # Short popup
    has_path = bool(TEST_UNICODE_PATH.strip())
    path_status = "provided" if has_path else "not set"

    tde4.postQuestionRequester(
        "Probe Unicode Paths - Done",
        "Probe complete.\n"
        "\n"
        "Test path: %s\n"
        "\n"
        "Full report printed to console.\n"
        "\n"
        "Check for:\n"
        "  - os.path.exists result\n"
        "  - listdir visibility\n"
        "  - requester mojibake indicators\n"
        "  - Case A/B/C/D classification"
        % path_status,
        "Ok",
    )


if __name__ == "__main__":
    main()
