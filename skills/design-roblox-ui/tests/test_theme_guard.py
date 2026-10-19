"""theme_guard.py: raw colours, fonts and text sizes outside the theme, and the command line."""
import subprocess
import sys

import pytest


def values(theme_guard, source):
    return [(line.number, line.values) for line in theme_guard.scan(source)]


@pytest.mark.parametrize(
    ("source", "value"),
    [
        ("local c = Color3.new(1, 0, 0)", "raw colour Color3.new"),
        ("local c = Color3.fromRGB(255, 0, 0)", "raw colour Color3.fromRGB"),
        ('local c = Color3.fromHex("#FF0000")', "raw colour Color3.fromHex"),
        ('local c = Color3.fromHex"#FF0000"', "raw colour Color3.fromHex"),
        ("local c = Color3.fromHSV(0, 1, 1)", "raw colour Color3.fromHSV"),
        ("local c = Color3 . fromRGB (255, 0, 0)", "raw colour Color3.fromRGB"),
        ("local toColour = Color3.fromRGB", "raw colour Color3.fromRGB"),
        ('part.BrickColor = BrickColor.new("Bright red")', "raw colour BrickColor"),
        ('local f = Font.new("rbxasset://fonts/families/GothamSSm.json")', "raw font Font.new"),
        ('local f = Font.fromName("Gotham")', "raw font Font.fromName"),
        ("local f = Font.fromId(12187365364)", "raw font Font.fromId"),
        ("label.Font = Enum.Font.GothamBold", "raw font Enum.Font"),
        ("TextSize = 18,", "raw text size TextSize=18"),
        ("label.TextSize = 14.5", "raw text size TextSize=14.5"),
        ("MinTextSize = 12,", "raw text size MinTextSize=12"),
        ("constraint.MaxTextSize=30", "raw text size MaxTextSize=30"),
    ],
)
def test_each_raw_value_is_found(theme_guard, source, value):
    assert values(theme_guard, source) == [(1, [value])]


def test_values_on_one_line_are_listed_in_order(theme_guard):
    source = "label.FontFace = Font.fromEnum(Enum.Font.Gotham); label.TextSize = 18"
    assert values(theme_guard, source) == [(1, ["raw font Font.fromEnum", "raw font Enum.Font", "raw text size TextSize=18"])]


@pytest.mark.parametrize(
    "source",
    [
        "TextSize = theme.text.body,",
        "if label.TextSize == 18 then end",
        "if label.TextSize >= 18 then end",
        "TextColor3 = theme.colour.text,",
        "BackgroundColor3 = theme.colour.surface:Lerp(theme.colour.surfaceRaised, 0.5),",
        "local colour: Color3 = theme.colour.text",
        "local font: Enum.Font = theme.font.body",
        "local tint = part.BrickColor.Color",
        "local weight = Enum.FontWeight.Bold",
    ],
)
def test_theme_reads_types_and_comparisons_pass(theme_guard, source):
    assert values(theme_guard, source) == []


def test_comments_are_skipped(theme_guard):
    source = "\n".join(
        [
            "-- Color3.fromRGB(1, 2, 3)",
            "--[[ Enum.Font.Gotham ]]",
            "--[==[",
            "TextSize = 18",
            "]] still a comment: BrickColor.new()",
            "]==]",
            "local x = 1 -- Font.new()",
        ]
    )
    assert values(theme_guard, source) == []


def test_strings_are_skipped(theme_guard):
    source = "\n".join(
        [
            'local a = "Color3.fromRGB(1, 2, 3)"',
            "local b = 'Enum.Font.Gotham'",
            "local c = [[TextSize = 18]]",
            "local d = [=[ ]] BrickColor.new() ]=]",
            'local e = "a \\" Color3.new(1, 1, 1)"',
            "local f = 'it\\'s Font.new'",
            "local g = `Font.new {name}`",
        ]
    )
    assert values(theme_guard, source) == []


def test_a_string_holding_two_dashes_is_not_a_comment(theme_guard):
    assert values(theme_guard, 'print("--", Color3.new(1, 1, 1))') == [(1, ["raw colour Color3.new"])]


def test_code_after_an_escaped_backslash_is_checked(theme_guard):
    source = 'local s = "\\\\" .. tostring(Color3.new(1, 1, 1))'
    assert values(theme_guard, source) == [(1, ["raw colour Color3.new"])]


def test_strings_that_continue_onto_the_next_line(theme_guard):
    source = "\n".join(
        [
            'local a = "one\\z',
            '           Color3.new(1, 1, 1)"',
            'local b = "two\\',
            'Enum.Font.Gotham"',
            "local c = Color3.new(0, 0, 0)",
        ]
    )
    assert values(theme_guard, source) == [(5, ["raw colour Color3.new"])]


def test_an_unterminated_string_ends_at_the_newline(theme_guard):
    assert values(theme_guard, 'local s = "oops\nlocal c = Color3.new(1, 1, 1)') == [(2, ["raw colour Color3.new"])]


def test_interpolated_expressions_are_checked(theme_guard):
    source = "\n".join(
        [
            "local a = `{Color3.new(1, 0, 0)}`",
            "local b = `outer {`inner {Color3.fromRGB(1, 2, 3)}`} text`",
            "local c = `{ {1} } Enum.Font.Gotham`",
            "local d = `\\{Color3.new(1, 1, 1)}`",
            "local e = `\\u{41} Font.new`",
        ]
    )
    assert values(theme_guard, source) == [(1, ["raw colour Color3.new"]), (2, ["raw colour Color3.fromRGB"])]


