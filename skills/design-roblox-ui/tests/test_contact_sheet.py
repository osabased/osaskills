"""contact_sheet.py: grid layout, backdrops, labels, and the command line."""
import os
import subprocess
import sys

import pytest
from PIL import Image

RED, GREEN, BLUE, GOLD = (220, 40, 40), (40, 180, 70), (40, 80, 220), (230, 180, 30)


def solid(tmp_path, name, colour, size=(300, 150), mode="RGB"):
    path = tmp_path / name
    Image.new(mode, size, colour).save(path)
    return path


def sheet(cli, contact_sheet, tmp_path, *args):
    out = tmp_path / "out" / "sheet.png"
    code, stdout, stderr = cli(contact_sheet, *args, "--out", out)
    assert code == 0, stderr
    return Image.open(out).convert("RGB"), stdout, stderr


def cell_bottoms(image, rows, columns, cell_width, padding):
    """Each cell's centre on its image's bottom pixel row, for same-height images."""
    row_height = (image.height - padding) // rows - padding
    return [
        (padding + column * (cell_width + padding) + cell_width // 2, padding + row * (row_height + padding) + row_height - 1)
        for row in range(rows)
        for column in range(columns)
    ]


def test_width_follows_the_columns(cli, contact_sheet, tmp_path):
    image = solid(tmp_path, "a.png", RED)
    padding = contact_sheet.PADDING
    result, stdout, _ = sheet(cli, contact_sheet, tmp_path, image, image, image, "--columns", 3, "--cell-width", 200)
    assert result.width == padding + 3 * (200 + padding)
    assert stdout == f"wrote {(tmp_path / 'out' / 'sheet.png').as_posix()} ({result.width}x{result.height})\n"


def test_rows_stack_with_padding_between(cli, contact_sheet, tmp_path):
    image = solid(tmp_path, "a.png", RED)
    one, _, _ = sheet(cli, contact_sheet, tmp_path, image)
    three, _, _ = sheet(cli, contact_sheet, tmp_path, image, image, image)
    assert three.width == contact_sheet.PADDING + 2 * (600 + contact_sheet.PADDING)
    assert three.height == 2 * one.height - contact_sheet.PADDING


def test_images_fill_cells_in_row_order_at_the_cell_width(cli, contact_sheet, tmp_path):
    paths = [solid(tmp_path, f"{index}.png", colour) for index, colour in enumerate([RED, GREEN, BLUE, GOLD])]
    result, _, _ = sheet(cli, contact_sheet, tmp_path, *paths, "--cell-width", 400)
    probes = cell_bottoms(result, rows=2, columns=2, cell_width=400, padding=contact_sheet.PADDING)
    assert [result.getpixel(point) for point in probes] == [RED, GREEN, BLUE, GOLD]
    row_height = (result.height - contact_sheet.PADDING) // 2 - contact_sheet.PADDING
    image_bottom = probes[0][1]
    assert result.getpixel((probes[0][0], image_bottom - 199)) == RED
    assert result.getpixel((probes[0][0], image_bottom + 1)) != RED
    assert row_height > 200


def test_transparent_renders_show_each_backdrop(cli, contact_sheet, tmp_path):
    clear = solid(tmp_path, "hud.png", (0, 0, 0, 0), mode="RGBA")
    result, _, stderr = sheet(cli, contact_sheet, tmp_path, clear, "--backdrop", "white", "--backdrop", "black")
    assert stderr == ""
    probes = cell_bottoms(result, rows=1, columns=2, cell_width=600, padding=contact_sheet.PADDING)
    assert [result.getpixel(point) for point in probes] == [(255, 255, 255), (0, 0, 0)]


def test_an_image_backdrop_covers_the_cell(cli, contact_sheet, tmp_path):
    clear = solid(tmp_path, "hud.png", (0, 0, 0, 0), mode="RGBA")
    screenshot = solid(tmp_path, "world.png", GREEN, size=(100, 100))
    result, _, _ = sheet(cli, contact_sheet, tmp_path, clear, "--backdrop", screenshot)
    (probe,) = cell_bottoms(result, rows=1, columns=1, cell_width=600, padding=contact_sheet.PADDING)
    assert result.getpixel(probe) == GREEN
    assert result.getpixel((contact_sheet.PADDING, probe[1])) == GREEN


def test_cells_are_image_major_with_backdrop_labels(contact_sheet, tmp_path):
    entries = [(tmp_path / "a.png", "A phone"), (tmp_path / "b.png", "B phone")]
    cells = contact_sheet.expand(entries, ["white", "busy", str(tmp_path / "world.png")])
    assert [cell.label for cell in cells] == [
        "A phone · white",
        "A phone · busy",
        "A phone · world",
        "B phone · white",
        "B phone · busy",
        "B phone · world",
    ]
    assert [cell.label for cell in contact_sheet.expand(entries, [])] == ["A phone", "B phone"]


def test_columns_default_to_one_row_per_image_with_backdrops(cli, contact_sheet, tmp_path):
    clear = solid(tmp_path, "hud.png", (0, 0, 0, 0), mode="RGBA")
    result, _, _ = sheet(cli, contact_sheet, tmp_path, clear, clear, "--backdrop", "white", "--backdrop", "black", "--backdrop", "busy", "--cell-width", 100)
    assert result.width == contact_sheet.PADDING + 3 * (100 + contact_sheet.PADDING)


def test_busy_backdrop_is_many_coloured_and_the_same_every_time(contact_sheet):
    first = contact_sheet.busy_backdrop((320, 160))
    assert first.tobytes() == contact_sheet.busy_backdrop((320, 160)).tobytes()
    assert len(first.getcolors(first.width * first.height)) > 20


@pytest.mark.parametrize(
    ("argument", "label"),
    [("{path}", "a"), ("{path}=A phone", "A phone"), ("{path}=x=y", "x=y")],
)
def test_entries_take_an_optional_label(contact_sheet, tmp_path, argument, label):
    path = solid(tmp_path, "a.png", RED)
    assert contact_sheet.parse_entry(argument.format(path=path)) == (path, label)


def test_a_file_name_with_an_equals_sign(contact_sheet, tmp_path):
    path = solid(tmp_path, "a=b.png", RED)
    assert contact_sheet.parse_entry(str(path)) == (path, "a=b")
    assert contact_sheet.parse_entry(f"{path}=Label") == (path, "Label")


def test_long_labels_are_shortened_to_the_cell(contact_sheet):
    font = contact_sheet.label_font()
    text = contact_sheet.fit_text("W" * 200, font, 300)
    assert text.endswith("…")
    assert font.getlength(text) <= 300
    assert contact_sheet.fit_text("Short", font, 300) == "Short"


def test_title_adds_a_band_above_the_grid(cli, contact_sheet, tmp_path):
    image = solid(tmp_path, "a.png", RED)
    plain, _, _ = sheet(cli, contact_sheet, tmp_path, image)
    titled, _, _ = sheet(cli, contact_sheet, tmp_path, image, "--title", "Style tiles")
    assert titled.height > plain.height
    assert titled.width == plain.width


def test_opaque_render_over_a_backdrop_warns(cli, contact_sheet, tmp_path):
    opaque = solid(tmp_path, "opaque.png", RED)
    _, _, stderr = sheet(cli, contact_sheet, tmp_path, opaque, "--backdrop", "black")
    assert "opaque.png" in stderr and "--transparent" in stderr


def test_max_size_shrinks_the_long_side(cli, contact_sheet, tmp_path):
    image = solid(tmp_path, "a.png", RED)
    result, _, _ = sheet(cli, contact_sheet, tmp_path, image, image, "--columns", 2, "--max-size", 400)
    assert max(result.size) == 400


@pytest.mark.parametrize(
    "args",
    [
        ["missing.png"],
        ["{text}"],
        ["{image}", "--backdrop", "missing.png"],
        ["{image}", "--columns", "0"],
        ["{image}", "--cell-width", "0"],
        ["{image}", "--max-size", "0"],
    ],
)
def test_bad_input_exits_2(cli, contact_sheet, tmp_path, monkeypatch, args):
    monkeypatch.chdir(tmp_path)
    image = solid(tmp_path, "a.png", RED)
    text = tmp_path / "notes.png"
    text.write_text("not an image", encoding="utf-8")
    filled = [arg.format(image=image, text=text) for arg in args]
    code, out, err = cli(contact_sheet, *filled, "--out", tmp_path / "sheet.png")
    assert code == 2
    assert out == ""
    assert err
    assert not (tmp_path / "sheet.png").exists()


def test_help_runs_as_a_script(scripts_dir):
    proc = subprocess.run(
        [sys.executable, str(scripts_dir / "contact_sheet.py"), "--help"], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout


def test_missing_pillow_exits_2_with_a_hint(scripts_dir, tmp_path):
    (tmp_path / "PIL").mkdir()
    (tmp_path / "PIL" / "__init__.py").write_text('raise ImportError("Pillow blocked for testing")\n', encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(scripts_dir / "contact_sheet.py"), "--help"], capture_output=True, text=True, env=env
    )
    assert proc.returncode == 2
    assert "Pillow" in proc.stderr
    assert "--with pillow python" in proc.stderr
    assert "Traceback" not in proc.stderr
