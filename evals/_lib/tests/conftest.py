"""Make evals/_lib importable from these tests the way harnesses import it: by path, not as a package."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
