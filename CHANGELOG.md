# Changelog

## Unreleased

- Moved the SQLite database to the platform-specific user data directory and
  added automatic relocation of databases created by earlier releases.
- Removed the obsolete JSON persistence backend and migration fallback. SQLite
  is now the sole task storage system.
