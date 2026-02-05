import os
import sys
from pathlib import Path
from typing import Optional, Tuple


if __name__ == "__main__" and (__package__ is None or __package__ == ""):
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

import gradio as gr
from PIL import Image

from ascii_magic import DEFAULT_GEMINI_MODEL
from ascii_magic.ui.export_service import ExportService
from ascii_magic.ui.image_source import ImageSourceService
from ascii_magic.ui.preflight import has_google_genai, supports_server_clipboard
from ascii_magic.ui.render_service import RenderService


def _wrap_html_fragment(fragment: str) -> str:
    return (
        '<div style="background:#000;padding:12px;overflow:auto;">'
        '<pre style="margin:0;font-family:monospace;line-height:1;font-size:10px;">'
        f"{fragment}"
        "</pre>"
        "</div>"
    )


def _load_from_url(url: str) -> Tuple[Optional[Image.Image], str]:
    art, error = ImageSourceService.from_url(url)
    if error:
        return None, error
    assert art is not None
    return art.image, "Loaded image from URL"


def _load_from_clipboard() -> Tuple[Optional[Image.Image], str]:
    art, error = ImageSourceService.from_clipboard()
    if error:
        return None, error
    assert art is not None
    return art.image, "Loaded image from clipboard (server-side)"


def _load_from_gemini(
    prompt: str, api_key: str, model: str
) -> Tuple[Optional[Image.Image], str]:
    key = api_key.strip() if api_key else None
    art, error = ImageSourceService.from_gemini(prompt=prompt, api_key=key, model=model)
    if error:
        return None, error
    assert art is not None
    return art.image, "Generated image via Gemini"


def _render_and_export(
    img: Image.Image,
    columns: int,
    width_ratio: float,
    char_ramp: str,
    enhance_image: bool,
    html_mode: str,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], str]:
    html_fragment, ascii_text, error = RenderService.render_previews(
        img,
        columns=columns,
        width_ratio=width_ratio,
        char_ramp=char_ramp,
        enhance_image=enhance_image,
        html_mode=html_mode,
    )
    if error:
        return None, None, None, None, error

    assert html_fragment is not None
    assert ascii_text is not None

    html_wrapped = _wrap_html_fragment(html_fragment)

    monochrome = html_mode == "mono"
    full_color = html_mode == "full"

    html_path, html_error = ExportService.write_html_file(
        img,
        columns=columns,
        width_ratio=width_ratio,
        char_ramp=char_ramp,
        enhance_image=enhance_image,
        monochrome=monochrome,
        full_color=full_color,
    )
    if html_error:
        return html_wrapped, ascii_text, None, None, html_error

    txt_path, txt_error = ExportService.write_text_file(
        img,
        columns=columns,
        width_ratio=width_ratio,
        char_ramp=char_ramp,
        enhance_image=enhance_image,
    )
    if txt_error:
        return html_wrapped, ascii_text, html_path, None, txt_error

    return html_wrapped, ascii_text, html_path, txt_path, "Rendered previews"


def _export_image(
    img: Image.Image,
    file_type: str,
    columns: int,
    width_ratio: float,
    char_ramp: str,
    enhance_image: bool,
    image_mode: str,
    back: str,
) -> Tuple[Optional[str], Optional[str], str]:
    if img is None:
        return None, None, "No image loaded"

    monochrome = image_mode == "mono"
    full_color = image_mode == "full"

    path, error = ExportService.write_image_file(
        img,
        file_type=file_type,  # type: ignore[arg-type]
        columns=columns,
        width_ratio=width_ratio,
        char_ramp=char_ramp,
        enhance_image=enhance_image,
        monochrome=monochrome,
        full_color=full_color,
        back=back,
    )
    if error:
        return None, None, error

    return path, path, "Exported image"


