"""contrast.py: WCAG ratios, see-through colours, and the command line."""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

THEME_MD = Path(__file__).resolve().parent.parent / "references" / "theme.md"


@pytest.mark.parametrize(
    ("fg", "bg", "shown", "verdict", "backdrop"),
    [
        ("000000", "FFFFFF", "21.00", "PASS", None),
        ("777777", "FFFFFF", "4.48", "FAIL", None),
        # 128 grey over white: 3.95 with the 8-bit rounding, 3.98 without it.
        ("FFFFFF", "000000@0.5", "3.95", "FAIL", "white"),
        ("000000@0.5", "FFFFFF", "3.95", "FAIL", None),
        ("FFFFFF@0.5", "000000@0.5", "2.17", "FAIL", "white"),
        ("FFF8EC", "2B1D14@0.35", "4.86", "PASS", "white"),
    ],
)
def test_ratios_match_hand_computed_values(cli, contrast, fg, bg, shown, verdict, backdrop):
    code, out, _ = cli(contrast, fg, bg)
    line = out.strip()
    assert line.startswith(f"{shown}:1  {verdict} 4.5  {fg} on {bg}")
    assert line.endswith(f"(over {backdrop})") == (backdrop is not None)
    assert code == (0 if verdict == "PASS" else 1)


def test_see_through_background_reports_the_worse_backdrop(contrast):
    ratio, backdrop = contrast.worst_ratio(contrast.parse_colour("1A1A1A"), contrast.parse_colour("FFFFFF@0.5"))
    assert backdrop == "black"
    assert ratio < 5


def test_composite_rounds_each_channel_to_8_bits(contrast):
    assert contrast.composite(contrast.parse_colour("2B1D14@0.35"), (255, 255, 255)) == (117, 108, 102)


@pytest.mark.parametrize("text", ["#FFAA00", "ffaa00", "#FA0", "fa0", "255,170,0", "255, 170, 0"])
def test_colour_forms(contrast, text):
    colour = contrast.parse_colour(text)
    assert colour.rgb == (255, 170, 0)
    assert colour.transparency == 0
    assert contrast.parse_colour(f"{text}@.25").transparency == 0.25


@pytest.mark.parametrize("text", ["GGGGGG", "12345", "256,0,0", "1,2", "red", "FFFFFF@1.5", "FFFFFF@", "FFFFFF@-0.1"])
def test_invalid_colours_exit_2_naming_the_forms(cli, contrast, text):
    code, out, err = cli(contrast, text, "FFFFFF")
    assert code == 2
    assert out == ""
    assert text in err
    assert "RRGGBB" in err and "R,G,B" in err


def test_colours_come_in_pairs(cli, contrast):
    code, _, err = cli(contrast, "000000", "FFFFFF", "777777")
    assert code == 2
    assert "pairs" in err and "got 3" in err


def test_min_sets_the_bar(cli, contrast):
    code, out, _ = cli(contrast, "--min", "3", "777777", "FFFFFF")
    assert code == 0
    assert out.strip().startswith("4.48:1  PASS 3  ")


def test_every_pair_is_reported_and_one_failure_fails_the_run(cli, contrast):
    code, out, _ = cli(contrast, "000000", "FFFFFF", "777777", "FFFFFF")
    assert code == 1
    assert [line.split()[1] for line in out.splitlines()] == ["PASS", "FAIL"]


def test_ratio_just_under_the_bar_is_never_shown_as_passing(contrast):
    assert contrast.shown(4.4999, 4.5) == "4.49"
    assert contrast.shown(4.4949, 4.5) == "4.49"
    assert contrast.shown(4.5, 4.5) == "4.50"
    assert contrast.shown(4.4999, 3) == "4.50"


def test_json_output(cli, contrast):
    code, out, _ = cli(contrast, "--json", "FFFFFF", "000000@0.5", "000000", "fff")
    assert code == 1
    first, second = json.loads(out)
    assert first == {
        "fg": "FFFFFF",
        "bg": "000000@0.5",
        "ratio": pytest.approx(3.949, abs=0.001),
        "min": 4.5,
        "pass": False,
        "backdrop": "white",
    }
    assert second["bg"] == "FFFFFF"
    assert second["pass"] is True
    assert second["backdrop"] is None


def _theme_examples() -> list[list[str]]:
    lines = re.findall(r"^python <skill>/scripts/contrast\.py (.+)$", THEME_MD.read_text(encoding="utf-8"), re.MULTILINE)
    assert len(lines) == 3
    return [shlex.split(line) for line in lines]


@pytest.mark.parametrize("args", _theme_examples())
def test_theme_examples_pass(cli, contrast, args):
    code, out, _ = cli(contrast, *args)
    assert code == 0, out


@pytest.mark.parametrize(
    ("fg", "bg", "shown"),
    [("FFF8EC", "C4552D", "4.25"), ("FFF8EC", "B54A24", "5.01"), ("1F6F6B", "E8D9B5", "4.24")],
)
def test_ratios_theme_md_states(contrast, fg, bg, shown):
    ratio, _ = contrast.worst_ratio(contrast.parse_colour(fg), contrast.parse_colour(bg))
    assert contrast.shown(ratio, 4.5) == shown
    assert f"{shown}:1" in THEME_MD.read_text(encoding="utf-8")


def test_help_runs_as_a_script(scripts_dir):
    proc = subprocess.run(
        [sys.executable, str(scripts_dir / "contrast.py"), "--help"], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout
