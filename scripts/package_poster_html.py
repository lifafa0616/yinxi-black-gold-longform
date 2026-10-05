#!/usr/bin/env python3
"""Build one browser-renderable Yinxi poster HTML file.

The case author works in ``render.html`` with ordinary relative image paths.
This script creates the ``poster.html`` render document: local images and CSS
assets become data URIs while the production fonts come from one allowlisted
Google Fonts stylesheet.  The renderer then renders this exact file to the
formal PNG output.
"""

import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


REQUIRED_FONTS = (
    "Noto Serif SC 700",
    "Noto Sans SC 400",
    "Noto Sans SC 500",
)
FONT_READY_SCRIPT = r"""async () => {
  const specs = [
    '700 32px "Noto Serif SC"',
    '400 32px "Noto Sans SC"',
    '500 32px "Noto Sans SC"',
  ];
  const loadedFaces = await Promise.all(specs.map((spec) => document.fonts.load(spec, '字体检测 Aa 123')));
  await document.fonts.ready;
  return document.fonts.status === 'loaded' &&
    loadedFaces.every((faces) => faces.length > 0) &&
    specs.every((spec) => document.fonts.check(spec, '字体检测 Aa 123'));
}"""
GOOGLE_FONTS_STYLESHEET = (
    "https://fonts.googleapis.com/css2?"
    "family=Noto+Sans+SC:wght@400;500&family=Noto+Serif+SC:wght@700&display=block"
)
RENDER_DOCUMENT_MARKER = '<meta name="yinxi-render-document" content="v2">'
# Compatibility alias for callers that still use the old validator name.
PORTABLE_MARKER = RENDER_DOCUMENT_MARKER
IMAGE_TAG_URL = re.compile(
    r"(?P<prefix><(?:img|source|image)\b[^>]*?\b(?:src|href|xlink:href)\s*=\s*)(?P<quote>['\"])(?P<url>[^'\"]+)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
CSS_URL = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<url>[^)'\"\s]+)(?P=quote)\s*\)", re.IGNORECASE)
SRCSET = re.compile(r"<(?:img|source)\b[^>]*?\bsrcset\s*=\s*(['\"])(?P<value>.*?)\1", re.IGNORECASE | re.DOTALL)
STYLESHEET_LINK = re.compile(
    r"<link\b(?=[^>]*\brel\s*=\s*['\"]stylesheet['\"])[^>]*\bhref\s*=\s*['\"](?P<url>https?://[^'\"]+)['\"][^>]*>",
    re.IGNORECASE | re.DOTALL,
)


def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    if not mime:
        mime = "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def resolve_local_asset(raw_url: str, base_dir: Path) -> Path | None:
    """Resolve one local image reference, rejecting remote image dependencies."""
    if raw_url.startswith("data:") or raw_url.startswith("#"):
        return None
    parsed = urlparse(raw_url)
    if parsed.scheme in {"http", "https"}:
        raise ValueError(f"remote asset is not allowed for poster images: {raw_url}")
    if parsed.scheme and parsed.scheme != "file":
        raise ValueError(f"unsupported asset URL scheme in poster render document: {raw_url}")
    if parsed.scheme == "file":
        path = Path(unquote(parsed.path))
    else:
        path = (base_dir / unquote(parsed.path)).resolve()
    if not path.is_file():
        raise ValueError(f"local asset does not exist: {raw_url}")
    return path


def replace_legacy_font_families(source: str) -> str:
    """Keep existing cases usable while moving from bundled aliases."""
    return source.replace("Yinxi Noto Serif SC", "Noto Serif SC").replace(
        "Yinxi Noto Sans SC", "Noto Sans SC"
    )


def replace_assets(source: str, base_dir: Path) -> tuple[str, int]:
    """Inline image-tag and CSS-url assets, returning the image-like asset count."""
    if match := SRCSET.search(source):
        if "data:" not in match.group("value"):
            raise ValueError("srcset is not supported in poster render documents; use one explicit <img src> asset")

    embedded = 0

    def replace_tag_url(match: re.Match[str]) -> str:
        nonlocal embedded
        raw_url = match.group("url")
        path = resolve_local_asset(raw_url, base_dir)
        if path is None:
            return match.group(0)
        embedded += 1
        return f'{match.group("prefix")}{match.group("quote")}{data_uri(path)}{match.group("quote")}'

    source = IMAGE_TAG_URL.sub(replace_tag_url, source)

    def replace_css_url(match: re.Match[str]) -> str:
        nonlocal embedded
        raw_url = match.group("url")
        path = resolve_local_asset(raw_url, base_dir)
        if path is None:
            return match.group(0)
        embedded += 1
        quote = match.group("quote") or '"'
        return f"url({quote}{data_uri(path)}{quote})"

    return CSS_URL.sub(replace_css_url, source), embedded


def inject_render_metadata(source: str) -> str:
    if RENDER_DOCUMENT_MARKER in source or "yinxi-portable-poster" in source:
        raise ValueError("source already contains Yinxi render metadata; package the editable render.html instead")
    stylesheet = html.escape(GOOGLE_FONTS_STYLESHEET, quote=True)
    injection = (
        f"\n    {RENDER_DOCUMENT_MARKER}\n"
        '    <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'    <link id="yinxi-google-fonts" rel="stylesheet" href="{stylesheet}">'
    )
    if "</head>" not in source.lower():
        raise ValueError("poster source must contain a </head> tag")
    return re.sub(r"</head>", injection + "\n  </head>", source, count=1, flags=re.IGNORECASE)


def validate_render_document(source: str) -> dict:
    """Return render-document facts or reject unknown network dependencies."""
    if RENDER_DOCUMENT_MARKER not in source:
        raise ValueError("missing yinxi render-document marker")
    stylesheets = [html.unescape(match.group("url")) for match in STYLESHEET_LINK.finditer(source)]
    unexpected = [url for url in stylesheets if url != GOOGLE_FONTS_STYLESHEET]
    if unexpected:
        raise ValueError("unapproved external stylesheet in render document: " + unexpected[0])
    if stylesheets.count(GOOGLE_FONTS_STYLESHEET) != 1:
        raise ValueError("render document requires exactly one approved Google Fonts stylesheet")
    if "data:font/" in source:
        raise ValueError("render document must not embed font files")

    image_refs = IMAGE_TAG_URL.findall(source)
    css_refs = CSS_URL.findall(source)
    non_embedded = []
    for _, _, url in image_refs:
        if not url.startswith("data:"):
            non_embedded.append(url)
    for _, url in css_refs:
        if not (url.startswith("data:") or url.startswith("#")):
            non_embedded.append(url)
    if non_embedded:
        raise ValueError("render document contains non-embedded local assets: " + ", ".join(non_embedded[:3]))
    return {
        "format": "yinxi-render-document-v2",
        "render_document": True,
        "font_source": "google-fonts-css2",
        "remote_font_stylesheet": GOOGLE_FONTS_STYLESHEET,
        "required_fonts": list(REQUIRED_FONTS),
        "embedded_font_count": 0,
        "embedded_asset_reference_count": len(image_refs) + len(css_refs),
    }


def validate_portable_document(source: str) -> dict:
    """Compatibility alias for scripts not yet renamed around poster.html."""
    return validate_render_document(source)


def package_html(input_path: Path) -> tuple[str, dict]:
    source = input_path.read_text(encoding="utf-8")
    source, embedded_images = replace_assets(source, input_path.parent)
    source = replace_legacy_font_families(source)
    source = inject_render_metadata(source)
    proof = validate_render_document(source)
    proof["embedded_local_asset_count"] = embedded_images
    proof["source"] = input_path.name
    return source, proof


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed local poster assets and attach the approved Google Fonts stylesheet.")
    parser.add_argument("--input", required=True, type=Path, help="editable case render.html source")
    parser.add_argument("--output", required=True, type=Path, help="network-backed intermediate poster.html render document")
    parser.add_argument("--proof", required=True, type=Path, help="machine-produced render-document proof JSON")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"input HTML does not exist: {args.input}")
    try:
        packaged, proof = package_html(args.input)
    except (OSError, ValueError) as error:
        print(f"cannot package poster render document: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.proof.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(packaged, encoding="utf-8")
    args.proof.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"packaged: {args.output}")
    print(f"proof: {args.proof}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
