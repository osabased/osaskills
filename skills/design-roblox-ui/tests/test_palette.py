"""palette.py: measured colours, merging, accents, transparency, and the command line."""
import json
import subprocess
import sys

from PIL import Image

INK = (43, 29, 20)
PAPER = (243, 233, 210)
RUST = (196, 85, 45)


def _bands(path, *bands, mode="RGB"):
    """Save a 100 x 100 image of vertical bands, each (width, colour)."""
    image = Image.new(mode, (100, 100))
    x = 0
    for width, colour in bands:
        image.paste(colour, (x, 0, x + width, 100))
        x += width
    assert x == 100
    image.save(path)
    return path


def _lines(out):
    return [line.split() for line in out.splitlines()]


def test_flat_colours_are_measured_exactly(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (70, RUST), (30, PAPER))
    code, out, _ = cli(palette, image)
    assert code == 0
    assert _lines(out)[1:] == [["#C4552D", "70.0%"], ["#F3E9D2", "30.0%"]]


def test_near_colours_merge_under_the_larger(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (50, PAPER), (30, (240, 230, 207)), (20, INK))
    code, out, _ = cli(palette, image)
    assert code == 0
    assert _lines(out)[1:] == [["#F3E9D2", "80.0%"], ["#2B1D14", "20.0%"]]
    _, out, _ = cli(palette, "--merge", "0", image)
    assert len(_lines(out)) == 4


def test_a_small_accent_needs_a_lower_min_share(cli, palette, tmp_path):
    image = Image.new("RGB", (100, 100), PAPER)
    image.paste(RUST, (0, 0, 10, 10))
    image.save(tmp_path / "ref.png")
    _, out, _ = cli(palette, tmp_path / "ref.png")
    assert "#C4552D" not in out
    _, out, _ = cli(palette, "--min-share", "0.005", tmp_path / "ref.png")
    assert ["#C4552D", "1.0%"] in _lines(out)


def test_see_through_pixels_are_ignored(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (50, (255, 0, 0, 0)), (50, (*INK, 255)), mode="RGBA")
    _, out, _ = cli(palette, image)
    assert _lines(out)[1:] == [["#2B1D14", "100.0%"]]


def test_several_images_end_with_what_they_share(cli, palette, tmp_path):
    first = _bands(tmp_path / "a.png", (100, PAPER))
    second = _bands(tmp_path / "b.png", (50, PAPER), (50, INK))
    code, out, _ = cli(palette, first, second)
    assert code == 0
    lines = out.splitlines()
    assert lines[-3:] == ["All 2 images", "  #F3E9D2   75.0%", "  #2B1D14   25.0%"]


def test_colours_caps_the_list(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (40, PAPER), (30, INK), (30, RUST))
    _, out, _ = cli(palette, "--colours", "1", image)
    assert _lines(out)[1:] == [["#F3E9D2", "40.0%"]]


def test_json_output(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (70, RUST), (30, PAPER))
    code, out, _ = cli(palette, "--json", image)
    assert code == 0
    assert json.loads(out) == {str(image): [{"hex": "#C4552D", "share": 0.7}, {"hex": "#F3E9D2", "share": 0.3}]}


def test_an_unreadable_image_exits_2_naming_it(cli, palette, tmp_path):
    bad = tmp_path / "not-an-image.png"
    bad.write_text("hello", encoding="utf-8")
    code, out, err = cli(palette, bad)
    assert code == 2
    assert out == ""
    assert "not-an-image.png" in err


def test_a_fully_see_through_image_exits_2(cli, palette, tmp_path):
    image = _bands(tmp_path / "ref.png", (100, (0, 0, 0, 0)), mode="RGBA")
    code, _, err = cli(palette, image)
    assert code == 2
    assert "no opaque pixels" in err


def test_help_runs_as_a_script(scripts_dir):
    proc = subprocess.run([sys.executable, str(scripts_dir / "palette.py"), "--help"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout
