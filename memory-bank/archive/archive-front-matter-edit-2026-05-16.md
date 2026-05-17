# TASK ARCHIVE: Menu-driven front matter edit

## METADATA
- **Task ID**: front-matter-edit-2026-05-16
- **Complexity**: Level 3 (user-visible UI + TOML serialization)
- **Task Type**: Phase 4 carry-over — menu-driven metadata editor
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-front-matter-edit-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-command-consolidation-2026-05-16.md`
- **Source deferral**: Phase 4 archive — *"Menu-driven front matter edit (dict editor for TOML; preserve YAML until a YAML dep is approved)."*

## SUMMARY

Closed the last open Phase 4 carry-over by shipping **View → Edit Front Matter…** (`Ctrl+Shift+M`). Users edit TOML metadata via a form-based dict editor, fix invalid TOML in a raw inner editor, or add a default TOML block when none exists. YAML front matter remains **read-only** in the dialog (edit in source). File save still preserves verbatim source; dialog OK **re-emits** TOML via **`tomli-w`**. Tests: **80 → 92 passed, 1 skipped** (+12). Coverage **80%**. `make check-all` green.

## REQUIREMENTS

1. Menu action under **View** to open a front matter editor.
2. TOML: structured dict editing with apply back to source + re-render.
3. YAML: no dict editor; read-only preview and guidance.
4. Documents without front matter: offer to create default TOML block.
5. Preserve-on-save invariant for manual source edits (verbatim round-trip).
6. Document re-emit trade-off when using dialog (comments/key order may change).
7. Unit + dialog + main-window tests; `make check-all` gate.
8. Update user docs (`front-matter.md`, `getting-started.md`).

## IMPLEMENTATION

### FM-A — Serialize + compose (`atlantis/utils/frontmatter.py`)

| Function | Role |
|----------|------|
| `serialize_toml_inner` | `tomli_w.dumps` — inner TOML text |
| `format_toml_front_matter` | Wrap with `+++` fences |
| `format_toml_front_matter_from_inner` | Wrap user-edited inner text |
| `replace_front_matter` | Swap FM segment; keep body |
| `insert_toml_front_matter` | Prepend new block |
| `validate_toml_inner` | Pre-accept validation |
| `strip_front_matter_inner` | Public fence strip helper |

**Dependency:** `tomli-w` (runtime; stdlib `tomllib` read-only).

### FM-B — `FrontMatterEditorDialog` (`atlantis/ui/front_matter_editor.py`)

| Mode | Behaviour |
|------|-----------|
| Valid TOML | Dynamic key/value rows; one-level `[table]` groups |
| Invalid TOML | Raw inner `QPlainTextEdit` + validation on OK |
| YAML | Read-only preview; Close only |
| No FM | Create default block (`title = ""`) |

Returns `result_front_matter: str | None` (full fenced block).

### FM-C — `MainWindow` (`atlantis/ui/main_window.py`)

- View menu: **Edit Front Matter…** — `Ctrl+Shift+M`
- `open_front_matter_editor()`: split → parse → dialog → `replace_front_matter` or prepend → `setModified` → debounced render
- YAML early-return guard (no source mutation)

### FM-D / FM-E — Flows + docs

- YAML read-only; no-FM create; invalid TOML recovery path
- `docs/user-guide/front-matter.md` — menu editor section
- `docs/getting-started.md` — link to front matter guide

### Files touched

| File | Change |
|------|--------|
| `pyproject.toml` | `tomli-w` dependency |
| `atlantis/utils/frontmatter.py` | Serialize/compose helpers |
| `atlantis/ui/front_matter_editor.py` | **New** dialog |
| `atlantis/ui/main_window.py` | Menu + `open_front_matter_editor` |
| `tests/test_frontmatter_serialize.py` | **New** (6 tests) |
| `tests/test_front_matter_editor.py` | **New** (4 tests) |
| `tests/test_main_window_front_matter.py` | **New** (2 tests) |
| `docs/user-guide/front-matter.md` | Menu editor docs |
| `docs/getting-started.md` | One-line pointer |

## TESTING

| Command | Result |
|---------|--------|
| `make check-all` | PASS |
| `uv run pytest -q` | **92 passed, 1 skipped** (+12) |
| `uv run mypy atlantis` | **0 errors** (31 source files) |
| Coverage | **80%** |

| Test module | Focus |
|-------------|--------|
| `test_frontmatter_serialize.py` | Round-trip, replace, insert, validate |
| `test_front_matter_editor.py` | Form accept, YAML read-only, create, invalid raw |
| `test_main_window_front_matter.py` | Stub dialog apply; menu action present |
| `test_phase4_frontmatter.py` | Unchanged (6 tests green) |

## EXIT CRITERIA — FINAL STATE

- [x] View → Edit Front Matter… with shortcut
- [x] TOML form + invalid raw + create flows
- [x] YAML read-only; source unchanged
- [x] Docs updated (re-emit vs verbatim)
- [x] 92 tests; `make check-all` green
- [x] `tomli-w` in runtime dependencies

## LESSONS LEARNED

- Use **`tomllib` + `tomli-w`** as the Python 3.12 read/write pair; do not hand-roll TOML serializers.
- **Document lossy edit paths** in dialog and docs when re-emitting from a dict editor.
- **Test serialize/compose before Qt UI** — faster feedback on fence/newline edge cases.
- **`QDialogButtonBox.accepted`** avoids mypy issues with optional `addButton()` return values.
- **Preserve-on-save** stays intact when dialog and file-save paths are clearly separated.

## DEFERRALS & FOLLOW-UPS

- **FS-F** — front-matter parse cache on `FileSession` (content-hash invalidation).
- **`_update_front_matter_action_tooltip()`** — optional YAML/TOML/none hints on menu action.
- **YAML dict editor** — when an approved YAML dependency lands.
- **Metadata-driven theme** — use parsed dict in render path (future).
- **Deep nested TOML in form** — edit in source for complex structures.
- **Backlog:** Phase 7/8 (Level 4 — plugins/packaging/rollout; requires `/creative`).
- **Removed deferral:** ~~Menu-driven front matter edit~~ — **done**.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-front-matter-edit-2026-05-16.md`
- Phase 4 source: `memory-bank/archive/archive-build-phase4-2026-05-11.md`
- Predecessor: `memory-bank/archive/archive-command-consolidation-2026-05-16.md`
- User guide: `docs/user-guide/front-matter.md`
- Project brief: `memory-bank/projectbrief.md` § Front Matter Handling
