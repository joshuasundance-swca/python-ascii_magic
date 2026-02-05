import importlib.util
import sys


def has_google_genai() -> bool:
    """Return True if the optional google-genai dependency appears importable."""
    return importlib.util.find_spec("google.genai") is not None


def supports_server_clipboard() -> bool:
    """Return True if the host running the UI can likely read its OS clipboard.

    Note: this is *server-side* clipboard access (not browser clipboard access).
    """
    if sys.platform in {"win32", "darwin"}:
        return True

    # On Linux, ascii_magic falls back to GTK via PyGObject (gi).
    if sys.platform.startswith("linux"):
        return importlib.util.find_spec("gi") is not None

    return False
