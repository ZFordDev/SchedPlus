# SchedPlus updater integration

The updater is disabled unless a packaged build embeds
`schedplus/build-info.json`. Source checkouts therefore cannot overwrite their
working tree, and Store formats are always opted out in code.

A managed portable build uses metadata shaped like:

```json
{
  "version": "0.8.0",
  "edition": "standard",
  "package_format": "managed",
  "platform": "win32",
  "architecture": "x86_64",
  "channel": "stable",
  "update_manifest_url": "https://downloads.example/updates/stable.json",
  "update_public_key": "BASE64_ED25519_PUBLIC_KEY",
  "updater_executable": "../schedplus-updater.exe",
  "install_root": "..",
  "launch_relative_path": "schedplus.exe",
  "updates_enabled": true
}
```

Relative installation and updater paths are resolved from the running packaged
executable, never from the process working directory. A managed installation
must contain `current/`, `_old/`, and `temp/`, with the independent updater
executable outside `current/`.

Release manifests are canonical JSON signed with Ed25519. The `signature` field
is excluded from the signed payload; all other fields are encoded with sorted
keys and compact separators. Artifact SHA-256 and exact byte size are covered by
that signature. Private signing keys belong in the release system and must never
be committed or embedded in SchedPlus.

The first implementation supports directory-managed ZIP installations. AppImage,
Debian, and Windows installer adapters belong to their respective packaging
issues because each must use its platform's installation and elevation model.
Snap and Microsoft Store MSIX packages must set `updates_enabled` to `false` and
use Store updates exclusively.
