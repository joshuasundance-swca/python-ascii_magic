import os
import tempfile
from typing import Literal, Optional, Tuple

from PIL import Image

from ascii_magic.ascii_art import AsciiArt
from ascii_magic.constants import DEFAULT_STYLES


ImageFileType = Literal["PNG", "JPG", "GIF", "WEBP"]


class ExportService:
    """Exports rendered outputs to temp files suitable for UI download widgets."""

    @staticmethod
    def _new_temp_path(*, suffix: str) -> str:
        handle, path = tempfile.mkstemp(suffix=suffix, prefix="ascii_magic_ui_")
        os.close(handle)
        return path

    @staticmethod
    def write_html_file(
        img: Image.Image,
        *,
        columns: int = 120,
        width_ratio: float = 2.2,
        char_ramp: Optional[str] = None,
        enhance_image: bool = False,
        monochrome: bool = False,
        full_color: bool = True,
        path: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Write a full HTML document to disk. Returns (path, error)."""

        if img is None:
            return None, "No image loaded"

        char = char_ramp.strip() if char_ramp is not None else None
        if char == "":
            char = None

        out_path = path or ExportService._new_temp_path(suffix=".html")

        try:
            art = AsciiArt.from_pillow_image(img)
            art.to_html_file(
                path=out_path,
                columns=int(columns),
                width_ratio=float(width_ratio),
                char=char,
                enhance_image=bool(enhance_image),
                monochrome=bool(monochrome),
                full_color=bool(full_color),
                styles=DEFAULT_STYLES,
                additional_styles="",
                auto_open=False,
                debug=False,
            )
            return out_path, None
        except Exception as exc:
            return None, f"HTML export failed: {exc}"

    @staticmethod
    def write_text_file(
        img: Image.Image,
        *,
        columns: int = 120,
        width_ratio: float = 2.2,
        char_ramp: Optional[str] = None,
        enhance_image: bool = False,
        path: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Write plain ASCII text to disk. Returns (path, error)."""

        if img is None:
            return None, "No image loaded"

        char = char_ramp.strip() if char_ramp is not None else None
        if char == "":
            char = None

        out_path = path or ExportService._new_temp_path(suffix=".txt")

        try:
            art = AsciiArt.from_pillow_image(img)
            text = art.to_ascii(
                columns=int(columns),
                width_ratio=float(width_ratio),
                char=char,
                monochrome=True,
                enhance_image=bool(enhance_image),
                debug=False,
            )
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            return out_path, None
        except Exception as exc:
            return None, f"Text export failed: {exc}"

    @staticmethod
    def write_image_file(
        img: Image.Image,
        *,
        file_type: ImageFileType = "PNG",
        columns: int = 120,
        width_ratio: float = 2.2,
        char_ramp: Optional[str] = None,
        enhance_image: bool = False,
        monochrome: bool = False,
        full_color: bool = False,
        back: str = "#000000",
        path: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Write an image export to disk. Returns (path, error)."""

        if img is None:
            return None, "No image loaded"

        char = char_ramp.strip() if char_ramp is not None else None
        if char == "":
            char = None

        suffix = "." + file_type.lower()
        out_path = path or ExportService._new_temp_path(suffix=suffix)

        try:
            art = AsciiArt.from_pillow_image(img)
            art.to_image_file(
                path=out_path,
                file_type=file_type,
                columns=int(columns),
                width_ratio=float(width_ratio),
                char=char,
                enhance_image=bool(enhance_image),
                monochrome=bool(monochrome),
                full_color=bool(full_color),
                back=back,
                debug=False,
            )
            return out_path, None
        except Exception as exc:
            return None, f"Image export failed: {exc}"
