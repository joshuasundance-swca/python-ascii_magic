import os
from typing import Optional, Tuple

from PIL import Image

from ascii_magic import DEFAULT_GEMINI_MODEL
from ascii_magic.ascii_art import AsciiArt

from ascii_magic.ui.preflight import has_google_genai, supports_server_clipboard


class ImageSourceService:
    """Loads images from different sources with UI-friendly error messages."""

    @staticmethod
    def from_pillow_image(img: Image.Image) -> Tuple[Optional[AsciiArt], Optional[str]]:
        if img is None:
            return None, "No image provided"

        try:
            return AsciiArt.from_pillow_image(img), None
        except Exception as exc:
            return None, f"Failed to load image: {exc}"

    @staticmethod
    def from_url(url: str) -> Tuple[Optional[AsciiArt], Optional[str]]:
        if not url or not url.strip():
            return None, "Please provide an image URL"

        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            return None, "URL must start with http:// or https://"

        try:
            return AsciiArt.from_url(url), None
        except Exception as exc:
            return None, f"Failed to fetch image: {exc}"

    @staticmethod
    def from_clipboard() -> Tuple[Optional[AsciiArt], Optional[str]]:
        if not supports_server_clipboard():
            return (
                None,
                "Clipboard is not supported on this host (Linux requires PyGObject)",
            )

        try:
            return AsciiArt.from_clipboard(), None
        except OSError as exc:
            return None, str(exc)
        except SystemExit:
            # ascii_magic may call exit() on Linux when gi is missing.
            return None, "Clipboard support is unavailable on this host"
        except Exception as exc:
            return None, f"Clipboard error: {exc}"

    @staticmethod
    def from_gemini(
        prompt: str,
        api_key: Optional[str] = None,
        model: str = DEFAULT_GEMINI_MODEL,
    ) -> Tuple[Optional[AsciiArt], Optional[str]]:
        if not has_google_genai():
            return None, "Gemini support requires: pip install google-genai"

        if not prompt or not prompt.strip():
            return None, "Please enter a prompt"

        if not api_key and not os.environ.get("GEMINI_API_KEY"):
            return None, "Set GEMINI_API_KEY or provide an API key"

        try:
            return (
                AsciiArt.from_gemini(
                    prompt=prompt.strip(), model=model, api_key=api_key
                ),
                None,
            )
        except ValueError as exc:
            return None, str(exc)
        except OSError as exc:
            return None, str(exc)
        except SystemExit:
            # ascii_magic may call exit() when google-genai is missing.
            return None, "Gemini initialization failed (missing dependency?)"
        except Exception as exc:
            return None, f"Gemini error: {exc}"
