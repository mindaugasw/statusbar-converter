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

    exe "$venvDir/bin/pip" install --upgrade pip
    exe "$venvDir/bin/pip" install wheel
    # Instead of `pip install` can alternatively use `pip-sync` - it would also remove not needed packages
    exe "$venvDir/bin/pip" install --require-hashes \
        -r "requirements/common.lock" \
        -r "requirements/$os.lock"

    if [[ "$os" == 'linux' ]]; then
        _verifyGiLoads
        _installClipnotify
    fi

    echo -e "$textArrowSuccess Successfully installed venv into $textYellow$venvDir$textReset"
}

# Verify that the UI libs bindings load in the new venv:
# - GTK/glib: fails if the venv was built from a Homebrew Python, whose bundled
#   glibc can't open the system libglib that PyGObject needs.
# - AyatanaAppIndicator3: fails if gir1.2-ayatanaappindicator3-0.1 is missing on the
#   host (needed during PyInstaller analysis and for bundling the Ayatana .so chain).
_verifyGiLoads() {
    echo -e "$textArrow Verifying gi/GTK + AyatanaAppIndicator3 bindings load in the venv"
    "$venvDir/bin/python" -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AyatanaAppIndicator3', '0.1'); from gi.repository import AyatanaAppIndicator3, Gtk"
}

_installClipnotify() {
    local clipnotifyDir='binaries/clipnotify'

    echo -e "$textArrow Installing clipnotify into $textYellow$clipnotifyDir$textReset"

    exe rm -rf "$clipnotifyDir"
    exe git clone https://github.com/cdown/clipnotify.git "$clipnotifyDir"
    exe make -C "$clipnotifyDir"

    echo -e "$textArrow Successfully installed clipnotify into $textYellow$clipnotifyDir$textReset"
}

_installVenv
