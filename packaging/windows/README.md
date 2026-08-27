# Windows packages

Windows releases provide portable ZIPs for Standard, Lite, Full, and CLI, plus
a normal Standard installer. Standard is the primary GitHub download.

```powershell
$version = python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"
python scripts/build_windows_packages.py `
  --frozen-root dist `
  --output-dir artifacts/windows `
  --version $version `
  --iscc "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Portable files are named `SchedPlus-<Edition>-<version>-windows-x86_64.zip`.
The Standard installer is named
`SchedPlus-Setup-<version>-windows-x86_64.exe`. Every artifact has an adjacent
SHA-256 checksum in `SHA256SUMS.txt` and contains license, NOTICE, and source
information.

`pyproject.toml` is the authoritative release version. Run
`python scripts/sync_release_versions.py` before packaging to update the Snap
manifest and `packaging/pyinstaller/version_info.txt`. Automated tests prevent
those derived files from drifting from the project version.

The installer is user-scoped: it installs to `%LocalAppData%\Programs\SchedPlus`
and adds SchedPlus and its uninstaller to the current user's Start Menu. Its
stable Inno Setup AppId upgrades in place. Uninstall removes only installed
application files; task data remains at
`%APPDATA%\ZFordDev\SchedPlus\tasks.db`. Portable builds use the same external
data path and never write into their own extracted directory.

## SmartScreen and signing

Direct GitHub installer and portable downloads are currently published without
Authenticode signatures and may trigger a Windows SmartScreen warning. The
Microsoft Store MSIX is the trusted Windows distribution: Microsoft signs it
after certification and manages its updates. Checksums and signed SchedPlus
update manifests verify GitHub release artifacts, but they do not replace
Windows publisher trust or suppress SmartScreen.

If the optional `WINDOWS_SIGNING_CERTIFICATE` and `WINDOWS_SIGNING_PASSWORD`
secrets contain a publicly trusted certificate, CI Authenticode-signs and
verifies the Standard installer before recalculating checksums. Those secrets
are intentionally optional and are not configured under the current release
policy. The unsigned installer is published without internal-update support.
Microsoft Store MSIX remains Store-signed and Store-managed. Portable ZIPs use a managed layout
with `current/`, a separate `SchedPlusUpdater.exe`, and embedded signed
update-feed metadata so activation can roll back after a failed health check.
