import argparse
import sys

from .core import check_pair, check_palette, suggest_text_colour


def _yn(b):
    return "pass" if b else "FAIL"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m maths_video_contrast",
                                 description="WCAG contrast checker for maths videos")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check one text/background pair")
    c.add_argument("text"); c.add_argument("background")
    c.add_argument("--large", action="store_true", help="large text (18pt or 14pt bold and up)")
    s = sub.add_parser("suggest", help="nearest passing text colour (same hue)")
    s.add_argument("text"); s.add_argument("background")
    s.add_argument("--level", choices=["AA", "AAA"], default="AA")
    s.add_argument("--large", action="store_true")
    p = sub.add_parser("palette", help="check every pair in a JSON palette file")
    p.add_argument("file")
    p.add_argument("--level", choices=["AA", "AAA"], default="AA")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check":
            r = check_pair(a.text, a.background, a.large)
            print(f"{a.text} on {a.background}: {r['ratio']}:1  AA {_yn(r['AA'])}  AAA {_yn(r['AAA'])}")
            return 0 if r["AA"] else 1
        if a.cmd == "suggest":
            out = suggest_text_colour(a.text, a.background, a.level, a.large)
            if out is None:
                print("no lightness of this hue passes on this background")
                return 1
            print(out)
            return 0
        bad = 0
        for r in check_palette(a.file, a.level):
            line = f"{r['name'] or r['text']}: {r['text']} on {r['background']} {r['ratio']}:1 {a.level} {_yn(r['passes'])}"
            if r["suggestion"]:
                line += f"  try {r['suggestion']}"
            bad += not r["passes"]
            print(line)
        return 1 if bad else 0
    except (ValueError, KeyError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
