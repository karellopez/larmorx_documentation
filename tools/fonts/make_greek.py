"""Make the site's Greek font subsets (static/fonts/*-Greek.woff2).

The site's Instrument Serif, Inter and JetBrains Mono files are Latin subsets: they have no
Greek letters (ω, γ, φ, ...) and no subscript digits (₀), which then fall back to whatever
serif the reader's system has. This script cuts small companion files with exactly those
characters from the full fonts in Google Fonts' repository (pinned commit, SHA-256 checked),
all under the SIL Open Font License 1.1:

- Noto Serif Display, italic and upright, as the serif's Greek: a high-contrast display serif
  that sits well beside Instrument Serif (Instrument Serif has no Greek at all);
- Inter (400) and JetBrains Mono (400): their own Greek, cut from their variable fonts.

static/css/site.css loads them with a `unicode-range`, so a page downloads one only when it
shows one of its characters. Needs fontTools and brotli:

    pip install fonttools brotli
    python tools/fonts/make_greek.py
"""

from __future__ import annotations

import hashlib
import io
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "static" / "fonts"
COMMIT = "47d54ca1ebb14fd864695f1d39dc734f39017c33"  # google/fonts, 2026-10-16
BASE = f"https://raw.githubusercontent.com/google/fonts/{COMMIT}/"

#: Greek and Coptic letters, the Greek symbol variants, subscript digits and signs.
UNICODES = [*range(0x0391, 0x03AA), *range(0x03B1, 0x03CA), 0x03D1, 0x03D5, 0x03D6, 0x03F0,
            0x03F1, 0x03F5, *range(0x2080, 0x208F)]
UNICODE_RANGE = "U+0391-03A9, U+03B1-03C9, U+03D1, U+03D5-03D6, U+03F0-03F1, U+03F5, U+2080-208E"

SOURCES = {
    "ofl/notoserifdisplay/NotoSerifDisplay-Italic[wdth,wght].ttf":
        "daad4d314708839a5c343f26e75467edf6c05a3a726502c98974dd3e240e6516",
    "ofl/notoserifdisplay/NotoSerifDisplay[wdth,wght].ttf":
        "4b661adcf6a5d38bf5befdc4d976e8a7238a4aeb57e62c1c1a67775380a09df9",
    "ofl/notoserifdisplay/OFL.txt": "5e0da210fb04058a8c0087985d2d456b931c2579811a49655721d3cf0c36b6d6",
    "ofl/inter/Inter[opsz,wght].ttf": "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
    "ofl/jetbrainsmono/JetBrainsMono[wght].ttf":
        "48715a42ec242c21e9f02692891e147d022299a52e48d5e413e1a942193ffeda",
}

#: output file -> (source, axis values)
CUTS = {
    "NotoSerifDisplay-Italic-Greek.woff2": (
        "ofl/notoserifdisplay/NotoSerifDisplay-Italic[wdth,wght].ttf", {"wght": 400, "wdth": 100}),
    "NotoSerifDisplay-Greek.woff2": (
        "ofl/notoserifdisplay/NotoSerifDisplay[wdth,wght].ttf", {"wght": 400, "wdth": 100}),
    "Inter-Greek.woff2": ("ofl/inter/Inter[opsz,wght].ttf", {"wght": 400, "opsz": 14}),
    "JetBrainsMono-Greek.woff2": ("ofl/jetbrainsmono/JetBrainsMono[wght].ttf", {"wght": 400}),
}


def fetch(rel: str) -> bytes:
    url = BASE + rel.replace("[", "%5B").replace("]", "%5D")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    digest = hashlib.sha256(data).hexdigest()
    expected = SOURCES[rel]
    if digest != expected:
        raise SystemExit(f"{url}: SHA-256 {digest}, expected {expected}")
    print(f"{rel}: {len(data)} bytes, sha256 {digest}")
    return data


def main() -> None:
    cache: dict[str, bytes] = {}
    for name, (rel, axes) in CUTS.items():
        data = cache.setdefault(rel, fetch(rel))
        font = instancer.instantiateVariableFont(TTFont(io.BytesIO(data)), axes)
        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.notdef_outline = True
        sub = subset.Subsetter(options)
        sub.populate(unicodes=UNICODES)
        sub.subset(font)
        font.flavor = "woff2"
        font.save(OUT / name)
        print(f"{name}: {(OUT / name).stat().st_size} bytes, axes {axes}")
    (OUT / "NotoSerifDisplay-OFL.txt").write_bytes(fetch("ofl/notoserifdisplay/OFL.txt"))
    print(f"unicode-range: {UNICODE_RANGE}")


if __name__ == "__main__":
    main()
