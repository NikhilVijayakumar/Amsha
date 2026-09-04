# -*- mode: python ; coding: utf-8 -*-
# Run via build_standalone.py (from the dedicated packaging venv, which has
# amsha_mcp installed) — imports amsha_mcp here purely to locate its bundled
# docs/ folder on disk so PyInstaller can package it as data.
import os
from pathlib import Path

import amsha_mcp

pkg_root = Path(amsha_mcp.__file__).resolve().parent
docs_dir = pkg_root / "docs"
build_name = os.environ.get("AMSHA_MCP_BUILD_NAME", "amsha-mcp")

a = Analysis(
    ['entrypoint.py'],
    pathex=[],
    binaries=[],
    datas=[(str(docs_dir), 'amsha_mcp/docs')],
    hiddenimports=['mcp.server.fastmcp', 'mcp.server.stdio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=build_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=build_name,
)
