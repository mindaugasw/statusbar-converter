#!/usr/bin/env bash
set -eEuo pipefail

# Pre-build dependency guards
# - current venv matches the lock files
# - common deps are platform-neutral
#
# Usage:
#   scripts/verify-dependencies.sh <venvDir>
# E.g.:
#   scripts/verify-dependencies.sh .venv

# shellcheck source=common.sh
source ./scripts/common.sh

venvDir=$1


_verifyDependencies() {
    local os
    os=$(_getOsName)

    _verifyVenvMatchesLock "$os"
    _verifyCommonIsPlatformNeutral
}

_verifyVenvMatchesLock() {
    local os=$1

    echo -e "$textArrow Verifying venv matches lock files"

    local output
    output=$("$venvDir/bin/pip-sync" --dry-run "requirements/common.lock" "requirements/$os.lock")

    if ! grep -q 'Everything up-to-date' <<< "$output"; then
        echo -e "$textError The venv does not match the lock files. pip-sync would change:"
        echo "$output"
        echo -e "Run ${textYellow}just venv-install${textReset} to fix, or ${textYellow}just lock${textReset} if you intended to change deps."
        exit 1
    fi

    echo -e "$textArrow Verifying venv matches lock files - passed"
}

_verifyCommonIsPlatformNeutral() {
    echo -e "$textArrow Verifying common deps are platform-neutral"

    "$venvDir/bin/python" scripts/verify-common-platform-neutral.py "requirements/common.lock"

    echo -e "$textArrow Verifying common deps are platform-neutral - passed"
}

_verifyDependencies
