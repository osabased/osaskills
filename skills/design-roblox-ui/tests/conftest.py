"""Shared test setup: load the scripts as importable modules."""
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def scripts_dir():
    return SCRIPTS_DIR


@pytest.fixture(scope="session")
def contrast():
    return load_script("contrast")


@pytest.fixture(scope="session")
def theme_guard():
    return load_script("theme_guard")


@pytest.fixture(scope="session")
def contact_sheet():
    return load_script("contact_sheet")


@pytest.fixture(scope="session")
def palette():
    return load_script("palette")


@pytest.fixture()
def cli(capsys):
    """Run a script's main() and return (exit code, stdout, stderr)."""

    def run(module, *args):
        try:
            code = module.main([str(arg) for arg in args])
        except SystemExit as error:
            code = error.code
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return run
