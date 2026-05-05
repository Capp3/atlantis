# Changelog

All notable changes to the Vibe Dev Template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Universal `.gitignore` with organized sections for all common development patterns
- Modular VSCode settings split by language (Python, JavaScript/TypeScript, Docker)
- Comprehensive `.editorconfig` with support for multiple file types
- Enhanced `.gitattributes` for cross-platform development
- Prettier configuration (`.prettierrc` and `.prettierignore`)
- Improved Makefile with error handling and no sudo requirements
- MkDocs configuration with mkdocs-bootswatch theme support
- Complete `.github/` directory structure:
  - Pull request template
  - Bug report issue template
  - Feature request issue template
  - Issue template configuration
  - Workflows directory with example workflows
- Comprehensive `README.md` with:
  - Repository initialization instructions
  - GitHub publishing workflow
  - Proper credits and attributions
  - File structure documentation
  - Customization guidelines
- `CONTRIBUTING.md` with detailed contribution guidelines
- `.vscode/README.md` explaining settings file structure
- `CHANGELOG.md` for tracking template changes

### Changed

- Reorganized `.gitignore` to be truly universal with Python-specific patterns as optional
- Improved Makefile with inline credits and better error messages
- Enhanced `mkdocs.yml` with better theme configuration and markdown extensions
- Updated `.editorconfig` with additional file type support

### Removed

- Sudo requirements from all Makefile targets
- Language-specific biases from core configuration files

## [1.0.0] - Initial Release

### Added

- Basic project structure
- Initial `.gitignore` (Python-focused)
- Basic VSCode settings
- Simple `.editorconfig`
- Basic Makefile with Cursor AI tool integration
- MkDocs documentation setup
- Basic README

---

## Guidelines for Updating This Changelog

When making changes to the template, update this file following these guidelines:

### Categories

- **Added** - New files, features, or functionality
- **Changed** - Changes to existing functionality
- **Deprecated** - Features that will be removed in future versions
- **Removed** - Features or files that have been removed
- **Fixed** - Bug fixes
- **Security** - Security-related changes

### Version Format

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** - Incompatible changes that require users to update their usage
- **MINOR** - New features that are backwards-compatible
- **PATCH** - Backwards-compatible bug fixes

### Keeping Track

Add changes to the `[Unreleased]` section as you make them. When creating a release:

1. Change `[Unreleased]` to the version number and date
2. Create a new `[Unreleased]` section at the top
3. Tag the release in Git

### Example Entry

```markdown
## [1.1.0] - 2026-01-15

### Added

- Support for Rust development with `.vscode/settings.rust.json`
- Cargo.toml patterns in `.gitignore`

### Changed

- Updated `.editorconfig` to include Rust file types
- Improved documentation structure

### Fixed

- Corrected typo in Makefile help text
```
