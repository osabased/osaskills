"""Build ml4-probe.rbxl: ModuleLoader built from the pinned 4.0.0 commit, plus the probe modules.

Needs Python 3.9+, network access and Rojo 7.7 (on PATH, or pass --rojo PATH).
    python build.py [--rojo PATH]
"""
import argparse, io, shutil, subprocess, tarfile, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMIT = "1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8"  # ModuleLoader v4.0.0, as pinned in ssa-bootstrap.md
TARBALL = f"https://codeload.github.com/ActualFire-Games/module-loader/tar.gz/{COMMIT}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rojo", default=shutil.which("rojo") or "rojo")
    rojo = ap.parse_args().rojo
    vendor = ROOT / "vendor"
    vendor.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, urllib.request.urlopen(TARBALL, timeout=60) as response:
        with tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz") as archive:
            archive.extractall(tmp, filter="data")
        (source,) = Path(tmp).iterdir()
        # The release .rbxm is a starter bundle (UngroupIn... models); its ModuleLoader is this module.
        subprocess.run([rojo, "build", str(source), "-o", str(vendor / "ModuleLoader.rbxm")], check=True)
    subprocess.run([rojo, "build", str(ROOT), "-o", str(ROOT / "ml4-probe.rbxl")], check=True)
    print(f"built {ROOT / 'ml4-probe.rbxl'}")


if __name__ == "__main__":
    main()
