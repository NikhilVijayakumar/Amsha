"""Verify the wheel and source archive contain the intended Amsha package."""
from __future__ import annotations

import argparse
import email
import tarfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(directory: Path) -> None:
    wheels = list(directory.glob("*.whl"))
    sources = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError("Expected exactly one wheel and one source archive")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    expected = {path.relative_to(ROOT / "src/nikhil").as_posix() for path in (ROOT / "src/nikhil/amsha").rglob("*.py")}
    with zipfile.ZipFile(wheels[0]) as wheel:
        names = set(wheel.namelist())
        packaged = {name for name in names if name.startswith("amsha/") and name.endswith(".py")}
        if expected != packaged:
            raise ValueError(f"Wheel source mismatch: missing={sorted(expected-packaged)}, unexpected={sorted(packaged-expected)}")
        metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one metadata file")
        data = email.message_from_bytes(wheel.read(metadata[0]))
        if data["Name"].lower() != project["name"].lower() or data["Version"] != project["version"]:
            raise ValueError("Wheel metadata does not match pyproject.toml")
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise ValueError("Wheel is missing LICENSE")
        _check_paths(names)
    with tarfile.open(sources[0], "r:gz") as source:
        names = set(source.getnames())
        for filename in ("LICENSE", "README.md", "pyproject.toml"):
            if not any(name.endswith("/" + filename) for name in names):
                raise ValueError(f"Source archive is missing {filename}")
        _check_paths(names)
    print(f"Verified {wheels[0].name} and {sources[0].name}")


def _check_paths(names: set[str]) -> None:
    forbidden = {name for name in names if any(part in {".git", "__pycache__", ".env"} or part.startswith(".env.") for part in name.split("/"))}
    if forbidden:
        raise ValueError(f"Unexpected private or generated files: {sorted(forbidden)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    check(parser.parse_args().directory)
