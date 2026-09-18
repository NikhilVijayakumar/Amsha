"""Build a standalone amsha-mcp bundle (and, on Windows, the Inno Setup
installer) in one shot:

    fresh venv → pip install ./mcp (non-editable) + pyinstaller → freeze
    entrypoint.py --onedir → compile amsha_mcp_installer.iss (Windows only,
    if ISCC.exe is found). Zero dependency on the repo's dev venv; only
    mcp/pyproject.toml's own declared deps land in the frozen bundle.

Config: build_config.json — platform-specific output_dir / build_venv_dir
live under the "platforms" key; top-level values are the Windows defaults
(backward-compatible with the existing .iss literal paths).
"""
import json
import os
import shutil
import subprocess
import sys
import venv as venv_mod
from pathlib import Path

HERE = Path(__file__).resolve().parent
MCP_DIR = HERE.parent
CONFIG = json.loads((HERE / "build_config.json").read_text(encoding="utf-8"))
IS_WINDOWS = sys.platform.startswith("win")

PLATFORM_KEY = "windows" if IS_WINDOWS else "linux"


def _platform_override() -> dict | None:
    return CONFIG.get("platforms", {}).get(PLATFORM_KEY)


def _out_dir() -> Path:
    p = _platform_override()
    return Path(p["output_dir"]) if p and "output_dir" in p else Path(CONFIG["output_dir"])


def _venv_dir() -> Path:
    p = _platform_override()
    if p and "build_venv_dir" in p:
        return Path(p["build_venv_dir"])
    if p and "output_dir" in p:
        return Path(p["output_dir"]) / ".build-venv"
    return Path(CONFIG["build_venv_dir"])


def _venv_python(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python")


def _dist_exe(dist_dir: Path, name: str) -> Path:
    return dist_dir / name / (name + (".exe" if IS_WINDOWS else ""))


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def main():
    out_dir = _out_dir()
    venv_dir = _venv_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    print(f"Creating build venv at {venv_dir}")
    venv_mod.create(venv_dir, with_pip=True)
    py = _venv_python(venv_dir)

    run([str(py), "-m", "pip", "install", "--no-cache-dir", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "--no-cache-dir", str(MCP_DIR)])
    run([str(py), "-m", "pip", "install", "--no-cache-dir", "pyinstaller"])

    dist_dir = out_dir / "dist"
    build_dir = out_dir / "build"
    for d in (dist_dir, build_dir):
        if d.exists():
            shutil.rmtree(d)

    env = dict(os.environ)
    env["AMSHA_MCP_BUILD_NAME"] = CONFIG["onedir_name"]

    run([str(py), "-m", "PyInstaller",
         str(HERE / "amsha_mcp.spec"),
         "--distpath", str(dist_dir),
         "--workpath", str(build_dir),
         "--noconfirm"],
        cwd=str(HERE), env=env)

    exe = _dist_exe(dist_dir, CONFIG["onedir_name"])
    print(f"\nStandalone build at: {dist_dir / CONFIG['onedir_name']}")
    print(f"Run it directly: {exe}")

    if not IS_WINDOWS:
        print(f"\nLinux: standalone folder is the distribution.")
        print(f"Register with MCP client:")
        print(f"  claude mcp add amsha-mcp -s local -- \"{exe}\"")
        return

    iscc = _find_iscc()
    if not iscc:
        print("\nISCC.exe (Inno Setup) not found — skipping installer compile.")
        print(f"Compile manually: ISCC.exe {HERE / 'amsha_mcp_installer.iss'}")
        return

    run([str(iscc), str(HERE / "amsha_mcp_installer.iss")])
    installer_dir = out_dir / "installer"
    built = sorted(installer_dir.glob("*.exe")) if installer_dir.is_dir() else []
    if built:
        print(f"\nInstaller built: {built[-1]}")


def _find_iscc() -> Path | None:
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    found = shutil.which("ISCC.exe") or shutil.which("iscc")
    return Path(found) if found else None


if __name__ == "__main__":
    main()
