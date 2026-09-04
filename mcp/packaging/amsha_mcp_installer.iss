; Amsha MCP standalone installer.
; Compile with: ISCC.exe amsha_mcp_installer.iss
; Expects the PyInstaller --onedir output already built at:
;   {#SourceDist}\{#MyAppExeName}\   (see build_standalone.py)

#define MyAppName "Amsha MCP"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Nikhil"
#define MyAppExeName "amsha-mcp"
#define SourceDist "E:\Python\Amsha\mcp\build\AmshaMCP-dist\dist"

[Setup]
AppId={{B1B6D6C4-6E3B-4B7E-9B0A-AMSHA-MCP-0001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; No-admin, per-user default install location — works on any drive layout,
; matches the standard modern-installer default (VSCode/Discord-style),
; not tied to any specific partition.
DefaultDirName={localappdata}\Programs\{#MyAppName}
; User can still Browse to any other folder/drive on the wizard's dir page.
DisableDirPage=no
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
; Everything self-contained under {app}; uninstall removes the whole tree.
Uninstallable=yes
PrivilegesRequired=lowest
OutputDir=E:\Python\Amsha\mcp\build\AmshaMCP-dist\installer
OutputBaseFilename=AmshaMCP-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; The full PyInstaller onedir tree, recursively, all landing under {app}.
Source: "{#SourceDist}\{#MyAppExeName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}.exe"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[UninstallDelete]
; Safety net: guarantee the whole install dir is gone after uninstall,
; even if a stray runtime-written file exists that wasn't in [Files].
Type: filesandordirs; Name: "{app}"
