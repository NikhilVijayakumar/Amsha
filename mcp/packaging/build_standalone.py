"""Build a standalone amsha-mcp bundle AND the Windows installer in one shot:
fresh venv -> pip install ./mcp (non-editable) + pyinstaller -> freeze
entrypoint.py --onedir -> compile amsha_mcp_installer.iss (if ISCC.exe is
found). Zero dependency on E:\\Python\\Amsha's dev venv; only mcp/pyproject.toml's
own declared deps land in the frozen bundle.

Config: build_config.json (output_dir, build_venv_dir, onedir_name).
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MCP_DIR = HERE.parent
CONFIG = json.loads((HERE / "build_config.json").read_text(encoding="utf-8"))


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def main():
    out_dir = Path(CONFIG["output_dir"])
    venv_dir = Path(CONFIG["build_venv_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    print(f"Creating build venv at {venv_dir}")
    import venv as venv_mod
    venv_mod.create(venv_dir, with_pip=True)
    py = venv_dir / "Scripts" / "python.exe"

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

    exe = dist_dir / CONFIG["onedir_name"] / (CONFIG["onedir_name"] + ".exe")
    print(f"\nStandalone build at: {dist_dir / CONFIG['onedir_name']}")
    print(f"Run it directly: {exe}")

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