def build_demo() -> gr.Blocks:
    gemini_available = has_google_genai()
    clipboard_available = supports_server_clipboard()

    with gr.Blocks(title="ascii_magic UI (Gradio)") as demo:
        gr.Markdown(
            "# ascii_magic UI\n"
            "Upload an image (or load from URL), tweak render settings, and export outputs."
        )

        current_image = gr.State(value=None)

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Tabs():
                    with gr.Tab("Upload"):
                        upload = gr.Image(type="pil", label="Upload image")
                        load_upload = gr.Button("Use uploaded image", variant="primary")

                    with gr.Tab("URL"):
                        url = gr.Textbox(
                            label="Image URL",
                            placeholder="https://example.com/image.jpg",
                        )
                        load_url = gr.Button("Fetch image")

                    with gr.Tab("Clipboard (server)"):
                        gr.Markdown(
                            "Reads the clipboard of the machine running this app (not your browser)."
                        )
                        load_clip = gr.Button(
                            "Load from clipboard",
                            interactive=clipboard_available,
                        )
                        if not clipboard_available:
                            gr.Markdown(
                                "Clipboard is disabled on this host. On Linux, it requires PyGObject (gi)."
                            )

                    with gr.Tab("Gemini"):
                        if gemini_available:
                            prompt = gr.Textbox(
                                label="Prompt",
                                lines=3,
                                placeholder="A cat wearing sunglasses...",
                            )
                            api_key = gr.Textbox(
                                label="API key (optional if GEMINI_API_KEY is set)",
                                type="password",
                            )
                            model = gr.Textbox(
                                label="Model",
                                value=os.environ.get(
                                    "GEMINI_MODEL", DEFAULT_GEMINI_MODEL
                                ),
                            )
                            load_gemini = gr.Button("Generate image")
                        else:
                            gr.Markdown(
                                "Gemini is disabled because `google-genai` is not installed.\n\n"
                                "Install with: `pip install google-genai`"
                            )
                            prompt = gr.Textbox(visible=False)
                            api_key = gr.Textbox(visible=False)
                            model = gr.Textbox(visible=False)
                            load_gemini = gr.Button(visible=False)

                loaded_preview = gr.Image(
                    type="pil",
                    label="Loaded image",
                    interactive=False,
                )

                with gr.Accordion("Render options", open=False):
                    columns = gr.Slider(
                        40,
                        200,
                        value=120,
                        step=1,
                        label="Columns",
                    )
                    width_ratio = gr.Slider(
                        1.0,
                        4.0,
                        value=2.2,
                        step=0.1,
                        label="Width ratio",
                    )
                    char_ramp = gr.Textbox(
                        label="Character ramp (optional)",
                        placeholder="Leave empty for default",
                    )
                    enhance = gr.Checkbox(label="Enhance image", value=False)
                    html_mode = gr.Radio(
                        choices=[
                            ("Full color", "full"),
                            ("Terminal palette", "terminal"),
                            ("Monochrome", "mono"),
                        ],
                        value="full",
                        label="HTML mode",
                    )

                render_btn = gr.Button("Render previews", variant="primary")

            with gr.Column(scale=2):
                status = gr.Markdown("Ready")

                with gr.Tabs():
                    with gr.Tab("HTML"):
                        html_out = gr.HTML()
                        html_file = gr.File(label="Download HTML")

                    with gr.Tab("Text"):
                        text_out = gr.Textbox(
                            lines=28, label="ASCII text", interactive=False
                        )
                        text_file = gr.File(label="Download TXT")

                    with gr.Tab("Image"):
                        image_mode = gr.Radio(
                            choices=[
                                ("Full color", "full"),
                                ("Terminal palette", "terminal"),
                                ("Monochrome", "mono"),
                            ],
                            value="terminal",
                            label="Image mode",
                        )
                        file_type = gr.Radio(
                            choices=["PNG", "JPG", "WEBP"],
                            value="PNG",
                            label="File type",
                        )
                        back = gr.ColorPicker(value="#000000", label="Background")
                        export_btn = gr.Button("Export image")
                        image_out = gr.Image(type="filepath", label="Preview")
                        image_file = gr.File(label="Download image")

        def _use_upload(
            img: Image.Image,
        ) -> Tuple[Optional[Image.Image], Optional[Image.Image], str]:
            if img is None:
                return None, None, "No image uploaded"
            return img, img, "Loaded image from upload"

        load_upload.click(
            fn=_use_upload,
            inputs=[upload],
            outputs=[current_image, loaded_preview, status],
        )

        load_url.click(
            fn=_load_from_url,
            inputs=[url],
            outputs=[current_image, status],
        ).then(
            fn=lambda img: img,
            inputs=[current_image],
            outputs=[loaded_preview],
        )

        load_clip.click(
            fn=_load_from_clipboard,
            inputs=[],
            outputs=[current_image, status],
        ).then(
            fn=lambda img: img,
            inputs=[current_image],
            outputs=[loaded_preview],
        )

        if gemini_available:
            load_gemini.click(
                fn=_load_from_gemini,
                inputs=[prompt, api_key, model],
                outputs=[current_image, status],
            ).then(
                fn=lambda img: img,
                inputs=[current_image],
                outputs=[loaded_preview],
            )

        render_btn.click(
            fn=_render_and_export,
            inputs=[current_image, columns, width_ratio, char_ramp, enhance, html_mode],
            outputs=[html_out, text_out, html_file, text_file, status],
        )

        export_btn.click(
            fn=_export_image,
            inputs=[
                current_image,
                file_type,
                columns,
                width_ratio,
                char_ramp,
                enhance,
                image_mode,
                back,
            ],
            outputs=[image_out, image_file, status],
        )

    return demo


if __name__ == "__main__":
    build_demo().queue().launch()
