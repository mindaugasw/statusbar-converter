#!/usr/bin/env bash
set -eEuo pipefail

export textYellow='\e[33m'
export textRed='\e[31m'
export textGreenBright='\e[92m'
export textBold='\e[1m'
export textReset='\e[0m'
export textArrow="$textYellow>$textReset"
export textArrowSuccess="$textGreenBright$textBold>$textReset"
export textError="$textRed> ERROR:$textReset"

# Print given command and then run it
# From https://stackoverflow.com/a/23342259/4110469
function exe() {
    # shellcheck disable=SC2145
    echo -e "${textYellow}\$ $@${textReset}"
    "$@"
}

_getOsName() {
    local name
    name=$(uname)
    # ${var,,} syntax converts string to lowercase
    name=${name,,}

    if [[ "$name" == 'linux' ]]; then
        echo 'linux'
    elif [[ "$name" == 'darwin' ]]; then
        echo 'macos'
    else
        echo -e "$textError Unknown OS type: $name" >&2
        exit 1
    fi
}

_getArchitecture() {
    local name
    name=$(uname -m)

    if [[ "$name" != 'arm64' ]] && [[ "$name" != 'x86_64' ]]; then
        echo -e "$textError Unknown architecture type: $name" >&2
        exit 1
    fi

    echo "$name"
}
