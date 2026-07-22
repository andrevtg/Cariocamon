# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Tuxemon is an open source, monster-fighting RPG written in Python (3.10+) using `pygame-ce`. Game content (monsters, items, techniques, maps, translations) is entirely data-driven via JSON/YAML/TMX files under `mods/`, separate from the engine code under `tuxemon/`.

## Commands

Run these from the project root.

```shell
# Setup
pip install -U -r requirements.txt
pip install -e .              # install as editable library (needed for imports/tests)

# Run the game
python run_tuxemon.py
python run_tuxemon.py -m <modname>   # run with a specific/additional mod
python run_tuxemon.py -s              # headless/dedicated server mode

# Tests (pytest, tests live in tests/tuxemon)
pytest tests
pytest tests/tuxemon/test_combat_layout.py          # single file
pytest tests/tuxemon/test_combat_layout.py::TestClassName::test_case_name  # single test
tox -e py3                                            # same, via tox

# Formatting & linting (ruff)
tox -e fmt          # ruff format + ruff check --fix --unsafe-fixes
tox -e format        # ruff format only
tox -e lint          # ruff check only

# Type checking
tox -e type          # mypy tuxemon

# Import sanity check (also run in CI)
python scripts/test_imports.py
```

CI (`.github/workflows/python-app.yml`) runs `scripts/test_imports.py` and `pytest tests` on Python 3.10. There is no separate CI lint/type gate currently, but `tox -e fmt`/`lint`/`type` are the canonical local checks — run them before committing.

Enable the in-game debug CLI by setting `cli_enabled = True` under `[game]` in the user's `tuxemon.yaml` (generated in user storage on first run, see Config below). See `docs/cli.md`.

## Architecture

### Startup & main loop

`run_tuxemon.py` parses CLI args, initializes the platform/display (`tuxemon/prepare.py`), and hands off to `tuxemon/main.py` (`main()` for pygame, `headless()` for dedicated servers). `main()` builds a `LocalPygameClient` (`tuxemon/client.py`, extends `BaseClient` in `base_client.py`) which owns the fixed-timestep update/draw loop, then runs `StartupStateMachine` (`tuxemon/startup_state_machine.py`) — a sequence of rule objects (`RuleBackground`, `RuleIntro`, `RuleLoadSlot`, `RuleSplash`, `RuleMods`, each with `should_apply()`/`apply()`) that push the correct initial states depending on CLI flags and saved state.

### State system

`tuxemon/state/` is the generic engine: `StateStack` (deque-based push/pop/replace), `StateManager` (stack + deferred `StateQueue` + `StateFactory`/`StateLoader`/`StateRepository` for dynamic instantiation by name), and the base `State` class. `tuxemon/states/` holds the ~70 concrete state classes grouped by domain: world/overlay (`world_state.py`, transitions), combat (`combat_state.py`, `combat_menus.py`, `combat_animations.py`), and menus/UI (`party.py`, `pc.py`, `monster_*`, `item_menu.py`, `shop_*`, etc). Overlays (menus, dialogs) stack on top of persistent base states (Background + World).

### Event/scripting system (`tuxemon/event/`)

Map scripting engine, distinct from `eventmanager.py` (input/middleware plumbing for `StateManager`). Flow: `EventParser` reads raw map event data (`behav`, `conditions`, `actions`) and builds structured objects (`EventObject`, `ParameterizableRule`, etc., defined in `db.py`) via `tuxemon/script/parser.py`. `EventEngine` evaluates conditions per-frame for the current map and runs `ActionManager` on match; actions/conditions can span multiple frames (`RunningEvent`/`RunningCondition`), reset on map change. Concrete behavior lives one-per-file in `event/actions/*.py` and `event/conditions/*.py` (see `tuxemon/event/README.md`: one action/condition per file, no imports outside the `tuxemon.event` package). The in-game CLI (`tuxemon/cli/`) reuses these exact `EventAction`/`EventCondition` classes for live `action`/`test` commands.

### Data layer (content vs. engine)

