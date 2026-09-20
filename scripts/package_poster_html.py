#!/usr/bin/env python3
"""Build one portable Yinxi poster HTML file.

The case author works in ``render.html`` with ordinary relative image paths.
This script creates the formal ``poster.html`` delivery: every local image and
CSS asset is converted to a data URI and the two production fonts are embedded
as well.  The renderer then renders this exact file, so the editable document
and the published PNG use one layout source.
"""

import argparse
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


SKILL_ROOT = Path(__file__).resolve().parents[1]
FONT_FILES = (
    ("Yinxi Noto Serif SC", 700, SKILL_ROOT / "assets" / "fonts" / "NotoSerifCJKsc-Bold.otf"),
    ("Yinxi Noto Sans SC", 500, SKILL_ROOT / "assets" / "fonts" / "NotoSansCJKsc-Medium.otf"),
)
PORTABLE_MARKER = '<meta name="yinxi-portable-poster" content="v1">'
IMAGE_TAG_URL = re.compile(
    r"(?P<prefix><(?:img|source|image)\b[^>]*?\b(?:src|href|xlink:href)\s*=\s*)(?P<quote>['\"])(?P<url>[^'\"]+)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
CSS_URL = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<url>[^)'\"\s]+)(?P=quote)\s*\)", re.IGNORECASE)
SRCSET = re.compile(r"<(?:img|source)\b[^>]*?\bsrcset\s*=\s*(['\"])(?P<value>.*?)\1", re.IGNORECASE | re.DOTALL)


def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    if path.suffix.lower() == ".otf":
        mime = "font/otf"
    if not mime:
        mime = "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def resolve_local_asset(raw_url: str, base_dir: Path) -> Path | None:
    """Resolve one local asset reference, rejecting network dependencies."""
    if raw_url.startswith("data:") or raw_url.startswith("#"):
        return None
    parsed = urlparse(raw_url)
    if parsed.scheme in {"http", "https"}:
        raise ValueError(f"remote asset is not allowed in portable poster HTML: {raw_url}")
    if parsed.scheme and parsed.scheme != "file":
        raise ValueError(f"unsupported asset URL scheme in portable poster HTML: {raw_url}")
    if parsed.scheme == "file":
        path = Path(unquote(parsed.path))
    else:
        path = (base_dir / unquote(parsed.path)).resolve()
    if not path.is_file():
        raise ValueError(f"local asset does not exist: {raw_url}")
    return path


def embedded_font_css() -> str:
    rules = []
    for family, weight, path in FONT_FILES:
        if not path.is_file():
            raise ValueError(f"bundled production font is missing: {path}")
        rules.append(
            f'@font-face {{ font-family: "{family}"; src: url("{data_uri(path)}") format("opentype"); '
            f"font-weight: {weight}; font-style: normal; font-display: block; }}"
        )
    return "\n".join(rules)


def replace_assets(source: str, base_dir: Path) -> tuple[str, int]:
    """Inline image-tag and CSS-url assets, returning the image-like asset count."""
    if match := SRCSET.search(source):
        if "data:" not in match.group("value"):
            raise ValueError("srcset is not supported in portable posters; use one explicit <img src> asset")

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


def inject_portable_metadata(source: str) -> str:
    if PORTABLE_MARKER in source:
        raise ValueError("source already contains Yinxi portable-poster metadata; package the editable render.html instead")
    injection = f"\n    {PORTABLE_MARKER}\n    <style id=\"yinxi-embedded-fonts\">\n{embedded_font_css()}\n    </style>"
    if "</head>" not in source.lower():
        raise ValueError("poster source must contain a </head> tag")
    return re.sub(r"</head>", injection + "\n  </head>", source, count=1, flags=re.IGNORECASE)


def validate_portable_document(source: str) -> dict:
    """Return portable-document facts or raise ValueError for a broken delivery."""
    if PORTABLE_MARKER not in source:
        raise ValueError("missing yinxi portable-poster marker")
    for family, _, _ in FONT_FILES:
        if family not in source:
            raise ValueError(f"missing embedded production font declaration: {family}")
    if source.count("data:font/otf;base64,") < len(FONT_FILES):
        raise ValueError("production fonts are not embedded as data URIs")

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
        raise ValueError("portable poster contains non-embedded assets: " + ", ".join(non_embedded[:3]))
    return {
        "format": "yinxi-portable-poster-v1",
        "portable_html": True,
        "embedded_font_count": len(FONT_FILES),
        "embedded_asset_reference_count": len(image_refs) + len(css_refs),
    }


def package_html(input_path: Path) -> tuple[str, dict]:
    source = input_path.read_text(encoding="utf-8")
    source, embedded_images = replace_assets(source, input_path.parent)
    source = inject_portable_metadata(source)
    proof = validate_portable_document(source)
    proof["embedded_local_asset_count"] = embedded_images
    proof["source"] = input_path.name
    return source, proof


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed poster assets and fonts into one portable HTML delivery.")
    parser.add_argument("--input", required=True, type=Path, help="editable case render.html source")
    parser.add_argument("--output", required=True, type=Path, help="formal self-contained poster.html")
    parser.add_argument("--proof", required=True, type=Path, help="machine-produced portable HTML proof JSON")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"input HTML does not exist: {args.input}")
    try:
        packaged, proof = package_html(args.input)
    except (OSError, ValueError) as error:
        print(f"cannot package portable poster: {error}", file=sys.stderr)
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
