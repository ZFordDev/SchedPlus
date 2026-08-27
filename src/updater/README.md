# SchedPlus updater integration

The updater is disabled unless a packaged build embeds
`schedplus/build-info.json`. Source checkouts therefore cannot overwrite their
working tree, and Store formats are always opted out in code.

A managed portable build uses metadata shaped like:

```json
{
  "version": "1.2.3",
  "edition": "standard",
  "format": "managed-zip",
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

Package handoff is deliberately format-aware:

- Windows managed ZIPs use the independent updater, atomic directory swap,
  health confirmation, and rollback.
- Direct-download Windows installer builds are unsigned under the current
  release policy and remain opted out of internal updates. Microsoft Store MSIX
  uses Store signing and Store-managed updates.
- Debian and AppImage builds download and verify the matching package, then
  expose it for installation through normal platform tools.
- Snap and Microsoft Store MSIX packages set `updates_enabled` to `false` and
  use Store updates exclusively.
- Source installations never enable the updater.

Approved release workflows read the Ed25519 private key only from the masked
`UPDATE_SIGNING_PRIVATE_KEY` secret. It is never written to an artifact or
printed. The matching public key is configured as the `UPDATE_PUBLIC_KEY`
repository variable and embedded in release packages. If public Windows signing
is configured later, CI uses masked certificate/password secrets and deletes
the temporary PFX before the job completes; their absence does not block a
release.
