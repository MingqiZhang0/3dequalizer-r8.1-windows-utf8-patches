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
import traceback
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
        lines.append("  copy a folder/file path in Windows Explorer,")
        lines.append("  run the probe again and choose Clip mode.")
        lines.append("")
        lines.append("File mode can test the native 3DE requester.")
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


def classify(env_lines, path_lines, test_path, path_source):
    """Classify the issue based on probe results."""
    lines = []
    lines.append("-" * 60)
    lines.append("Diagnostic Classification")
    lines.append("-" * 60)

    # Requester itself failed before obtaining a path
    if path_source == "File requester failed":
        lines.append("RESULT: Requester path selection failed")
        lines.append("")
        lines.append("The native 3DE file requester failed before a")
        lines.append("path could be tested.  This suggests a native")
        lines.append("requester / path conversion limitation.")
        lines.append("")
        lines.append("Use Clipboard mode to test whether Python can")
        lines.append("access the same path directly.")
        lines.append("")
        lines.append("Note: Case A (native 3DE UI / requester display")
        lines.append("limitation) can only be confirmed by visual")
        lines.append("inspection of the requester window.")
        return lines

    if path_source == "Clipboard path failed":
        lines.append("RESULT: Clipboard path failed")
        lines.append("")
        lines.append("The probe could not read a usable path from the")
        lines.append("Windows clipboard.")
        lines.append("")
        lines.append("Copy a folder/file path in Windows Explorer")
        lines.append("and try again.")
        return lines

    if path_source == "Paste path failed":
        lines.append("RESULT: Paste path failed")
        lines.append("")
        lines.append("The 3DE custom requester text field failed.")
        lines.append("Use Clipboard mode instead.")
        return lines

    # No test path selected - environment-only run
    if not test_path:
        lines.append("RESULT: Environment-only check")
        lines.append("")
        lines.append("No Unicode test path was selected.")
        lines.append("Path-specific classification was not performed.")
        lines.append("")
        lines.append("Use File or Paste mode to test a Chinese folder,")
        lines.append("or set TEST_UNICODE_PATH as a fallback.")
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
        lines.append("Python can access the Unicode path normally.")
        lines.append("")
        lines.append("RESULT: Python path access OK")
        lines.append("")
        lines.append("Python filesystem access works for this path.")
        lines.append("")
        if requester_mojibake:
            lines.append("Mojibake was detected in the path string obtained")
            lines.append("from the requester (Case D pattern).  This suggests")
            lines.append("a path encoding conversion issue between 3DE native")
            lines.append("UI and Python.")
        else:
            lines.append("Requester context:")
            lines.append("")
            lines.append("- If File mode failed with UnicodeDecodeError or")
            lines.append("  returned no path, this supports a native 3DE")
            lines.append("  requester / path conversion limitation.")
            lines.append("- If File mode works but a specific import workflow")
            lines.append("  fails, investigate that importer script.")
            lines.append("- If both File mode and Clip mode succeed and no")
            lines.append("  specific import issue is reported, Python and")
            lines.append("  the native requester both handle the path.")
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
# Path helpers
# ---------------------------------------------------------------------------
def normalize_user_path(raw_path):
    """Strip quotes, whitespace, expand env vars and ~."""
    if raw_path is None:
        return ""
    path = raw_path.strip()
    if len(path) >= 2:
        if (path[0] == '"' and path[-1] == '"') or \
           (path[0] == "'" and path[-1] == "'"):
            path = path[1:-1]
    path = path.strip()
    try:
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
    except Exception:
        pass
    return path


def path_to_test_folder(path):
    """
    Normalize *path* and return the folder to test.
    If *path* is a directory, return it directly.
    If *path* is a file, return its parent directory.
    Otherwise return *path* as-is for diagnostics.
    Returns (folder_path, error_message).
    """
    path = normalize_user_path(path)
    if not path:
        return "", "Empty path"
    try:
        if os.path.isdir(path):
            return path, None
        if os.path.isfile(path):
            return os.path.dirname(path), None
        # Doesn't exist - still return for diagnostics
        return path, "Path does not exist according to os.path"
    except Exception as exc:
        return path, str(exc)


