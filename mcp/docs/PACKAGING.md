# Amsha MCP — Packaging, Building, and Installing

How to turn `mcp/` into a standalone platform-native bundle (Windows installer or Linux folder), and how to install/use the result. See [proposal 08](../src/amsha_mcp/docs/proposal/08-standalone-repo-agnostic-server.md) for why this is architected as a repo-agnostic, zero-`amsha`-dependency server in the first place.

The build script (`build_standalone.py`) is platform-aware and runs on both Windows and Linux; the per-platform output paths live in `build_config.json`.

## What gets built

1. **Standalone frozen app** (PyInstaller `--onedir`) — bundles the Python interpreter, `mcp` SDK, `PyYAML`, `pydantic`, and `amsha_mcp`'s own methodology docs into one self-contained folder. No system Python required to run it. Zero dependency on the dev venv or the `amsha`/`crewai` packages at build time.
2. **Windows only:** an **Inno Setup installer** — wraps that folder into a normal double-click `.exe` installer with a Start Menu entry and a real uninstaller. On Linux there is no installer step: the `--onedir` folder *is* the distribution, and the build script prints a one-line `claude mcp add` registration command.

## One-time setup (build machine only)

- Python 3.12–3.13 (any install; the build script makes its own fresh venv, doesn't touch your dev venv).
- Windows only: Inno Setup 6, for the installer compile step:
  ```
  winget install --id JRSoftware.InnoSetup --silent --accept-package-agreements --accept-source-agreements
  ```
  If you skip this, the build script still produces the standalone folder — it just prints the manual `ISCC.exe` command instead of compiling the installer for you.

## Build

The same script works on both OSes — it reads its paths from the per-platform block in `build_config.json` and uses the correct venv layout (`Scripts/python.exe` vs `bin/python`), so there is nothing to pass:

```powershell
E:\Python\Amsha\.venv\Scripts\python.exe E:\Python\Amsha\mcp\packaging\build_standalone.py
```

```bash
python3 /home/dell/PycharmProjects/Amsha/mcp/packaging/build_standalone.py
```

One command does everything:
1. Deletes and recreates a fresh venv under the configured `build_venv_dir`.
2. `pip install ./mcp` into it — non-editable, so it's a real standalone copy built from whatever's currently in `mcp/pyproject.toml`/`mcp/src`, not a live link back to this checkout.
3. `pip install pyinstaller`.
4. Freezes `mcp/packaging/entrypoint.py` per `mcp/packaging/amsha_mcp.spec` into `--onedir` output.
5. Windows only: finds `ISCC.exe` (checks the common install paths, then `PATH`) and compiles `mcp/packaging/amsha_mcp_installer.iss` against that fresh build. Linux: skips this step entirely — the folder is the distribution.

Run this again any time `mcp/` changes — it always starts from a clean venv, so there's no stale-cache risk.

### Where things land

Everything lives under the configured `output_dir`. On Windows that's `mcp/build/` (covered by the repo's root `.gitignore` — the generic `build/` rule matches at any depth, so it never gets committed); on this machine it's `/home/dell/mcp/amsha`:

```
<output_dir>/                    e.g. E:\Python\Amsha\mcp\build\AmshaMCP-dist   or   /home/dell/mcp/amsha
├── .build-venv/                 throwaway venv used only to run PyInstaller
├── build/                       PyInstaller's own intermediate work dir
├── dist/amsha-mcp/              the frozen standalone app
│   ├── amsha-mcp.exe            Windows: run this directly to test without installing
│   └── amsha-mcp                Linux: run this directly (the .exe has no Linux sibling)
└── installer/                   Windows only
    └── AmshaMCP-Setup-0.1.0.exe   <- the file you share/run to install
```

### Config

`mcp/packaging/build_config.json`:

| Field | Meaning |
|---|---|
| `app_name`, `app_version`, `publisher` | Cosmetic — shown in the installer UI |
| `output_dir` (top-level) | Windows default; where everything above gets built |
| `build_venv_dir` (top-level) | Windows default; where the throwaway build venv goes (usually just `output_dir/.build-venv`) |
| `platforms.linux.output_dir` | Linux output — the build script prefers the platform block over the top-level values |
| `platforms.linux.build_venv_dir` | Linux build venv location (defaults to `<linux output_dir>/.build-venv` if omitted) |
| `onedir_name` | Name of the frozen app folder and its executable |

