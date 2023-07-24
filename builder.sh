#!/usr/bin/env bash

# Usage:
# `install arm64 python3.10` or `install x86_64 python3.10-intel64`
# `buildSpec arm64`
# Modify spec file as needed
# `build arm64`

install() {(set -e
    # Prepare virtualenv for given architecture

    arch=$1 # architecture name, `arm64` | `x86_64`
    pythonExec=$2 # python executable name, e.g. `python3.10` or `python3.10-intel64`

    _validateArchArg "$arch"

    if [ -z "$pythonExec" ]; then
        _logError 'Python executable must be provided as argument (e.g. "python3.10" or "python3.10-intel64")'
        exit 1
    fi

    _validateExecutableArchitecture "$arch" "$pythonExec"

    venvPath=".venv-$arch"
    _log "Installing virtualenv to \"$venvPath\""

    $pythonExec -m venv ".venv-$arch" --clear --copies

    source "$venvPath/bin/activate"

    pip install wheel
    pip install -r requirements_macos.txt

    _log "Successfully installed virtualenv to \"$venvPath\""
)}

buildSpec() {(set -e
    arch=$1 # architecture name, `arm64` | `x86_64`

    _validateArchArg "$arch"

    _log "Generating spec for $arch"

    venvPath=".venv-$arch"
    specFilePath="build/spec-$arch.spec"
    rm -f "$specFilePath"

    source "$venvPath/bin/activate"

    "$venvPath/bin/pyi-makespec" \
        --name "Statusbar Converter" \
        --onedir \
        --windowed \
        --add-data '../assets:assets' \
        --add-data '../config:config' \
        --icon '../assets/icon.png' \
        --target-arch "$arch" \
        --osx-bundle-identifier 'com.mindaugasw.statusbar_converter' \
        --specpath 'build' \
        start.py

    mv "build/Statusbar Converter.spec" "$specFilePath"

    _log "Successfully generated spec for $arch at $specFilePath"
)}

build() {(set -e
    arch=$1 # architecture name, `arm64` | `x86_64`

    _validateArchArg "$arch"
    venvPath=".venv-$arch"
    distPath="build/dist-$arch"

    source "$venvPath/bin/activate"

    rm -rf "./$distPath"

    _log "Starting build for $arch"

    "$venvPath/bin/pyinstaller" \
        --clean \
        --distpath "$distPath" \
        --workpath "$distPath/build" \
        "build/spec-$arch.spec"

    _log "Successfully built for $arch in $distPath"

    _createZip "$arch"
)}

_createZip() {(set -e
    # Compress app to .zip archive.
    # Previously there was also a script for packing into .dmg image (see git history).
    # But .dmg triggers additional security measures: because of missing app signature,
    # Chrome warns about unsafe app when downloading. So .zip is more convenient.

    arch=$1 # architecture name, `arm64` | `x86_64`

    cd "build/dist-$arch"
    fileName="Statusbar_Converter_macOS_$arch.app.zip"
    _log "Compressing into zip for $arch"

    zip -qr "$fileName" "Statusbar Converter.app"

    _log "Successfully compressed into \"$fileName\""
)}

_validateExecutableArchitecture() {(set -e
    arch=$1 # architecture name, `arm64` | `x86_64`
    pythonExec=$2 # python executable name, e.g. `python3.10` or `python3.10-intel64`

    platform=$($pythonExec -c 'import platform; print(platform.platform())')

    if [[ "$platform" != *"$arch"* ]]; then
        _logError "Requested architecture ($arch) does not match provided python executable ($platform)"
        exit 1
    else
        _log "Requested architecture ($arch) matches provided python executable ($platform)"
    fi
)}

_validateArchArg() {(set -e
    # $1 - architecture name

    if [ "$1" != 'arm64' ] && [ "$1" != 'x86_64' ]; then
        _logError 'Argument must be either "arm64" or "x86_64"'
        exit 1
    fi
)}

_log() {(set -e
    yellowCode='\033[0;33m'
    resetCode='\033[0m'

    printf "%s> %s%s\n" "$yellowCode" "$1" "$resetCode"
)}

_logError() {(set -e
    redCode='\033[0;31m'
    resetCode='\033[0m'

    printf "%s\nERROR: %s%s\n" "$redCode" "$1" "$resetCode"
)}

# This will call function name from the first argument
# See: https://stackoverflow.com/a/16159057/4110469
"$@"
