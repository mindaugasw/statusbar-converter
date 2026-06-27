#!/usr/bin/env bash
set -eEuo pipefail

# Build the distributable app.
# A spec file must be generated first with build-spec.sh.
#
# Usage:
#   scripts/build.sh <venvDir>
# E.g.:
#   scripts/build.sh .venv

# shellcheck source=common.sh
source ./scripts/common.sh

venvDir=$1


_build() {
    local os arch
    os=$(_getOsName)
    arch=$(_getArchitecture)

    local specFilePath="build/spec-$os-$arch.spec"
    local distDir="build/dist-$os-$arch"

    echo -e "$textArrow Starting build for ${textYellow}${os}-${arch}${textReset}"

    exe ./scripts/verify-dependencies.sh "$venvDir"

    exe rm -rf "$distDir"

    exe "$venvDir/bin/pyinstaller" \
        --clean \
        --distpath "$distDir" \
        --workpath "$distDir/build" \
        "$specFilePath"

    _createZip "$os" "$arch" "$distDir"

    echo -e "$textArrowSuccess Successfully built ${textYellow}${os}-${arch}${textReset} into ${textYellow}${distDir}${textReset}"
}

_createZip() {
    # Compress the app into a .zip archive.
    local os=$1 arch=$2 distDir=$3

    local version
    version=$(xargs < version)

    local compressContent fileName

    if [[ "$os" == 'macos' ]]; then
        compressContent='Statusbar Converter.app'
        fileName="Statusbar_Converter_v${version}_macOS_${arch}.app.zip"
    else
        compressContent='Statusbar Converter'
        fileName="Statusbar_Converter_v${version}_linux_${arch}.zip"
    fi

    echo -e "$textArrow Compressing into zip"

    # Run from within the dist dir so the archive holds the app at its top level
    ( cd "$distDir" && exe zip -qr "$fileName" "$compressContent" )
}

_createDmg() {
    # `create-dmg` must be in PATH (`brew install create-dmg`)

    # Note that .dmg triggers additional security measures. Because of the missing app signature
    # Chrome warns about an unsafe app when downloading. So .zip is more convenient.

    # DEPRECATED: because of the reason above, dmg packing is no longer used and this function is no longer maintained.

    local arch=$1 distDir=$2

    local version
    version=$(xargs < version)

    local fileName
    fileName="Statusbar_Converter_v${version}_macOS_${arch}.dmg"

    echo -e "$textArrow Packing into dmg image for ${textYellow}${arch}${textReset}"

    (
        cd "$distDir"

        # create-dmg includes all files in the directory, so copy only the needed app to a clean dir
        exe rm -rf dmg/ ./*.dmg
        exe mkdir dmg
        exe cp -r 'Statusbar Converter.app' 'dmg/Statusbar Converter.app'

        create-dmg \
            --volname 'Statusbar Converter' \
            --icon-size 80 \
            --text-size 14 \
            --icon 'Statusbar Converter.app' 0 0 \
            --app-drop-link 190 0 \
            --hide-extension 'Statusbar Converter.app' \
            "$fileName" \
            dmg/

        exe rm -rf dmg/
    )

    echo -e "$textArrowSuccess Successfully packed into dmg image ${textYellow}${fileName}${textReset}"
}

_build
