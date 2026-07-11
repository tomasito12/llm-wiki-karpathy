# Technical Specification: Central Path Configuration

Last updated: 2026-07-11

This is the first implementation slice for the future repository and vault
split.

It introduces a central path configuration layer without moving any data yet.

## Purpose

Before the project can split code, knowledge data, and Obsidian vault output,
commands need a shared way to resolve paths.

Today, many commands assume paths like:

```text
raw/readwise
state/reviews
state/synthesis
wiki
```

inside the code repository.

That must remain the default for compatibility, but the system should also
support external paths.

## Goal

Add one reusable path configuration module.

It should:

- preserve current defaults when no config is present
- support an optional config file
- support environment override for config file location
- resolve absolute paths
- be easy for CLIs to use
- be tested independently

## Non-Goals

Do not move files.

Do not change output formats.

Do not introduce server deployment.

Do not rewrite all CLIs in one pass if that becomes too large.

Do not add a web UI.

## Proposed Module

```text
src/wiki_paths/
  __init__.py
  config.py
```

Alternative if preferred:

```text
src/wiki_ops/paths.py
```

But a separate `wiki_paths` module is cleaner because this will be used by
render, synthesis, ops, ingest, and future server code.

## Config File

Suggested default optional file:

```text
config/wiki_paths.toml
```

Environment override:

```text
LLM_WIKI_PATHS_CONFIG=/path/to/wiki_paths.toml
```

If no config file exists, use current repo-local defaults.

## Config Shape

```toml
[paths]
knowledge_root = "/Users/plischke/Desktop/Private Development/llm-wiki-data"
vault_root = "/Users/plischke/Documents/Obsidian/llm-wiki-vault-private"

raw_dir = "{knowledge_root}/raw/readwise"
reviews_dir = "{knowledge_root}/state/reviews"
synthesis_dir = "{knowledge_root}/state/synthesis"
graph_path = "{knowledge_root}/state/wiki_render_graph.json"
manifest_path = "{knowledge_root}/state/wiki_render_manifest.json"
release_dir = "{knowledge_root}/state/releases"

preview_dir = "{knowledge_root}/tmp/synthesis_previews"
run_dir = "{knowledge_root}/tmp/synthesis_runs"
backup_dir = "{knowledge_root}/tmp/synthesis_backups"

wiki_dir = "{vault_root}/wiki"
source_pages_dir = "{vault_root}/sources/full"
source_index_path = "{vault_root}/sources/index.md"
indexes_dir = "{vault_root}/indexes"
```

All fields should be optional. Missing fields fall back to defaults.

## Default Paths

When no config is present, defaults should match current behavior:

```text
repo/raw/readwise
repo/state/reviews
repo/state/synthesis
repo/state/wiki_render_graph.json
repo/state/wiki_render_manifest.json
repo/state/synthesis_previews
repo/state/synthesis_runs
repo/state/synthesis_backups
repo/wiki
```

Source page defaults can initially be:

```text
repo/wiki/sources/full
repo/wiki/sources/index.md
repo/wiki/indexes
```

until the vault split happens.

## Dataclass

Suggested dataclass:

```python
@dataclass(frozen=True)
class WikiPaths:
    repo_root: Path
    knowledge_root: Path
    vault_root: Path
    raw_dir: Path
    reviews_dir: Path
    synthesis_dir: Path
    graph_path: Path
    manifest_path: Path
    release_dir: Path
    preview_dir: Path
    run_dir: Path
    backup_dir: Path
    wiki_dir: Path
    source_pages_dir: Path
    source_index_path: Path
    indexes_dir: Path
```

## API

Suggested functions:

```python
def load_wiki_paths(
    *,
    repo_root: Path | None = None,
    config_path: Path | None = None,
) -> WikiPaths:
    ...

def default_wiki_paths(repo_root: Path) -> WikiPaths:
    ...

def resolve_path_template(value: str, variables: Mapping[str, Path]) -> Path:
    ...
```

## CLI Integration Pattern

Existing CLIs should keep explicit path flags.

Precedence:

1. explicit CLI flag
2. config file value
3. repo-local default

Example:

```bash
hatch run wiki-ops-status --config config/wiki_paths.toml
hatch run wiki-render --paths-config config/wiki_paths.toml
```

Use one option name consistently. Preferred:

```text
--paths-config
```

Do not break existing flags like `--graph-path` or `--cache-dir`.

## First Commands to Migrate

Start with:

- `wiki-ops-status`
- `wiki-render`
- `wiki-synthesis-plan`
- `wiki-synthesis-select`
- `wiki-synthesis-batch`
- `wiki-synthesis-cache-lint`

Do not migrate Streamlit/dashboard in the first slice unless it is trivial.

## Debug Output

Add a read-only way to inspect resolved paths.

Preferred:

```bash
hatch run wiki-ops-status --paths-json
```

or a later dedicated command.

Do not create another Hatch command just for path debugging unless needed.

## Tests

Required tests:

- no config returns current repo-local defaults
- config file overrides roots
- individual path entries override derived defaults
- explicit CLI path overrides config path
- missing config is okay when not explicitly requested
- explicitly requested missing config returns a clear error
- placeholder expansion works
- relative paths are resolved relative to config file parent or repo root; choose
  one and document it

Recommended relative-path rule:

Relative paths in config are resolved relative to the config file directory.

## Acceptance Criteria

This slice is done when:

- a central path config module exists
- current commands still work without config
- at least `wiki-ops-status`, `wiki-synthesis-select`, and
  `wiki-synthesis-batch` can use external paths through config
- tests prove CLI flags override config
- no data is moved
- no generated outputs change unless external paths are explicitly configured

