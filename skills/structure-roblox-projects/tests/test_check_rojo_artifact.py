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


def rojo_runs() -> bool:
    """True when `rojo` runs outside a toolchain project; a bare rokit/aftman shim does not."""
    if not shutil.which("rojo"):
        return False
    with tempfile.TemporaryDirectory() as directory:
        try:
            result = subprocess.run(["rojo", "--version"], cwd=directory, check=False, capture_output=True, text=True)
        except OSError:
            return False
    return result.returncode == 0


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

    def test_null_sourcemap_names_the_non_scripts_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "empty.sourcemap.json"
            map_path.write_text("null", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "--include-non-scripts"):
                CHECKER.read_sourcemap(map_path)

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

    @unittest.skipUnless(rojo_runs(), "Rojo is not runnable here")
    def test_rojo_thin_profiles_keep_development_and_exclude_it_from_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = root / "src" / "client"
            preview = client / "Preview"
            preview.mkdir(parents=True)
            (client / "Runtime.luau").write_text("return {}\n", encoding="utf-8")
            (client / "Button.story.luau").write_text("return {}\n", encoding="utf-8")
            (preview / "init.luau").write_text("return {}\n", encoding="utf-8")
            (preview / "Child.luau").write_text("return {}\n", encoding="utf-8")

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
                        "ReplicatedStorage/Client/Preview/Child",
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

    @unittest.skipUnless(rojo_runs(), "Rojo is not runnable here")
    def test_rojo_service_beside_root_path_duplicates_only_in_the_place_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = root / "src" / "client"
            client.mkdir(parents=True)
            (client / "Runtime.luau").write_text("return {}\n", encoding="utf-8")
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
            wrapper_project = {
                "name": "Fixture Wrapper",
                "tree": {
                    "$path": "common.project.json",
                    "ReplicatedStorage": {"$className": "ReplicatedStorage"},
                },
            }
            (root / "common.project.json").write_text(json.dumps(common_project), encoding="utf-8")
            (root / "wrapper.project.json").write_text(json.dumps(wrapper_project), encoding="utf-8")
            sourcemap_path = root / "wrapper.sourcemap.json"
            place_path = root / "wrapper.rbxlx"
            for command in (
                ["rojo", "sourcemap", "wrapper.project.json", "-o", str(sourcemap_path)],
                ["rojo", "build", "wrapper.project.json", "-o", str(place_path)],
            ):
                result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)

            failures = CHECKER.check_artifacts(
                {
                    "sourcemap": CHECKER.read_sourcemap(sourcemap_path),
                    "place": CHECKER.read_rbxlx(place_path),
                },
                singleton_classes=["ReplicatedStorage"],
            )
            self.assertEqual(["place: expected exactly one ReplicatedStorage, found 2"], failures)

    @unittest.skipUnless(rojo_runs(), "Rojo is not runnable here")
    def test_rojo_client_script_in_replicated_storage_needs_client_run_context(self) -> None:
        local_script = "'ReplicatedStorage/Shared' is a LocalScript, expected Script"
        for emit_legacy, client_failures, server_context in (
            (True, [f"sourcemap: {local_script}", f"place: {local_script}"], "Legacy"),
            (False, [], "Server"),
        ):
            with self.subTest(emitLegacyScripts=emit_legacy), tempfile.TemporaryDirectory() as directory:
                sourcemap_path, place_path = build_script_fixture(Path(directory), emit_legacy)
                artifacts = {
                    "sourcemap": CHECKER.read_sourcemap(sourcemap_path),
                    "place": CHECKER.read_rbxlx(place_path),
                }
                self.assertEqual(
                    client_failures,
                    CHECKER.check_artifacts(
                        artifacts,
                        required_classes=[
                            "ReplicatedStorage/Shared=Script:Client",
                            f"ServerScriptService/Server/Main=Script:{server_context}",
                            "ServerScriptService/Server/Util=ModuleScript",
                        ],
                    ),
                )

    @unittest.skipUnless(rojo_runs(), "Rojo is not runnable here")
    def test_rojo_wrong_run_context_fails_only_in_the_place(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sourcemap_path, place_path = build_script_fixture(Path(directory), False)
            failures = CHECKER.check_artifacts(
                {
                    "sourcemap": CHECKER.read_sourcemap(sourcemap_path),
                    "place": CHECKER.read_rbxlx(place_path),
                },
                required_classes=["ReplicatedStorage/Shared=Script:Server"],
            )
            self.assertEqual(
                ["place: 'ReplicatedStorage/Shared' has RunContext Client, expected Server"],
                failures,
            )

    @unittest.skipUnless(rojo_runs(), "Rojo is not runnable here")
    def test_rojo_sourcemap_keeps_remotes_only_with_non_scripts_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "src" / "shared"
            (shared / "Remotes").mkdir(parents=True)
            (shared / "Util.luau").write_text("return {}\n", encoding="utf-8")
            (shared / "Remotes" / "Buy.model.json").write_text(
                json.dumps({"className": "RemoteEvent"}), encoding="utf-8"
            )
            project = {
                "name": "Fixture",
                "tree": {
                    "$className": "DataModel",
                    "ReplicatedStorage": {
                        "$className": "ReplicatedStorage",
                        "Shared": {"$path": "src/shared"},
                    },
                },
            }
            (root / "default.project.json").write_text(json.dumps(project), encoding="utf-8")
            place_path = root / "fixture.rbxlx"
            result = subprocess.run(
                ["rojo", "build", "-o", str(place_path)], cwd=root, check=False, capture_output=True, text=True
            )
            self.assertEqual(0, result.returncode, result.stderr)
            missing = "sourcemap: 'ReplicatedStorage/Shared/Remotes/Buy' is missing"
            for flags, expected in (([], [missing]), (["--include-non-scripts"], [])):
                with self.subTest(flags=flags):
                    sourcemap_path = root / "sourcemap.json"
                    result = subprocess.run(
                        ["rojo", "sourcemap", *flags, "-o", str(sourcemap_path)],
                        cwd=root,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual(
                        expected,
                        CHECKER.check_artifacts(
                            {
                                "sourcemap": CHECKER.read_sourcemap(sourcemap_path),
                                "place": CHECKER.read_rbxlx(place_path),
                            },
                            required_classes=["ReplicatedStorage/Shared/Remotes/Buy=RemoteEvent"],
                        ),
                    )


def build_script_fixture(directory: Path, emit_legacy: bool) -> tuple[Path, Path]:
    shared = directory / "src" / "shared"
    server = directory / "src" / "server"
    shared.mkdir(parents=True)
    server.mkdir(parents=True)
    (shared / "init.client.luau").write_text("print('client')\n", encoding="utf-8")
    (server / "Main.server.luau").write_text("print('server')\n", encoding="utf-8")
    (server / "Util.luau").write_text("return {}\n", encoding="utf-8")
    project = {
        "name": "Fixture",
        "emitLegacyScripts": emit_legacy,
        "tree": {
            "$className": "DataModel",
            "ReplicatedStorage": {
                "$className": "ReplicatedStorage",
                "Shared": {"$path": "src/shared"},
            },
            "ServerScriptService": {
                "$className": "ServerScriptService",
                "Server": {"$path": "src/server"},
            },
        },
    }
    (directory / "default.project.json").write_text(json.dumps(project), encoding="utf-8")
    sourcemap_path = directory / "fixture.sourcemap.json"
    place_path = directory / "fixture.rbxlx"
    for command in (
        ["rojo", "sourcemap", "default.project.json", "-o", str(sourcemap_path)],
        ["rojo", "build", "default.project.json", "-o", str(place_path)],
    ):
        result = subprocess.run(command, cwd=directory, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            raise AssertionError(result.stderr)
    return sourcemap_path, place_path


def script_sourcemap() -> dict[str, object]:
    return {
        "name": "Fixture",
        "className": "DataModel",
        "children": [
            {
                "name": "ReplicatedStorage",
                "className": "ReplicatedStorage",
                "children": [
                    {"name": "Shared", "className": "LocalScript"},
                    {"name": "Twin", "className": "ModuleScript"},
                    {"name": "Twin", "className": "ModuleScript"},
                ],
            },
            {
                "name": "ServerScriptService",
                "className": "ServerScriptService",
                "children": [
                    {"name": "Main", "className": "Script"},
                    {"name": "Old", "className": "Script"},
                ],
            },
        ],
    }


def script_rbxlx() -> str:
    return '''<roblox version="4">
<Item class="ReplicatedStorage"><Properties><string name="Name">ReplicatedStorage</string></Properties>
  <Item class="LocalScript"><Properties><string name="Name">Shared</string></Properties></Item>
  <Item class="ModuleScript"><Properties><string name="Name">Twin</string></Properties></Item>
  <Item class="ModuleScript"><Properties><string name="Name">Twin</string></Properties></Item>
</Item>
<Item class="ServerScriptService"><Properties><string name="Name">ServerScriptService</string></Properties>
  <Item class="Script"><Properties><string name="Name">Main</string><token name="RunContext">1</token></Properties></Item>
  <Item class="Script"><Properties><string name="Name">Old</string></Properties></Item>
</Item>
</roblox>'''


class RequireClassTests(unittest.TestCase):
    def check(self, *requirements: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "fixture.sourcemap.json"
            place_path = root / "fixture.rbxlx"
            map_path.write_text(json.dumps(script_sourcemap()), encoding="utf-8")
            place_path.write_text(script_rbxlx(), encoding="utf-8")
            arguments = ["--sourcemap", str(map_path), "--place", str(place_path)]
            for requirement in requirements:
                arguments += ["--require-class", requirement]
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                code = CHECKER.main(arguments)
            return code, stderr.getvalue()

    def test_accepts_matching_classes_and_run_contexts(self) -> None:
        code, stderr = self.check(
            "ReplicatedStorage/Shared=LocalScript",
            "ServerScriptService/Main=Script:Server",
            "ServerScriptService/Old=Script:Legacy",
            "/ServerScriptService/Main/=Script",
        )
        self.assertEqual((0, ""), (code, stderr))

    def test_rejects_wrong_class_in_both_artifacts(self) -> None:
        code, stderr = self.check("ReplicatedStorage/Shared=Script:Client")
        self.assertEqual(1, code)
        self.assertIn("sourcemap: 'ReplicatedStorage/Shared' is a LocalScript, expected Script", stderr)
        self.assertIn("place: 'ReplicatedStorage/Shared' is a LocalScript, expected Script", stderr)

    def test_rejects_wrong_run_context_in_place_only(self) -> None:
        code, stderr = self.check("ServerScriptService/Main=Script:Client")
        self.assertEqual(1, code)
        self.assertNotIn("sourcemap:", stderr)
        self.assertIn("place: 'ServerScriptService/Main' has RunContext Server, expected Client", stderr)

    def test_script_without_run_context_reads_as_legacy(self) -> None:
        code, stderr = self.check("ServerScriptService/Old=Script:Server")
        self.assertEqual(1, code)
        self.assertIn("has RunContext Legacy, expected Server", stderr)

    def test_rejects_missing_and_ambiguous_paths(self) -> None:
        code, stderr = self.check(
            "ReplicatedStorage/Missing=ModuleScript", "ReplicatedStorage/Twin=ModuleScript"
        )
        self.assertEqual(1, code)
        self.assertIn("place: 'ReplicatedStorage/Missing' is missing", stderr)
        self.assertIn(
            "sourcemap: 'ReplicatedStorage/Twin' names 2 instances; a class check needs exactly one",
            stderr,
        )

    def test_rejects_malformed_requirements(self) -> None:
        for requirement in (
            "ReplicatedStorage/Shared",
            "=LocalScript",
            "ReplicatedStorage/Shared=",
            "ReplicatedStorage/Shared=Script:",
            "ReplicatedStorage/Shared=LocalScript:Client",
            "ReplicatedStorage/Shared=Script:client",
        ):
            with self.subTest(requirement=requirement):
                code, stderr = self.check(requirement)
                self.assertEqual(2, code)
                self.assertIn("--require-class", stderr)


if __name__ == "__main__":
    unittest.main()
