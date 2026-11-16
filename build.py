#!/usr/bin/env python3
"""Build the single-file, fully offline index.html for 나라장터 조달 타이쿤.

All runtime dependencies are inlined so the submitted ZIP opens with a plain
double-click on index.html (file://) with no network:
  three.min.js (vendored r147) + 마스코트/로고 WebP data URI + 게임 데이터(JS 객체)

Usage:  python3 build.py [output.html]
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def data_uri(name: str, mime: str) -> str:
    raw = (ASSETS / name).read_bytes()
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))


def main() -> None:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
    html = (ROOT / "index_template.html").read_text(encoding="utf-8")

    html = html.replace("__NARMI__", data_uri("mascot_narmi.webp", "image/webp"))
    html = html.replace("__DALL__", data_uri("mascot_dall.webp", "image/webp"))
    html = html.replace("__LOGO__", data_uri("logo_h.webp", "image/webp"))

    assert html.count("<script>__THREE__</script>") == 1, "template must carry exactly one three.js slot"
    three = (ROOT / "three.min.js").read_text(encoding="utf-8")
    assert "</script" not in three, "vendored three.js must not close a script tag"
    html = html.replace("<script>__THREE__</script>", "<script>" + three + "</script>")

    assert "__NARMI__" not in html and "__DALL__" not in html and "__LOGO__" not in html
    for bad in ("unpkg", "jsdelivr", "fonts.googleapis", "cdnjs"):
        assert bad not in html.lower(), bad
    game_src = html.rsplit("<script>", 1)[-1]
    for bad in ("fetch(", "XMLHttpRequest", "type=\"module\"", "import("):
        assert bad not in game_src, bad

    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size
    print(f"built {out}  ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
