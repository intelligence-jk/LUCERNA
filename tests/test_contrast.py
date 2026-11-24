import json
import pytest
from maths_video_contrast import (contrast_ratio, check_pair, suggest_text_colour,
                                  check_palette, relative_luminance, parse_hex)
from maths_video_contrast.__main__ import main


def test_black_on_white_is_21():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0)
    assert contrast_ratio("#ffffff", "#000000") == pytest.approx(21.0)


def test_same_colour_is_1():
    assert contrast_ratio("#336699", "#336699") == pytest.approx(1.0)


def test_grey_777_on_white_fails_aa():
    r = check_pair("#777777", "#ffffff")
    assert 4.47 < r["ratio"] < 4.49
    assert r["AA"] is False and r["AAA"] is False
    assert check_pair("#777777", "#ffffff", large=True)["AA"] is True


def test_short_hex_and_luminance_ends():
    assert parse_hex("#fff") == (255, 255, 255)
    assert relative_luminance((0, 0, 0)) == 0
    assert relative_luminance((255, 255, 255)) == pytest.approx(1.0)


def test_bad_hex():
    with pytest.raises(ValueError):
        parse_hex("#12")
    with pytest.raises(ValueError):
        parse_hex("zzzzzz")


@pytest.mark.parametrize("level", ["AA", "AAA"])
def test_suggestion_passes_and_keeps_hue(level):
    fix = suggest_text_colour("#777777", "#ffffff", level)
    assert check_pair(fix, "#ffffff")[level]
    fix2 = suggest_text_colour("#ff9900", "#ffffff", level)
    assert check_pair(fix2, "#ffffff")[level]
    # hue kept: orange stays red-dominant with green in between
    r, g, b = parse_hex(fix2)
    assert r > g > b


def test_suggestion_on_dark_background_lightens():
    fix = suggest_text_colour("#333399", "#111111")
    assert check_pair(fix, "#111111")["AA"]
    assert sum(parse_hex(fix)) > sum(parse_hex("#333399"))


def test_passing_colour_unchanged():
    assert suggest_text_colour("#000000", "#ffffff") == "#000000"


def test_palette(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"pairs": [
        {"name": "title", "text": "#ffffff", "background": "#0b2a6f"},
        {"name": "caption", "text": "#777777", "background": "#ffffff"},
    ]}))
    res = check_palette(str(f))
    assert res[0]["passes"] and not res[1]["passes"]
    assert check_pair(res[1]["suggestion"], "#ffffff")["AA"]
    assert main(["palette", str(f)]) == 1


def test_cli_check(capsys):
    assert main(["check", "#000", "#fff"]) == 0
    assert "21.0:1" in capsys.readouterr().out
    assert main(["check", "#777777", "#ffffff"]) == 1