`tuxemon/db.py` defines pydantic models/enums for every data type (Monster, Item, Technique, NPC, map metadata, etc.). `tuxemon/database/` is the loading/validation machinery: `bootstrap.py` reads `mods/db_config.yaml`, builds a `model_map`, and loads via `ModelLoader`/`ModData`; `loader.py`/`yaml_utils.py` read JSON/YAML per category directory keyed by `slug`, with later-loaded mods overriding earlier entries (multi-mod overlay support); `validate_mod_data.py`/`validator.py` enforce schema + cross-reference integrity.

Content lives under `mods/tuxemon/`: `db/<category>/*.json` (item, monster, technique, npc, encounter, economy, mission, status, element, taste, terrain, weather, etc.), `maps/*.tmx` (Tiled maps carrying embedded event data), `l18n/<locale>/` (PO translation files), plus `sprites/`, `gfx/`, `music/`, `sounds/`, `font/`, `animations/`, `effects/`. `mods/tuxemon/mod.yaml` declares mod metadata (slug, version, starting player/map/position/money) and points at `mods/tuxemon/rules.py` for mod-specific startup rules. The engine itself is content-agnostic; additional/override mods can be loaded with `-m`.

### Combat system

`tuxemon/combat/` holds supporting logic (`action_queue.py`, `combat_context.py`, `damage_tracker.py`, `experience_strategies.py`, `field_monsters.py`, `machine.py`, `reward_system.py`, `sort_manager.py`), separate from the UI/state layer in `tuxemon/states/combat_state.py` (entry point), `combat_menus.py`, `combat_animations.py`.

### Save system

See `docs/save_system.md`. Slot model: autosave is slot 0 (hidden in the save menu but loadable, only ever written by `AutosaveAction`); user slots 1–3 map to UI indices 0–2 via `ui_to_save_index`/`save_index_to_ui`. Implementation is split across `save_system/save_slots.py` (pure mapping helpers), `save_manager.py` (orchestrator), `save_state.py` (data model), `save.py` (serialization/IO) — designed so autosave can never be clobbered by player actions.

### Config

`tuxemon/config.py` defines pydantic config models (`TuxemonConfig`, `DisplayConfig`, etc.). `tuxemon/user_config.py`'s `setup_user_environment()` ensures user storage directories exist and loads/creates the user's `tuxemon.yaml` there (not shipped in the repo) on first run, round-tripped via `dump_yaml_path`/`load_yaml`.

## Code guidelines (from CONTRIBUTING.md)

- New files follow PEP8, 79-char line limit; format with `ruff` (`tox -e fmt`) before committing
- Docstrings mandatory on new functions/methods (unless overloading); include basic type annotations
- Don't change existing formatting unless actively improving it; avoid dead code and duplication
- No debug `print()` — use the `logging` module; `print()` is reserved for CLI-facing output
- Prefer raising/crashing over silently swallowing errors; fix root causes rather than adding defensive error handling for things that shouldn't happen
- Mark incomplete code paths with TODOs
- Interactive/manual test scripts go in `scripts/`; automated unit tests go in `tests/`
- Work from a feature branch off `development`, never commit directly to `development`; PRs target `development`

### Test style (from tests/README.md)

- Descriptive, plain-English test names (e.g. `test_event_names_do_not_exceed_max_length`) — long names over short ones, no explanatory comments
- One behavior per test
- Mocks are fine, use `spec=` when creating them; keep tests fast by mocking expensive/irrelevant work

### Scripts folder (from scripts/README.md)

- `scripts/` is optional tooling, not required to run/play the game — no unit tests required, no project dependencies added to `requirements.txt` for script-only needs
- Anything required to actually *play* the game belongs in the engine, not a script

### Asset/content contributions (from CONTRIBUTING.md)

- Filenames: lowercase only, ASCII, letters/numbers/`_`/`-` only, no spaces
- Images: PNG only (no JPG); music: OGG only; sounds: WAV or OGG; animations: one image per frame, no GIFs
- New contributions need an entry in `ATTRIBUTIONS.md` (author, source, license)
- Maps: grid-aligned events/collisions, external tilesets only (no embedded), use `translated_dialog` for all dialogs, prefer "core" tilesets
