from typing import Optional, Tuple

from PIL import Image

from ascii_magic.ascii_art import AsciiArt


HtmlMode = str  # "full" | "terminal" | "mono"


class RenderService:
    """Renders previews from a Pillow image using ascii_magic's native renderers."""

    @staticmethod
    def render_previews(
        img: Image.Image,
        *,
        columns: int = 120,
        width_ratio: float = 2.2,
        char_ramp: Optional[str] = None,
        enhance_image: bool = False,
        html_mode: HtmlMode = "full",
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Return (html_fragment, ascii_text, error_message)."""

        if img is None:
            return None, None, "No image loaded"

        char = char_ramp.strip() if char_ramp is not None else None
        if char == "":
            char = None

        monochrome = html_mode == "mono"
        full_color = html_mode == "full"

        try:
            art = AsciiArt.from_pillow_image(img)

            html = art.to_html(
                columns=int(columns),
                width_ratio=float(width_ratio),
                char=char,
                enhance_image=bool(enhance_image),
                monochrome=monochrome,
                full_color=full_color,
                debug=False,
            )

            text = art.to_ascii(
                columns=int(columns),
                width_ratio=float(width_ratio),
                char=char,
                monochrome=True,
                enhance_image=bool(enhance_image),
                debug=False,
            )

            return html, text, None
        except Exception as exc:
            return None, None, f"Render failed: {exc}"
