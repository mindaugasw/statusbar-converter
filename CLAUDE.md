# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Statusbar Converter is a Python 3.10 desktop app (macOS + Linux) that watches the OS clipboard and, when the copied text parses as a known format, shows the converted value in the system statusbar. Supported conversions: Unix timestamp → datetime, metric ↔ imperial (distance/volume/weight/temperature), and currency.

## Common commands

The virtualenv lives at `.venv-<os>-<arch>/` (e.g. `.venv-linux-x86_64`) and must be activated first. `make` targets auto-source it via glob; running Python directly requires manual `source .venv-*/bin/activate`.

- `make run` — start the app (`python -m src`). `--debug`, `--mock-update {old,new}`, `--mock-packaged`, `--currency-rates-url <url>`, `--sleep <sec>` are available CLI args (see `src/Service/ArgumentParser.py`).
- `make test` — run all unit tests (`python -m unittest`).
- Run a single test: `source .venv-*/bin/activate && python -m unittest tests.Service.Conversion.testConversionManager` (or `...testConversionManager.TestClass.test_method`).
- `make coverage` — run tests with coverage, HTML report to `var/htmlcov/`.
- `make mypy` — static type check over `src tests` with `--follow-untyped-imports --ignore-missing-imports`.
- `make install_linux` / `make install_macOS_AppleSilicon` / `make install_macOS_intel_simulated` — create venv from `requirements_<os>.txt` via `builder.sh install`.
- `make build_linux` / `make build_macOS_AppleSilicon` / `make build_macOS_intel` — produce distributable via PyInstaller (`builder.sh build`). A spec file in `build/spec-<os>-<arch>.spec` is required; regenerate via `./builder.sh buildSpec <arch>` when distribution inputs change.
- `make run_dist_linux` — run the built Linux binary.

## Architecture

### DI + OS switching (most important thing to understand)

Wiring happens in `src/Service/ServiceBuilder.py`. `ServiceBuilder.initializeServices()` returns a `ServiceContainer` (a typed `dict[type, object]` — see `src/DTO/ServiceContainer.py`) that `__main__.py` uses to pull entry-point services. There is no decorator-based DI framework; every service is constructed manually.

Many services have a base class plus `*Linux` / `*MacOs` concrete implementations selected by `OSSwitch` (`src/Service/OSSwitch.py`). This pattern applies to `AppLoop`, `AutostartManager`, `ClipboardManager`, `FilesystemHelper`, `StatusbarApp`. The `_get*` helpers in `ServiceBuilder` do the dispatch and import the platform-specific module lazily so that macOS-only (`rumps`) and Linux-only (`vext.gi`, `clipnotify`) imports never load on the wrong OS. When adding a new cross-platform service, follow this pattern and put the `from src.Service.XxxMacOs import …` inside the `isMacOS()` branch — don't hoist it to the top of the file.

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

- Python 3.10 is pinned. On macOS Apple Silicon, building the x86_64 distributable requires a separate `python3.10-intel64` from python.org (Homebrew Python is single-arch).
- Linux builds depend on `binaries/clipnotify` (cloned+built by `builder.sh _installLinux`) and a copy of `/usr/lib/python3/dist-packages/gi` into the venv — both are required for PyInstaller to pick them up.
- `# mypy: disable-error-code="..."` pragmas at the top of some files are intentional; leave them unless you're fixing the underlying typing issue.
- There is a TODO in `ServiceBuilder` and `ArgumentParser` to reuse utilities from a separate `algotrading-repo`. Don't invent those abstractions here preemptively.