# ---------------------------------------------------------------------------
# Windows clipboard reader (bypasses 3DE requester encoding issues)
# ---------------------------------------------------------------------------
def read_windows_clipboard_text():
    """
    Read Unicode text from the Windows clipboard using CF_UNICODETEXT.
    All API functions have explicit argtypes/restype to avoid 64-bit
    handle/pointer truncation.

    Returns (text, error_string).
    """
    if os.name != "nt":
        return None, "Windows clipboard mode is only supported on Windows"

    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        CF_UNICODETEXT = 13

        # --- Explicit prototypes (critical for 64-bit) ---
        user32.OpenClipboard.argtypes = [wintypes.HWND]
        user32.OpenClipboard.restype = wintypes.BOOL

        user32.CloseClipboard.argtypes = []
        user32.CloseClipboard.restype = wintypes.BOOL

        user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
        user32.IsClipboardFormatAvailable.restype = wintypes.BOOL

        user32.GetClipboardData.argtypes = [wintypes.UINT]
        user32.GetClipboardData.restype = wintypes.HANDLE

        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalLock.restype = wintypes.LPVOID

        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalUnlock.restype = wintypes.BOOL

        kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalSize.restype = ctypes.c_size_t

        if not user32.OpenClipboard(None):
            err = ctypes.get_last_error()
            return None, "OpenClipboard failed, error=%s" % err

        locked = False
        handle = None

        try:
            if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                return None, "Clipboard does not contain CF_UNICODETEXT"

            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                err = ctypes.get_last_error()
                return None, "GetClipboardData failed, error=%s" % err

            size_bytes = kernel32.GlobalSize(handle)
            if not size_bytes:
                err = ctypes.get_last_error()
                return None, "GlobalSize failed or zero, error=%s" % err

            ptr = kernel32.GlobalLock(handle)
            if not ptr:
                err = ctypes.get_last_error()
                return None, "GlobalLock failed, error=%s" % err

            locked = True

            # CF_UNICODETEXT is UTF-16LE, null-terminated.
            # size_bytes includes the terminating null bytes.
            max_chars = int(size_bytes // ctypes.sizeof(ctypes.c_wchar))
            if max_chars <= 0:
                return None, "Clipboard Unicode text size is zero"

            text = ctypes.wstring_at(ptr, max_chars)

            # Strip trailing nulls
            text = text.split("\x00", 1)[0]
            text = text.strip()

            if not text:
                return None, "Clipboard Unicode text is empty"

            return text, None

        finally:
            if locked and handle:
                try:
                    kernel32.GlobalUnlock(handle)
                except Exception:
                    pass
            try:
                user32.CloseClipboard()
            except Exception:
                pass

    except Exception as exc:
        traceback.print_exc()
        return None, "%s: %s" % (exc.__class__.__name__, exc)


def ask_clipboard_path():
    """Read a Unicode path from the Windows clipboard."""
    text, error = read_windows_clipboard_text()
    if error:
        return "", error

    # Handle multi-line clipboard (use first line)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return "", "Clipboard text is empty"
    path = lines[0]
    if len(lines) > 1:
        print("[INFO] Clipboard contained %d lines; using first line." % len(lines))

    path = normalize_user_path(path)
    if not path:
        return "", "Clipboard path is empty after normalization"

    folder, folder_error = path_to_test_folder(path)
    return folder, folder_error  # folder_error may be None or a diagnostic message


# ---------------------------------------------------------------------------
# Interactive path selection
# ---------------------------------------------------------------------------
def ask_file_parent_path():
    """Use file requester, then return the parent folder."""
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
        if isinstance(selected, (list, tuple)):
            selected = selected[0] if selected else ""
        parent = os.path.dirname(selected)
        if parent:
            return parent, None
        return None, "Could not determine parent folder"
    except Exception as e:
        return None, str(e)


def ask_pasted_path():
    """Let the user paste a full path.  Returns (raw_path, error_string)."""
    if not hasattr(tde4, "createCustomRequester"):
        return None, "createCustomRequester not available"
    try:
        req = tde4.createCustomRequester()
        tde4.addTextFieldWidget(req, "path", "Path", "")
        ret = tde4.postCustomRequester(
            req,
            "Paste Unicode Path",
            800, 120,
            "Continue", "Cancel",
        )
        if ret != 1:
            tde4.deleteCustomRequester(req)
            return None, "User cancelled paste path"
        path = tde4.getWidgetValue(req, "path")
        tde4.deleteCustomRequester(req)
        if not path or not path.strip():
            return None, "Empty path"
        return path.strip(), None
    except Exception as exc:
        traceback.print_exc()
        return None, str(exc)


def interactive_select_path():
    """
    Let the user pick a test path interactively.
    Returns (test_folder_path, path_source, error_message).
    """
    # If hardcoded path is set, use it directly
    if TEST_UNICODE_PATH.strip():
        return TEST_UNICODE_PATH.strip(), "TEST_UNICODE_PATH", None

    r = tde4.postQuestionRequester(
        "Probe Unicode Paths",
        "Choose how to select a Unicode path test target.\n"
        "\n"
        "File:\n"
        "  Use native 3DE file requester.\n"
        "  This may fail on Chinese paths.\n"
        "\n"
        "Clip:\n"
        "  Copy a folder/file path in Windows\n"
        "  Explorer first.  Then choose Clip to\n"
        "  read it from the Windows clipboard.\n"
        "  This avoids 3DE requester encoding issues.\n"
        "\n"
        "Skip:\n"
        "  Run environment checks only.",
        "File", "Clip", "Skip", "Cancel",
    )

    if r == 4 or r < 1:
        return "", "Cancelled", "User cancelled"

    if r == 3:
        return "", "Skip", "User chose environment checks only"

    if r == 1:
        # File mode - test native requester
        path, err = ask_file_parent_path()
        if path:
            return path, "File requester parent folder", None
        return "", "File requester failed", err or "File requester returned no path"

    # r == 2: Clipboard mode
    folder, err = ask_clipboard_path()
    if err:
        return "", "Clipboard path failed", err
    return folder, "Clipboard path", None


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
    class_lines = classify(env_lines, path_lines, test_path, path_source)
    report.extend(class_lines)
    report.append("")
    report.append("=" * 60)

    full_report = "\n".join(report)
    print(full_report)

    # Short popup
    if path_source == "File requester failed":
        popup_text = (
            "Native file requester did not return a\n"
            "usable path.\n"
            "\n"
            "Try Clipboard mode:\n"
            "copy the path in Windows Explorer, then\n"
            "run Probe again and choose Clip.\n"
            "\n"
            "Full report printed to console."
        )
    elif path_source in ("Clipboard path failed", "Paste path failed"):
        popup_text = (
            "Could not read a Unicode path.\n"
            "\n"
            "Try Clipboard mode:\n"
            "copy the path in Windows Explorer, then\n"
            "run Probe again and choose Clip.\n"
            "\n"
            "Full report printed to console."
        )
    elif test_path:
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
            "Use File or Paste mode to test a Chinese\n"
            "folder.\n"
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
