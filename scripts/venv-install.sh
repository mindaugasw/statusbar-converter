#!/usr/bin/env bash
set -eEuo pipefail

# Install the Python virtual env into the given directory.
#
# Usage:
#   scripts/venv-install.sh <venvDir> <basePythonBinary>
# E.g.:
#   scripts/venv-install.sh .venv python3.10

# shellcheck source=common.sh
source ./scripts/common.sh

venvDir=$1
basePythonBinary=$2


_installVenv() {
    local os
    os=$(_getOsName)

    echo -e "$textArrow Installing venv into $textYellow$venvDir$textReset from $textYellow$basePythonBinary$textReset for $textYellow$os$textReset os"

    # --clear - delete the contents of the env dir if it already exists, before creation
    # --copies - use copies rather than symlinks, even when symlinks are the platform default
    exe "$basePythonBinary" -m venv "$venvDir" --clear --copies

    exe "$venvDir/bin/pip" install wheel
    exe "$venvDir/bin/pip" install -r "requirements_common.txt"
    exe "$venvDir/bin/pip" install -r "requirements_$os.txt"

    if [[ "$os" == 'linux' ]]; then
        _installClipnotify
        _installGi
    fi

    echo -e "$textArrowSuccess Successfully installed venv into $textYellow$venvDir$textReset"
}

_installClipnotify() {
    local clipnotifyDir='binaries/clipnotify'

    echo -e "$textArrow Installing clipnotify into $textYellow$clipnotifyDir$textReset"

    exe rm -rf "$clipnotifyDir"
    exe git clone https://github.com/cdown/clipnotify.git "$clipnotifyDir"
    exe make -C "$clipnotifyDir"

    echo -e "$textArrow Successfully installed clipnotify into $textYellow$clipnotifyDir$textReset"
}

_installGi() {
    echo -e "$textArrow Copying gi from host system"

    # Installing PyGObject directly into the virtual env seems not possible,
    # so we copy the system package instead. This should be solved somehow better
    local venvSitePackagesDir
    venvSitePackagesDir=$(echo "$venvDir"/lib/python*/site-packages)

    exe cp -r /usr/lib/python3/dist-packages/gi "$venvSitePackagesDir/gi"
}

_installVenv
