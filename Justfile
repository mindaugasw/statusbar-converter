set ignore-comments := true
set shell := ['bash', '-eEuo', 'pipefail', '-c']

# Docs: https://just.systems/man/en/
# Examples: https://github.com/casey/just/tree/master/examples
# Cheatsheet: https://cheatography.com/linux-china/cheat-sheets/justfile/


_venvDir := '.venv'
_pythonBinary := _venvDir + '/bin/python'
_scriptsDir := 'scripts'

_yellow := '\e[33m'
_r := '\e[0m'
_arrow := _yellow + '>' + _r


# --- help ---
# Print this help
[group('help')]
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
venv-install basePythonBinary='python3.10':
    {{_scriptsDir}}/venv-install.sh {{_venvDir}} {{basePythonBinary}}


# --- build ---
# Build a spec file. Generally does not need runing, build uses pre-built spec.
[group('build')]
build-spec:
    {{_scriptsDir}}/build-spec.sh {{_venvDir}}

# Build a distributable
[group('build')]
build:
    {{_scriptsDir}}/build.sh {{_venvDir}}


# --- scripts ---
#
[group('scrips')]
test:
    echo hello
    source {{_venvDir}}/bin/activate
    python -V
