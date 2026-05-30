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
