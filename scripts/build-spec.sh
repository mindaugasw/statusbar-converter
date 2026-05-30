#!/usr/bin/env bash
set -eEuo pipefail

# Generate a PyInstaller spec file for the given architecture.
# After generating, modify the spec file manually as needed, then build with build.sh.
#
# Usage:
#   scripts/build-spec.sh <venvDir>
# E.g.:
#   scripts/build-spec.sh .venv

# shellcheck source=common.sh
source ./scripts/common.sh

venvDir=$1


_getArchitecture() {
    os=$1

    if [ "$os" == 'macos' ]; then
        echo 'arm64'
    elif [ "$os" == 'linux' ]; then
        echo 'x86_64'
    fi
}

_buildSpec() {
    local os arch
    os=$(_getOsName)
    arch=$(_getArchitecture "$os")

    local specFilePath="build/spec-$os-$arch.spec"

    echo -e "$textArrow Generating spec for $textYellow$os-$arch$textReset"

    exe rm -f "$specFilePath"

    if [[ "$os" == 'macos' ]]; then
        "$venvDir/bin/pyi-makespec" \
            --name 'Statusbar Converter' \
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
        "$venvDir/bin/pyi-makespec" \
            --name 'Statusbar Converter' \
            --onefile \
            --add-data '../assets:assets' \
            --add-data '../config:config' \
            --add-data '../version:.' \
            --add-binary '../binaries/clipnotify/clipnotify:binaries/clipnotify' \
            --icon '../assets/icon_linux.png' \
            --specpath 'build' \
            start.py
    fi

    exe mv "build/Statusbar Converter.spec" "$specFilePath"

    echo -e "$textArrowSuccess Successfully generated spec into $textYellow$specFilePath$textReset"
    echo -e "$textArrow Build the executable by running $textYellow""just build$textReset"
}

_buildSpec
