# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Statusbar Converter is a Python 3.14 desktop app (macOS + Linux) that watches the OS clipboard and, when the copied text parses as a known format, shows the converted value in the system statusbar. Supported conversions: Unix timestamp → datetime, metric ↔ imperial (distance/volume/weight/temperature), and currency.

## Common commands

Tasks are run via [`just`](https://just.systems) (the `Justfile`). The virtualenv lives at `.venv/`; Scripts invoke `.venv/bin/python` directly, so they don't need it activated. To run Python yourself, `source .venv/bin/activate` first. The user usually runs these commands themselves — prefer asking them to run a command over running it yourself unless told otherwise.

- `just` — list all recipes.
- `just run` — start the app (`python -m src`). `--debug`, `--mock-update {old,new}`, `--mock-packaged`, `--currency-rates-url <url>`, `--sleep <sec>` are available CLI args (see `src/Service/ArgumentParser.py`).
- `just test` — run all unit tests (`python -m unittest`). Run a single test with the activated venv: `python -m unittest tests.Service.Conversion.testConversionManager` (or `...testConversionManager.TestClass.test_method`).
- `just mypy` — static type check over `src` only (config in `mypy.ini`).
- `just venv-install [basePythonBinary=python3.14]` — create `.venv` by hash-installing the lock files (`requirements/common.lock` + `requirements/<os>.lock`) via `scripts/venv-install.sh` (also builds `binaries/clipnotify` on Linux).
- `just lock` — regenerate the lock files from the `.in` sources via pip-tools (`pip-compile`). Conservative by default; use `just lock-upgrade <pkg>` or `just lock-upgrade-all` to bump pins. See the Dependencies section below.
- `just build` / `just build-spec` — produce the distributable via PyInstaller / regenerate the spec (`scripts/build.sh`, `scripts/build-spec.sh`). `just build` first runs `scripts/verify-dependencies.sh` (venv matches lock + common deps are platform-neutral). The spec lives in `build/spec-<os>-<arch>.spec`; regenerate when distribution inputs change. `just run-dist` runs the built binary.

## Architecture

### DI + OS switching (most important thing to understand)

Wiring happens in `src/Service/ServiceBuilder.py`. `ServiceBuilder.initializeServices()` returns a `ServiceContainer` (a typed `dict[type, object]` — see `src/DTO/ServiceContainer.py`) that `__main__.py` uses to pull entry-point services. There is no decorator-based DI framework; every service is constructed manually.

Many services have a base class plus `*Linux` / `*MacOs` concrete implementations selected by `OSSwitch` (`src/Service/OSSwitch.py`). This pattern applies to `AppLoop`, `AutostartManager`, `ClipboardManager`, `FilesystemHelper`, `StatusbarApp`. The `_get*` helpers in `ServiceBuilder` do the dispatch and import the platform-specific module lazily so that macOS-only (`rumps`) and Linux-only (PyGObject's `gi`, `clipnotify`) imports never load on the wrong OS. When adding a new cross-platform service, follow this pattern and put the `from src.Service.XxxMacOs import …` inside the `isMacOS()` branch — don't hoist it to the top of the file.

### Event bus

`src/Service/EventService.py` is the seam between layers. Instead of services holding references to each other, they subscribe/dispatch on the shared `EventService`: `ClipboardChanged`, `Converted`, `StatusbarClear`, `AppLoopIteration`, `UpdateCheckCompleted`, `DelayedConverterInitialized`. `ConversionManager` listens for `ClipboardChanged`, runs the text through the converter chain, and dispatches `Converted`; `StatusbarApp` listens for `Converted` to update the bar. `UpdateManager ↔ StatusbarApp` uses events specifically to break a circular import (see the docstring in `EventService.subscribeUpdateCheckCompleted`).

### Converter chain

`ConversionManager` holds an ordered list of `ConverterInterface` implementations (`src/Service/Conversion/ConverterInterface.py`) and returns on the first successful `tryConvert`. The chain today is `TimestampConverter` then `UnitConverter`. `UnitConverter` delegates to `UnitParser` → `UnitToConverterMapper` → per-unit `UnitConverterInterface` (distance, volume, weight, temperature, currency). `CurrencyConverter` is special: it's a `UnitConverterInterface` whose unit list is populated asynchronously by `ConversionRateUpdater` (hence `DelayedConverterInitialized` event and the `unitBeforeConverters` / `unitAfterConverters` split in `ServiceBuilder.getConversionManager`).

### Configuration

Three YAML layers, merged by `Configuration` (`src/Service/Configuration.py`):
1. `config/config.app.yml` — shipped defaults, never edited by users.
2. User config in the user data dir (path from `FilesystemHelper.getUserDataDir()`) — user overrides.
3. State file in the same dir — app-writable runtime state (e.g. last update check).

Access goes through `ConfigParameter` instances defined in `src/Constant/ConfigId.py` (each carries the YAML key path, default, and an `isState` flag). Only `isState=True` params can be `set()`.

### App lifecycle (see `src/__main__.py`)

1. `ServiceBuilder().initializeServices()` builds everything.
2. Logger prints platform info; `--sleep` delays icon appearance (Linux startup-order hack).
3. `ClipboardManager.validateSystem()` — early exit if clipboard backend is unavailable (e.g. missing `xsel` on Linux; shows the `MISSING_XSEL` modal).
4. `AutostartManager.setupAutostart()`, `ClipboardManager.initializeClipboardWatch()`, `ConversionRateUpdater.initializeRatesAsync()` (background thread), `AppLoop.startLoop()` (background thread dispatching `AppLoopIteration` every 10 s).
5. `StatusbarApp.createApp()` — blocking; runs the GUI event loop (`rumps` on macOS, `gi`/GTK on Linux). Everything after this returns only on app exit.

## Testing conventions

- Framework: stdlib `unittest` + `parameterized`. No pytest.
- Conversion logic is covered via integration-style tests against a real `ConversionManager` assembled through `ServiceBuilder.getConversionManager` — see `tests/Service/Conversion/AbstractConversionManagerTest.py`. Tests mock only `Configuration`, `Logger`, `ArgumentParser`, and `FilesystemHelper` (via `tests/TestUtil/MockLibrary.py`); the real converter wiring runs so regex/precedence bugs across converters surface.
- Currency tests load `assets_dev/rates_response_mock.json` and hydrate `CurrencyConverter` directly (no network).
- Pass `configOverrides: ConfigurationsList` to override individual `ConfigId` values per test.

## Things to know

- Python 3.14 is pinned. Linux GTK/statusbar access goes through native PyGObject + pycairo (`requirements/linux.in`). PyGObject is held at `>= 3.50, < 3.52` because 3.52+ needs girepository-2.0 (GLib ≥ 2.80) while Ubuntu 22.04 ships GLib 2.72 Additional build dependencies include `libgirepository1.0-dev`, `libcairo2-dev`, `pkg-config` (+ `gir1.2-gtk-3.0` at runtime).
- `# mypy: disable-error-code="..."` pragmas at the top of some files are intentional; leave them unless you're fixing the underlying typing issue.

### Dependencies (pip-tools lock files)

`requirements/*.in` are the hand-edited sources; `requirements/*.lock` are generated by `pip-compile` (`just lock`) — fully pinned + hashed, and committed. Install is `pip install --require-hashes` from the locks (`venv-install.sh`). Three sets: `common` (shared libs) plus `linux` / `macos`.

- **`common` must stay platform-neutral** so one `common.lock` is valid on both OSes. A package whose dependency graph differs per-OS (e.g. `pyinstaller`, which needs `macholib` only on macOS) must live in the OS `.in` files.
- **Generate `common.lock` once** (platform-neutral) but **OS locks on their own OS** (`macos.lock` needs a Mac; `pip-compile` can't cross-resolve).
- `scripts/verify-dependencies.sh` (run by `just build`) enforces both invariants: venv-matches-lock (`pip-sync --dry-run`) and common-is-platform-neutral.
