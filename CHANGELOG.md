# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Plugin manifest and `PluginRegistry` scaffold (`atlantis.plugins`) without dynamic loading.
- PyInstaller one-folder packaging PoC (`packaging/pyinstaller/`, `make bundle`, `make bundle-smoke`).
- ADR 0004 (native bundle), user guides for [installation](docs/user-guide/installation.md) and [plugins](docs/user-guide/plugins.md).

## [0.0.1] - 2026-05-16

### Added

- Initial MVP: Mermaid editor, WebEngine preview, offline Mermaid bundle, autosave/recovery, front matter menu editor, `make check` quality gates.

[Unreleased]: https://github.com/capp3/atlantis/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/capp3/atlantis/releases/tag/v0.0.1
