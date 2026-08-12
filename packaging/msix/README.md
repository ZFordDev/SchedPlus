# Microsoft Store (MSIX) package

This package is **Standard edition only**. It launches the PyQt interface
directly and contains no application execution alias: users launch SchedPlus
from Start or the Microsoft Store.

## Partner Center hand-off

After reserving the product name, copy these exact values from Partner Center:

- Package/Identity name
- Publisher (`CN=...` value)
- Publisher display name

Do not invent these values. They bind the package to the Store product and
cannot be changed after publication. Set them as repository secrets named
`MSIX_IDENTITY_NAME`, `MSIX_PUBLISHER`, and `MSIX_PUBLISHER_DISPLAY_NAME`.
The manual GitHub Actions workflow reads those secrets; it never asks for them
as workflow inputs or prints them to the log.

## Build locally

Build `dist/SchedPlusStandard` with the Standard PyInstaller spec, install
Pillow as a build-only tool, then run:

```powershell
python -m pip install Pillow
python scripts/build_msix.py `
  --frozen-dir dist/SchedPlusStandard `
  --output-dir artifacts/msix `
  --identity-name "<Partner Center package identity name>" `
  --publisher "<Partner Center publisher>" `
  --publisher-display-name "ZFordDev" `
  --makeappx "<path to MakeAppx.exe>"
```

The script creates an unsigned `.msix`, and MakeAppx validates its manifest
during packaging and then unpacks the completed package as a structure check.
This is appropriate for Store upload: Microsoft signs the package after
certification.
For local installation only, sign with a self-signed development certificate;
never commit a certificate or private key. The GitHub Actions workflow builds
and retains an unsigned package for manual Partner Center upload; it does not
publish anything.

The manifest declares `runFullTrust`, required for the packaged PyInstaller
desktop process. It does not request camera, microphone, location, networking,
or other device capabilities. SchedPlus continues to store task data at
`%APPDATA%\ZFordDev\SchedPlus`, never in the MSIX installation directory.

See [store-listing.md](store-listing.md) for listing copy, privacy-policy work,
license disclosure, and screenshot requirements.
