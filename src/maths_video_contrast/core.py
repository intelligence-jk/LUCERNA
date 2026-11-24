"""WCAG 2.x contrast maths. Standard library only."""
import colorsys
import json

# (normal text, large text)
THRESHOLDS = {"AA": (4.5, 3.0), "AAA": (7.0, 4.5)}


def parse_hex(value):
    """Parse '#rgb' or '#rrggbb' (the # is optional) into (r, g, b) ints 0..255."""
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"not a hex colour: {value!r}")
    try:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"not a hex colour: {value!r}") from None


def to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(round(c)))):02x}" for c in rgb)


def _linear(channel_8bit):
    c = channel_8bit / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = (_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    """Contrast ratio of two hex colours, from 1 to 21."""
    l1 = relative_luminance(parse_hex(fg))
    l2 = relative_luminance(parse_hex(bg))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def check_pair(fg, bg, large=False):
    ratio = contrast_ratio(fg, bg)
    idx = 1 if large else 0
    return {
        "text": fg, "background": bg, "large": large,
        "ratio": round(ratio, 2),
        "AA": ratio >= THRESHOLDS["AA"][idx],
        "AAA": ratio >= THRESHOLDS["AAA"][idx],
    }


def suggest_text_colour(fg, bg, level="AA", large=False):
    """Nearest passing text colour: change HSL lightness only, keep hue and saturation.

    Returns a hex string, or None if no lightness passes. If fg already passes it is returned unchanged.
    """
    target = THRESHOLDS[level][1 if large else 0]
    if contrast_ratio(fg, bg) >= target:
        return to_hex(parse_hex(fg))
    r, g, b = (c / 255 for c in parse_hex(fg))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    best = None
    steps = 1000
    for k in range(1, steps + 1):
        for sign in (1, -1):
            l2 = l + sign * k / steps
            if not 0 <= l2 <= 1:
                continue
            cand = to_hex([c * 255 for c in colorsys.hls_to_rgb(h, l2, s)])
            if contrast_ratio(cand, bg) >= target:
                best = cand
                break
        if best:
            break
    return best


def check_palette(path_or_data, level="AA"):
    """Check a palette: JSON {"pairs": [{"name", "text", "background", "large"?}]}."""
    if isinstance(path_or_data, (str, bytes)) or hasattr(path_or_data, "__fspath__"):
        with open(path_or_data, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = path_or_data
    results = []
    for p in data["pairs"]:
        large = bool(p.get("large", False))
        res = check_pair(p["text"], p["background"], large)
        res["name"] = p.get("name", "")
        res["passes"] = res[level]
        res["suggestion"] = None if res["passes"] else suggest_text_colour(
            p["text"], p["background"], level, large)
        results.append(res)
    return results
