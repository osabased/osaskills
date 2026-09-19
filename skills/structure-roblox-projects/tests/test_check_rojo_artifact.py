from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_rojo_artifact.py"
SPEC = importlib.util.spec_from_file_location("check_rojo_artifact", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def sourcemap(
    include_preview: bool = False,
    duplicate_service: bool = False,
    runtime_name: str = "Runtime",
) -> dict[str, object]:
    client_children: list[dict[str, object]] = [
        {
            "name": runtime_name,
            "className": "ModuleScript",
            "filePaths": [f"src/{runtime_name}.luau"],
        }
    ]
    if include_preview:
        client_children.append(
            {"name": "Preview", "className": "ModuleScript", "filePaths": ["src/Preview/init.luau"]}
        )
    services: list[dict[str, object]] = [
        {
            "name": "ReplicatedStorage",
            "className": "ReplicatedStorage",
            "children": [{"name": "Client", "className": "Folder", "children": client_children}],
        }
    ]
    if duplicate_service:
        services.append(
            {"name": "ReplicatedStorage", "className": "ReplicatedStorage", "children": []}
        )
    return {"name": "Fixture", "className": "DataModel", "children": services}


def rbxlx(
    include_preview: bool = False,
    duplicate_service: bool = False,
    runtime_name: str = "Runtime",
) -> str:
    preview = ""
    if include_preview:
        preview = '<Item class="ModuleScript"><Properties><string name="Name">Preview</string></Properties></Item>'
    second_service = ""
    if duplicate_service:
        second_service = '<Item class="ReplicatedStorage"><Properties><string name="Name">ReplicatedStorage</string></Properties></Item>'
    return f'''<roblox version="4">
<Item class="DataModel"><Properties><string name="Name">Fixture</string></Properties>
  <Item class="ReplicatedStorage"><Properties><string name="Name">ReplicatedStorage</string></Properties>
    <Item class="Folder"><Properties><string name="Name">Client</string></Properties>
      <Item class="ModuleScript"><Properties><string name="Name">{runtime_name}</string></Properties></Item>
      {preview}
    </Item>
  </Item>
  {second_service}
</Item>
</roblox>'''


def service_root_rbxlx() -> str:
    return '''<roblox version="4">
<Item class="ReplicatedStorage"><Properties><string name="Name">ReplicatedStorage</string></Properties>
  <Item class="Folder"><Properties><string name="Name">Client</string></Properties>
    <Item class="ModuleScript"><Properties><string name="Name">Runtime</string></Properties></Item>
  </Item>
</Item>
</roblox>'''


class ArtifactCheckerTests(unittest.TestCase):
    def run_checker(
        self,
        *,
        map_preview: bool = False,
        place_preview: bool = False,
        map_duplicate: bool = False,
        place_duplicate: bool = False,
        runtime_name: str = "Runtime",
    ) -> int:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "fixture.sourcemap.json"
            place_path = root / "fixture.rbxlx"
            map_path.write_text(
                json.dumps(sourcemap(map_preview, map_duplicate, runtime_name)), encoding="utf-8"
            )
            place_path.write_text(
                rbxlx(place_preview, place_duplicate, runtime_name), encoding="utf-8"
            )
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                return CHECKER.main(
                    [
                        "--sourcemap",
                        str(map_path),
                        "--place",
                        str(place_path),
                        "--require-path",
                        "ReplicatedStorage/Client/Runtime",
                        "--forbid-path-fragment",
                        "ReplicatedStorage/Client/Preview",
                        "--singleton-class",
                        "ReplicatedStorage",
                    ]
                )

    def test_accepts_retained_runtime_and_excluded_preview(self) -> None:
        self.assertEqual(0, self.run_checker())

    def test_checks_place_even_when_sourcemap_is_clean(self) -> None:
        self.assertEqual(1, self.run_checker(place_preview=True))

    def test_rejects_duplicate_singleton_service(self) -> None:
        self.assertEqual(1, self.run_checker(map_duplicate=True, place_duplicate=True))

    def test_exact_required_path_rejects_runtimeold_when_runtime_is_missing(self) -> None:
        self.assertEqual(1, self.run_checker(runtime_name="RuntimeOld"))

    def test_service_root_sourcemap_and_unwrapped_place_keep_root_segment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "service.sourcemap.json"
            place_path = root / "service.rbxlx"
            full_map = sourcemap()
            children = full_map.get("children")
            assert isinstance(children, list)
            service_map = children[0]
            map_path.write_text(json.dumps(service_map), encoding="utf-8")
            place_path.write_text(service_root_rbxlx(), encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    0,
                    CHECKER.main(
                        [
                            "--sourcemap",
                            str(map_path),
                            "--place",
                            str(place_path),
                            "--require-path",
                            "ReplicatedStorage/Client/Runtime",
                            "--singleton-class",
                            "ReplicatedStorage",
                        ]
                    ),
                )

    def test_rejects_zero_or_blank_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "fixture.sourcemap.json"
            place_path = root / "fixture.rbxlx"
            map_path.write_text(json.dumps(sourcemap()), encoding="utf-8")
            place_path.write_text(rbxlx(), encoding="utf-8")
            base = ["--sourcemap", str(map_path), "--place", str(place_path)]
            cases = [
                [],
                ["--require-path", "  "],
                ["--require-path-fragment", ""],
                ["--forbid-path-fragment", "///"],
            ]
            for extra in cases:
                with self.subTest(extra=extra):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        self.assertEqual(2, CHECKER.main([*base, *extra]))

    def test_malformed_artifact_returns_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "broken.sourcemap.json"
            place_path = root / "fixture.rbxlx"
            map_path.write_text("{", encoding="utf-8")
            place_path.write_text(rbxlx(), encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    2,
                    CHECKER.main(
                        [
                            "--sourcemap",
                            str(map_path),
                            "--place",
                            str(place_path),
                            "--require-path",
                            "ReplicatedStorage/Client/Runtime",
                        ]
                    ),
                )

    @unittest.skipUnless(shutil.which("rojo"), "Rojo is not installed")
    def test_rojo_thin_profiles_keep_development_and_exclude_it_from_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = root / "src" / "client"
            preview = client / "Preview"
            preview.mkdir(parents=True)
            (client / "Runtime.luau").write_text("return {}\n", encoding="utf-8")
            (client / "Button.story.luau").write_text("return {}\n", encoding="utf-8")
            (preview / "init.luau").write_text("return {}\n", encoding="utf-8")

            common_project = {
                "name": "Fixture",
                "tree": {
                    "$className": "DataModel",
                    "ReplicatedStorage": {
                        "$className": "ReplicatedStorage",
                        "Client": {"$path": "src/client"},
                    },
                },
            }
            development_project = {
                "name": "Fixture Development",
                "tree": {"$path": "common.project.json"},
            }
            release_project = {
                "name": "Fixture Release",
                "globIgnorePaths": [
                    "**/*.story.luau",
                    "**/Preview",
                    "**/Preview/**",
                ],
                "tree": {"$path": "common.project.json"},
            }
            (root / "rokit.toml").write_text(
                '[tools]\nrojo = "rojo-rbx/rojo@7.7.0"\n', encoding="utf-8"
            )
            for name, project in (
                ("common.project.json", common_project),
                ("development.project.json", development_project),
                ("release.project.json", release_project),
            ):
                (root / name).write_text(json.dumps(project), encoding="utf-8")

            artifacts: dict[str, tuple[Path, Path]] = {}
            for profile in ("development", "release"):
                sourcemap_path = root / f"{profile}.sourcemap.json"
                place_path = root / f"{profile}.rbxlx"
                sourcemap_result = subprocess.run(
                    ["rojo", "sourcemap", f"{profile}.project.json", "-o", str(sourcemap_path)],
                    cwd=root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, sourcemap_result.returncode, sourcemap_result.stderr)
                build_result = subprocess.run(
                    ["rojo", "build", f"{profile}.project.json", "-o", str(place_path)],
                    cwd=root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, build_result.returncode, build_result.stderr)
                artifacts[profile] = (sourcemap_path, place_path)

            development_map, development_place = artifacts["development"]
            self.assertEqual(
                [],
                CHECKER.check_artifacts(
                    {
                        "sourcemap": CHECKER.read_sourcemap(development_map),
                        "place": CHECKER.read_rbxlx(development_place),
                    },
                    required_paths=[
                        "ReplicatedStorage/Client/Runtime",
                        "ReplicatedStorage/Client/Preview",
                        "ReplicatedStorage/Client/Button.story",
                    ],
                    singleton_classes=["ReplicatedStorage"],
                ),
            )

            release_map, release_place = artifacts["release"]
            self.assertEqual(
                [],
                CHECKER.check_artifacts(
                    {
                        "sourcemap": CHECKER.read_sourcemap(release_map),
                        "place": CHECKER.read_rbxlx(release_place),
                    },
                    required_paths=["ReplicatedStorage/Client/Runtime"],
                    forbidden_fragments=["ReplicatedStorage/Client/Preview", ".story"],
                    singleton_classes=["ReplicatedStorage"],
                ),
            )


if __name__ == "__main__":
    unittest.main()
