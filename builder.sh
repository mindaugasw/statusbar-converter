#!/usr/bin/env bash

# Usage examples:
# `install arm python3.10` or `install intel python3.10-intel64`
# `build arm` or `build intel`

install() {(set -e
    # Prepare virtualenv for given architecture

    arch=$1 # architecture name, `arm` | `intel`
    pythonExec=$2 # python executable name, e.g. `python3.10` or `python3.10-intel64`

    _validateArchArg $arch

    if [ -z "$pythonExec" ]; then
        _logError 'Python executable must be provided as argument (e.g. "python3.10" or "python3.10-intel64")'
        exit 1
    fi

    _validateExecutableArchitecture $arch $pythonExec

    venvPath=".venv-$arch"
    _log "Installing virtualenv to \"$venvPath\""

    $pythonExec -m venv .venv-$arch --clear --copies

    source "$venvPath/bin/activate"

    pip install wheel
    pip install -r requirements_macos.txt

    _log "Successfully installed virtualenv to \"$venvPath\""
)}

build() {(set -e
    arch=$1 # architecture name, `arm` | `intel`

    _validateArchArg $arch
    fullArchName=$(_getFullArchName $arch)
    venvPath=".venv-$arch"
    distPath="dist/$fullArchName"

    source "$venvPath/bin/activate"

    rm -rf ./$distPath ./build/ ./*.spec

    _log "Starting build for $fullArchName"

    $venvPath/bin/pyinstaller \
        --clean \
        --name "Statusbar Converter" \
        --onedir \
        --windowed \
        --add-data '../../assets:assets' \
        --add-data '../../config:config' \
        --distpath "$distPath" \
        --workpath "$distPath/build" \
        --specpath "$distPath" \
        --icon '../../assets/icon.png' \
        --target-arch "$fullArchName" \
        --osx-bundle-identifier 'com.mindaugasw.statusbar_converter' \
        start.py

    _log "Successfully built for $fullArchName in $distPath"

    _createZip $fullArchName
)}

_createDmg() {(set -e
    # No longer used. .dmg image triggers additional safety measures for unsigned apps:
    # - Chrome warns about unsafe file when downloading. .zip avoids this problem
    # - Still need to manually un-quarantine app with `xattr -d com.apple.quarantine path.app`
    #   For .dmg it's always needed for download. .zip seems to avoid quarantine
    #   after download but only on the same machine that it was built on

    # `create-dmg` in path is required
    # `brew install create-dmg`

    arch=$1 # full architecture name, `arm64` | `x86_64`

    _log "Packing into dmg image for $arch"

    fileName="Statusbar_Converter_macOS_$arch.dmg"

    cd dist/$arch

    # create-dmg includes all files in the directory. So we copy only the needed stuff to a new directory
    rm -rf dmg/ ./*.dmg
    mkdir dmg
    cp -r 'Statusbar Converter.app' 'dmg/Statusbar Converter.app'

    create-dmg \
        --volname 'Statusbar Converter' \
        --icon-size 80 \
        --text-size 14 \
        --icon 'Statusbar Converter.app' 190 0 \
        --app-drop-link 0 0 \
        --hide-extension 'Statusbar Converter.app' \
        $fileName \
        dmg/

    rm -rf dmg/

    _log "Successfully packed into dmg image \"$fileName\""
)}

_createZip() {(set -e
    arch=$1 # full architecture name, `arm64` | `x86_64`

    cd "dist/$arch"
    fileName="Statusbar_Converter_macOS_$arch.app.zip"
    _log "Compressing into zip for $arch"

    zip -r "$fileName" "Statusbar Converter.app"

    _log "Successfully compressed into \"$fileName\""
)}

_validateExecutableArchitecture() {(set -e
    arch=$1 # architecture name, `arm` | `intel`
    pythonExec=$2 # python executable name, e.g. `python3.10` or `python3.10-intel64`

    _validateArchArg $arch

    platform=$($pythonExec -c 'import platform; print(platform.platform())')
    needle=$(_getFullArchName $arch)

    if [[ "$platform" != *"$needle"* ]]; then
        _logError "Requested architecture ($arch) does not match provided python executable ($platform)"
        exit 1
    else
        _log "Requested architecture ($arch) matches provided python executable ($platform)"
    fi
)}

_validateArchArg() {(set -e
    # $1 - architecture name

    if [ "$1" != 'arm' ] && [ "$1" != 'intel' ]; then
        _logError 'Argument must be either "arm" or "intel"'
        exit 1
    fi
)}

_getFullArchName() {(set -e
    # $1 - architecture name

    if [ "$1" == 'arm' ]; then
        printf 'arm64'
    elif [ "$1" == 'intel' ]; then
        printf 'x86_64'
    else
        _logError 'Argument must be either "arm" or "intel"'
        exit 1
    fi
)}

_log() {(set -e
    yellowCode='\033[0;33m'
    resetCode='\033[0m'

    printf "$yellowCode> $1$resetCode\n"
)}

_logError() {(set -e
    redCode='\033[0;31m'
    resetCode='\033[0m'

    printf "$redCode\nERROR: $1$resetCode\n"
)}

# This will call function name from the first argument
# See: https://stackoverflow.com/a/16159057/4110469
"$@"