def test_line_numbers_survive_block_comments_and_long_strings(theme_guard):
    source = "--[[\nline 2\n]]\nlocal s = [[\nline 5\n]]\nlocal c = Color3.new(1, 1, 1)"
    assert values(theme_guard, source) == [(7, ["raw colour Color3.new"])]


def test_allow_marker_with_a_reason_skips_the_line(theme_guard):
    assert values(theme_guard, "local red = Color3.fromRGB(200, 0, 0) -- theme-guard: allow logo red") == []


@pytest.mark.parametrize("marker", ["-- theme-guard: allow", "--theme-guard:allow   "])
def test_allow_marker_needs_a_reason(theme_guard, marker):
    (line,) = theme_guard.scan(f"local red = Color3.fromRGB(200, 0, 0) {marker}")
    assert line.values == ["raw colour Color3.fromRGB"]
    assert line.needs_reason


def test_allow_marker_counts_only_in_a_comment_on_the_same_line(theme_guard):
    in_string = 'print("-- theme-guard: allow logo red", Color3.new(1, 0, 0))'
    line_above = "-- theme-guard: allow logo red\nlocal red = Color3.new(1, 0, 0)"
    assert values(theme_guard, in_string) == [(1, ["raw colour Color3.new"])]
    assert values(theme_guard, line_above) == [(2, ["raw colour Color3.new"])]


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ui = tmp_path / "src" / "UI"
    (ui / "drafts").mkdir(parents=True)
    (ui / "Theme.luau").write_text("return { accent = Color3.fromHex(\"B54A24\") }\n", encoding="utf-8")
    (ui / "Button.luau").write_text(
        "--!strict\nlocal theme = require(script.Parent.Theme)\n"
        "return { BackgroundColor3 = theme.accent, TextSize = 18 }\n",
        encoding="utf-8",
    )
    (ui / "Label.lua").write_text("label.FontFace = Font.fromEnum(Enum.Font.Gotham)\n", encoding="utf-8")
    (ui / "drafts" / "TileA.luau").write_text("return { surface = Color3.fromRGB(243, 233, 210) }\n", encoding="utf-8")
    (ui / "notes.md").write_text("Color3.new(1, 1, 1)\n", encoding="utf-8")
    return tmp_path


def test_report_lists_each_line_then_a_summary(cli, theme_guard, project):
    code, out, err = cli(theme_guard, "src/UI", "--allow", "src/UI/Theme.luau", "--allow", "drafts")
    assert code == 1, err
    assert out.splitlines() == [
        "src/UI/Button.luau:3: raw text size TextSize=18: return { BackgroundColor3 = theme.accent, TextSize = 18 }",
        "src/UI/Label.lua:1: raw font Font.fromEnum, raw font Enum.Font: label.FontFace = Font.fromEnum(Enum.Font.Gotham)",
        "theme_guard: 3 raw values in 2 files. Take them from the theme module, "
        'or mark a real one-off with "-- theme-guard: allow <reason>".',
    ]


def test_a_reasonless_marker_is_reported(cli, theme_guard, project):
    (project / "src" / "UI" / "Button.luau").write_text("TextSize = 18 -- theme-guard: allow\n", encoding="utf-8")
    code, out, _ = cli(theme_guard, "src/UI/Button.luau")
    assert code == 1
    assert out.splitlines()[0].endswith(" (an allow marker needs a reason)")
    assert out.splitlines()[-1].startswith("theme_guard: 1 raw value in 1 file.")


def test_clean_files_pass(cli, theme_guard, project):
    (project / "src" / "UI" / "Button.luau").write_text("return { TextSize = theme.text.body }\n", encoding="utf-8")
    code, out, _ = cli(theme_guard, "src/UI/Button.luau", "src/UI/Theme.luau", "--allow", "Theme.luau")
    assert code == 0
    assert out == "theme_guard: 1 file checked, no raw values.\n"


@pytest.mark.parametrize("glob", ["src\\UI\\Theme.luau", "./src/UI/Theme.luau", "*.luau"])
def test_allow_globs_are_normalized(cli, theme_guard, project, glob):
    code, out, _ = cli(theme_guard, "src/UI/Theme.luau", "--allow", glob)
    assert code == 0
    assert out == "theme_guard: 0 files checked, no raw values.\n"


def test_an_explicit_file_is_checked_whatever_its_extension(cli, theme_guard, project):
    code, out, _ = cli(theme_guard, "src/UI/notes.md")
    assert code == 1
    assert out.startswith("src/UI/notes.md:1: raw colour Color3.new: ")


def test_a_folder_scan_skips_other_files(cli, theme_guard, project):
    (project / "docs").mkdir()
    (project / "docs" / "notes.md").write_text("Color3.new(1, 1, 1)\n", encoding="utf-8")
    code, out, err = cli(theme_guard, "docs")
    assert code == 2
    assert out == ""
    assert "docs" in err and "no .luau or .lua files" in err


@pytest.mark.parametrize("path", ["src/Missing", "src/UI/Missing.luau"])
def test_a_missing_path_exits_2(cli, theme_guard, project, path):
    code, out, err = cli(theme_guard, path)
    assert code == 2
    assert out == ""
    assert path in err


def test_a_file_that_is_not_utf8_exits_2(cli, theme_guard, project):
    (project / "src" / "UI" / "Bad.luau").write_bytes(b"local s = '\xff'\n")
    code, _, err = cli(theme_guard, "src/UI/Bad.luau")
    assert code == 2
    assert "Bad.luau" in err


def test_help_runs_as_a_script(scripts_dir):
    proc = subprocess.run(
        [sys.executable, str(scripts_dir / "theme_guard.py"), "--help"], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout
