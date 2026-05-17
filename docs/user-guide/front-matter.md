# Front matter

Mermaid documents may begin with a YAML (`---`) or TOML (`+++`) fenced front matter block. Atlantis preserves the original text on save and never blocks editing on a malformed block — invalid TOML and YAML-without-parser cases surface as non-blocking warnings in the status bar.

## Menu editor (TOML)

Use **View → Edit Front Matter…** (`Ctrl+Shift+M`) to edit TOML metadata as key/value fields, fix invalid TOML in a raw inner editor, or add a new TOML block when the document has none.

| Document | Dialog behaviour |
|----------|------------------|
| TOML (`+++`) | Form editor for top-level keys and one-level `[tables]`; OK re-emits the fenced block |
| YAML (`---`) | Read-only preview; edit in the source editor |
| No front matter | Create a default TOML block (e.g. `title = ""`) |

**Important:** Saving from the dialog **re-serializes** TOML (comments and key order may change). Editing the source directly still round-trips verbatim on file save.

## Supported formats

| Fence | Format | Parser |
|-------|--------|--------|
| `---` … `---` | YAML | **Preserved verbatim**; no parser shipped in MVP (warns when metadata is requested). |
| `+++` … `+++` | TOML | Parsed with the stdlib `tomllib`; invalid TOML surfaces as a warning, never an exception. |

## What Atlantis does on save

- The entire front-matter block (including fences) is preserved exactly as the user typed it. We do **not** re-emit YAML/TOML from a parsed dict, so comments, key order, and whitespace round-trip.
- The body (everything after the closing fence) is the only part fed to Mermaid.

## What Atlantis does on render

- TOML metadata is parsed with `tomllib`. On success, the dict is available for future features (theming, navigation hints). On failure, the user sees a status-bar warning of the form `Invalid TOML front matter: …`.
- YAML metadata is preserved but not interpreted; the warning makes the deferral explicit.

## Examples

### YAML (preserved, not parsed)

```yaml
---
title: System Architecture
config:
  theme: default
---
flowchart TD
  A --> B
```

### TOML (parsed)

```toml
+++
title = "System Architecture"
[config]
theme = "default"
+++
flowchart TD
  A --> B
```

### Invalid TOML (warns, still renders)

```toml
+++
not toml at all
+++
flowchart TD
  A --> B
```

The diagram still renders; the status bar surfaces the TOML error and you can cycle through any active errors with `Ctrl+E`.
