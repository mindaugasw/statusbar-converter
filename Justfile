set ignore-comments := true
set shell := ['bash', '-eEuo', 'pipefail', '-c']

# Docs: https://just.systems/man/en/
# Examples: https://github.com/casey/just/tree/master/examples
# Cheatsheet: https://cheatography.com/linux-china/cheat-sheets/justfile/


_venvDir := '.venv'
_scriptsDir := 'scripts'
_requirementsDir := 'requirements'
_pythonBinary := _venvDir + '/bin/python'
# pip-compile command for lock generation.
# --allow-unsafe pins pip, setuptools (required by --require-hashes installs);
# --strip-extras is the pip-tools 8.0 default;
# --generate-hashes locks every artifact's hash.
_pipCompileCommand := _venvDir + '/bin/pip-compile --allow-unsafe --strip-extras --generate-hashes --cache-dir var/pip_tools_cache --quiet'
_os := `source scripts/common.sh && _getOsName`

_yellow := '\e[33m'
_r := '\e[0m'
_arrow := _yellow + '>' + _r


# --- help ---
# Print this help
help:
    @just --list --unsorted

# --- setup ---
# Print instructions to activate Python venv
[group('setup')]
venv-activate-instructions:
    @echo -e '{{_arrow}} Run this command manually to active venv:'
    @echo 'source {{_venvDir}}/bin/activate'

# Install Python virtual env
[group('setup')]
venv-install basePythonBinary='/usr/bin/python3.14':
    {{_scriptsDir}}/venv-install.sh {{_venvDir}} {{basePythonBinary}}

# Regenerate dependency lock files from .in sources
[group('setup')]
lock:
    # pip-compile is conservative - it keeps existing pins unless an upgrade is requested (see `lock-upgrade`).
    # OS-specific lock files must be generated on the correct OS.

    {{_pipCompileCommand}} "{{_requirementsDir}}/common.in" -o "{{_requirementsDir}}/common.lock"
    {{_pipCompileCommand}} "{{_requirementsDir}}/{{_os}}.in" -o "{{_requirementsDir}}/{{_os}}.lock"

# Upgrade a single locked package to its latest allowed version, then relock
[group('setup')]
lock-upgrade package:
    {{_pipCompileCommand}} --upgrade-package {{package}} "{{_requirementsDir}}/common.in" -o "{{_requirementsDir}}/common.lock"
    {{_pipCompileCommand}} --upgrade-package {{package}} "{{_requirementsDir}}/{{_os}}.in" -o "{{_requirementsDir}}/{{_os}}.lock"

# Upgrade every locked package to its latest allowed version, then relock
[group('setup')]
lock-upgrade-all:
    {{_pipCompileCommand}} --upgrade "{{_requirementsDir}}/common.in" -o "{{_requirementsDir}}/common.lock"
    {{_pipCompileCommand}} --upgrade "{{_requirementsDir}}/{{_os}}.in" -o "{{_requirementsDir}}/{{_os}}.lock"


# --- scripts ---
# Run the app
[group('scripts')]
run *ARGS:
    {{_pythonBinary}} -m src {{ARGS}}

# Run tests and all static analysers
[group('scripts')]
static-analysis:
    @echo -e "{{_arrow}} Test":
    @just test

    @echo -e "\n{{_arrow}} Mypy":
    @just mypy

    @echo -e "\n{{_arrow}} Lint":
    @just lint-fix

    @echo -e "\n{{_arrow}} Format":
    @just format

# Run unit tests
[group('scripts')]
test *ARGS:
    {{_pythonBinary}} -m unittest {{ARGS}}

# Run unit tests with coverage
[group('scripts')]
coverage:
    {{_pythonBinary}} -m coverage run
    @{{_pythonBinary}} -m coverage html

    @echo -e "\nCoverage %:"
    @{{_pythonBinary}} -m coverage report --format=total

# Run mypy static analysis
[group('scripts')]
mypy *ARGS:
    @mkdir -p var/mypy_cache
    {{_pythonBinary}} -m mypy src {{ARGS}}

# Run code linter
[group('scripts')]
lint *ARGS:
    # We run linter twice to output both full error info and concise summary at the end
    -@{{_venvDir}}/bin/ruff check {{ARGS}}
    @echo -e "--- --- ---   --- --- ---   --- --- ---   --- --- ---   --- --- ---   --- --- ---   --- --- ---   ---"
    @{{_venvDir}}/bin/ruff check --statistics {{ARGS}}

    # Some ruff commands that may be relevant when solving errors:
    # `ruff check --select UP015` - check only 1 rule
    # `ruff rule UP015` - explain a rule

# Run code linter and auto-fix errors
[group('scripts')]
lint-fix *ARGS: (lint "--fix")

# Run automated style formatting
[group('scripts')]
format *ARGS:
    @{{_venvDir}}/bin/ruff format {{ARGS}}

# --- build ---
# Build a spec file. Generally does not need runing, build uses pre-built spec.
[group('build')]
build-spec:
    {{_scriptsDir}}/build-spec.sh {{_venvDir}}

# Build a distributable
[group('build')]
build:
    {{_scriptsDir}}/build.sh {{_venvDir}}

# Run the app from the built distributable
[group('build')]
run-dist:
    #!/usr/bin/env bash
    os="$(uname)"

    if [[ "$os" == 'Linux' ]]; then
        'build/dist-linux-x86_64/Statusbar Converter'
    elif [[ "$os" == 'Darwin' ]]; then
        open 'build/dist-macos-arm64/Statusbar Converter.app'
    else
        echo "Unsupported OS: $os" >&2
        exit 1
    fi