**Not auto-synced**: if you change `output_dir` or `app_version`, also update the matching literal values at the top of `mcp/packaging/amsha_mcp_installer.iss` (`SourceDist`, `OutputDir`, `#define MyAppVersion`) — kept as a manual two-file sync rather than building a config-injection layer for four values that rarely change together. (Windows-only concern; the Linux build has no `.iss`.)

## Install

Run `AmshaMCP-Setup-0.1.0.exe`. Standard installer behavior:

- **Default location**: `%LOCALAPPDATA%\Programs\Amsha MCP` — no admin rights needed, works regardless of drive layout.
- **Custom location**: the wizard's destination page lets you Browse to any folder/drive. Everything the app needs lands entirely under whatever folder you pick — nothing is written elsewhere.
- **Silent install** (e.g. for scripting): `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="C:\some\path"` — quote the whole `/DIR=...` value if the path has spaces. Note: this got tested via PowerShell's `Start-Process -ArgumentList`, not Git Bash — Git Bash/MSYS auto-converts `/DIR=...`-style arguments as if they were Unix paths and corrupts them. Use PowerShell (or `cmd`) for silent installs.
- **Uninstall**: Start Menu → "Uninstall Amsha MCP", or `<install dir>\unins000.exe`. Removes the install directory, Start Menu shortcuts, and the registry uninstall entry completely — verified empty afterward.

## After installing: registering it with an MCP client

The installer just puts the executable on disk — it does not register it with Claude Code or any other client, and does not touch your global MCP config. Register it yourself:

```powershell
claude mcp add amsha-mcp -s local -- "C:\Users\<you>\AppData\Local\Programs\Amsha MCP\amsha-mcp.exe"
```

On Linux there's no installer — point the client straight at the frozen binary:

```bash
claude mcp add amsha-mcp -s local -- "/home/dell/mcp/amsha/dist/amsha-mcp/amsha-mcp"
# or in an opencode.jsonc:
# { "mcp": { "amsha-mcp": { "type": "local", "command": ["/home/dell/mcp/amsha/dist/amsha-mcp/amsha-mcp"] } } }
```

(`-s user` instead of `-s local` to make it available in every project, not just the one you run this from.)

### Pointing it at an Amsha-shaped repo

With nothing configured, the server only serves its own bundled methodology docs (`get_prerequisite_stage`, `get_implementation_guide`) — no repo-specific docs, and schema-verification tools (`verify_crew_yaml`, `dry_run_parse`, `smoke_test`) report they can't verify anything. To get real docs + real schema validation, set the target repo **before launching** (schema imports are resolved once, eagerly, at startup — see proposal 08's deadlock-guard discussion for why):

```powershell
claude mcp add amsha-mcp -s local -e AMSHA_MCP_TARGET_REPO="E:\Python\Amsha" -- "C:\...\amsha-mcp.exe"
```

```bash
claude mcp add amsha-mcp -s local -e AMSHA_MCP_TARGET_REPO="/home/dell/PycharmProjects/Amsha" -- "/home/dell/mcp/amsha/dist/amsha-mcp/amsha-mcp"
```

`register_repo(path)` (a tool call) can also point doc-serving tools at a different repo mid-session, but schema-verification tools stay bound to whatever `AMSHA_MCP_TARGET_REPO` was at startup until the server restarts — deliberate, not a bug (see proposal 08).

### Known limitation

`smoke_test` additionally needs `crewai`/`crewai_tools` importable from the registered repo (not just `amsha`'s own source) — it builds a real `Crew` object, which needs the full CrewAI stack, not just Amsha's Pydantic schemas. If the registered repo's dependencies aren't importable from wherever the standalone exe runs, `smoke_test` reports `"could not import builders: ModuleNotFoundError: No module named 'crewai'"` — honest, not a crash, not a fake pass. `verify_crew_yaml`/`dry_run_parse` don't have this problem — they only need Amsha's own Pydantic models, which are lighter.

## Rebuilding after a change

Same one command as Build, above — it always freshens the venv and re-freezes, so there's nothing to clean up manually first.
