# Windows packages

Windows releases provide portable ZIPs for Standard, Lite, Full, and CLI, plus
a normal Standard installer. Standard is the primary GitHub download.

```powershell
python scripts/build_windows_packages.py `
  --frozen-root dist `
  --output-dir artifacts/windows `
  --version 0.8.0 `
  --iscc "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Portable files are named `SchedPlus-<Edition>-<version>-windows-x86_64.zip`.
The Standard installer is named
`SchedPlus-Setup-<version>-windows-x86_64.exe`. Every artifact has an adjacent
SHA-256 checksum in `SHA256SUMS.txt` and contains license, NOTICE, and source
information.

Before changing the release version, update
`packaging/pyinstaller/version_info.txt` to the matching four-part numeric
Windows version. The automated test prevents the file and `pyproject.toml`
from drifting apart.

The installer is user-scoped: it installs to `%LocalAppData%\Programs\SchedPlus`
and adds SchedPlus and its uninstaller to the current user's Start Menu. Its
stable Inno Setup AppId upgrades in place. Uninstall removes only installed
application files; task data remains at
`%APPDATA%\ZFordDev\SchedPlus\tasks.db`. Portable builds use the same external
data path and never write into their own extracted directory.

## SmartScreen and signing

Before public distribution, sign both the Standard installer and all portable
executables with an EV or organization-validation Authenticode certificate and
a trusted RFC 3161 timestamp service. Store certificate credentials only in the
release signing system or GitHub protected secrets—never in source control.
Unsigned development artifacts may trigger SmartScreen because reputation is
not established; they must be clearly marked as test builds. Verify signatures
and timestamps before publishing a release.
