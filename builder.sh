#!/usr/bin/env bash

# Usage:
# `install arm64 python3.10` (arm64 native on macOS)
# `install x86_64 python3.10` (x86_64 native on macOS/Linux)
# `install x86_64 python3.10-intel64` (building x86_64 on arm64 on macOS)
#
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

    os=$(_getOsName)
    venvPath=".venv-$os-$arch"
    # ${var:?} needed to safeguard against deleting /* if variable is empty
    rm -rf "${venvPath:?}/*"
    _log "Installing virtualenv to \"$venvPath\""

    $pythonExec -m venv "$venvPath" --clear --copies

    source "$venvPath/bin/activate"

    pip install wheel
    pip install -r "requirements_$os.txt"

    if [[ "$os" == 'linux' ]]; then
        _installLinux "$venvPath"
    fi

    _log "Successfully installed virtualenv to \"$venvPath\""
)}

_installLinux() {(set -e
    # $1 - virtualenv path
    venvPath=$1

    _log "Installing clipnotify"

    clipnotifyPath="binaries/clipnotify"
    rm -rf "$clipnotifyPath"
    git clone https://github.com/cdown/clipnotify.git "$clipnotifyPath"
    make -C "$clipnotifyPath"

    _log "Successfully installed clipnotify"

    # TODO solve this somehow better. Installing PyGObject directly into virtualenv seems not possible
    cp -r /usr/lib/python3/dist-packages/gi "$venvPath/lib/python3.10/site-packages/gi"
)}

buildSpec() {(set -e
    arch=$1 # architecture name, `arm64` | `x86_64`
    os=$(_getOsName)

    _validateArchArg "$arch"

    _log "Generating spec for $os-$arch"

    venvPath=".venv-$os-$arch"
    specFilePath="build/spec-$os-$arch.spec"
    rm -f "$specFilePath"

    source "$venvPath/bin/activate"

    if [ "$os" == 'macos' ]; then
        "$venvPath/bin/pyi-makespec" \
            --name "Statusbar Converter" \
            --onedir \
            --windowed \
            --add-data '../assets:assets' \
            --add-data '../config:config' \
            --add-data '../version:.' \
            --icon '../assets/icon_macos.png' \
            --target-arch "$arch" \
            --osx-bundle-identifier 'com.mindaugasw.statusbar_converter' \
            --specpath 'build' \
            start.py
    else
        "$venvPath/bin/pyi-makespec" \
            --name "Statusbar Converter" \
            --onefile \
            --add-data '../assets:assets' \
            --add-data '../config:config' \
            --add-data '../version:.' \
            --add-binary '../binaries/clipnotify/clipnotify:binaries/clipnotify' \
            --icon '../assets/icon_linux.png' \
            --specpath 'build' \
            start.py
    fi

    mv "build/Statusbar Converter.spec" "$specFilePath"

    _log "Successfully generated spec at $specFilePath"
    _log "Build the executable by running \`./builder.sh build $arch\`"
)}

build() {(set -e
    arch=$1 # architecture name, `arm64` | `x86_64`
    os=$(_getOsName)

    _validateArchArg "$arch"
    venvPath=".venv-$os-$arch"
    distPath="build/dist-$os-$arch"

    source "$venvPath/bin/activate"

    rm -rf "./$distPath"

    _log "Starting build for $os-$arch"

    "$venvPath/bin/pyinstaller" \
        --clean \
        --distpath "$distPath" \
        --workpath "$distPath/build" \
        "build/spec-$os-$arch.spec"

    _log "Successfully built in $distPath"

    _createZip "$arch" "$os"
)}

_createZip() {(set -e
    # Compress app to .zip archive.
    # Previously there was also a script for packing into .dmg image for macOS (see git history).
    # But .dmg triggers additional security measures: because of missing app signature,
    # Chrome warns about unsafe app when downloading. So .zip is more convenient.

    arch=$1 # architecture name, `arm64` | `x86_64`
    os=$2 # OS name, `linux` | `macos`
    version=$(cat 'version' | xargs)

    cd "build/dist-$os-$arch"

    if [ "$os" == 'macos' ]; then
        compressContent='Statusbar Converter.app'

        if [ "$arch" == 'arm64' ]; then
            fileName=$(printf 'Statusbar_Converter_v%s_macOS_AppleSilicon_%s.app.zip' "$version" "$arch")
        else
            fileName=$(printf 'Statusbar_Converter_v%s_macOS_intel_%s.app.zip' "$version" "$arch")
        fi
    else
        compressContent='Statusbar Converter'
        fileName=$(printf 'Statusbar_Converter_v%s_linux_%s.zip' "$version" "$arch")
    fi

    _log "Compressing into zip for $os-$arch"

    zip -qr "$fileName" "$compressContent"

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

_getOsName() {(set -e
    name=$(uname)

    if [ "$name" == 'Linux' ]; then
        echo 'linux'
    elif [ "$name" == 'Darwin' ]; then
        echo 'macos'
    else
        _logError "Unsupported OS type: $name"
        exit 1
    fi
)}

_log() {(set -e
    yellowCode='\033[0;33m'
    resetCode='\033[0m'

    echo -e "$yellowCode> $1$resetCode"
)}

_logError() {(set -e
    redCode='\033[0;31m'
    resetCode='\033[0m'

    echo -e "$redCode> ERROR: $1$resetCode"
)}

# This will call function name from the first argument
# See: https://stackoverflow.com/a/16159057/4110469
"$@"
