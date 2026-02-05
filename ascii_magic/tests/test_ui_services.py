from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from ascii_magic.ui.export_service import ExportService
from ascii_magic.ui.image_source import ImageSourceService
from ascii_magic.ui.render_service import RenderService


def _make_test_image() -> Image.Image:
    img = Image.new("RGB", (32, 16), color=(255, 0, 0))
    return img


def test_image_source_from_pillow_image_ok() -> None:
    img = _make_test_image()
    art, error = ImageSourceService.from_pillow_image(img)

    assert error is None
    assert art is not None
    assert art.image.size == (32, 16)


def test_image_source_from_url_validation() -> None:
    art, error = ImageSourceService.from_url("")
    assert art is None
    assert error

    art, error = ImageSourceService.from_url("ftp://example.com/x.png")
    assert art is None
    assert "http" in (error or "").lower()


def test_image_source_clipboard_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ascii_magic.ui.image_source.supports_server_clipboard", lambda: False
    )

    art, error = ImageSourceService.from_clipboard()
    assert art is None
    assert error


def test_image_source_gemini_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ascii_magic.ui.image_source.has_google_genai", lambda: False)

    art, error = ImageSourceService.from_gemini(prompt="a test")
    assert art is None
    assert error


@pytest.mark.parametrize(
    "mode, expect_style",
    [
        ("mono", False),
        ("terminal", True),
        ("full", True),
    ],
)
def test_render_service_html_modes(mode: str, expect_style: bool) -> None:
    img = _make_test_image()
    html, text, error = RenderService.render_previews(img, columns=40, html_mode=mode)

    assert error is None
    assert html is not None
    assert text is not None
    assert "<span" in html

    if expect_style:
        assert 'style="color:' in html
    else:
        assert 'style="color:' not in html


def test_export_service_text_file(tmp_path: Path) -> None:
    img = _make_test_image()

    out_path = tmp_path / "art.txt"
    path, error = ExportService.write_text_file(img, columns=40, path=str(out_path))

    assert error is None
    assert path == str(out_path)
    assert out_path.exists()
    assert out_path.read_text(encoding="utf-8").strip() != ""


def test_export_service_html_file(tmp_path: Path) -> None:
    img = _make_test_image()

    out_path = tmp_path / "art.html"
    path, error = ExportService.write_html_file(
        img,
        columns=40,
        full_color=True,
        path=str(out_path),
    )

    assert error is None
    assert path == str(out_path)
    assert out_path.exists()

    contents = out_path.read_text(encoding="utf-8")
    lower = contents.lower()
    assert "<!doctype html" in lower
    assert "</html>" in lower
    assert "<pre" in lower


def test_export_service_image_file_png(tmp_path: Path) -> None:
    img = _make_test_image()

    out_path = tmp_path / "art.png"
    path, error = ExportService.write_image_file(
        img,
        file_type="PNG",
        columns=40,
        path=str(out_path),
    )

    assert error is None
    assert path == str(out_path)
    assert out_path.exists()

    opened = Image.open(out_path)
    assert opened.size[0] > 0
    assert opened.size[1] > 0
    assert (opened.format or "").upper() == "PNG"
