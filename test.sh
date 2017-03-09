#!/usr/bin/env bash

set -e -x

script="$PWD/signal-wont-let-me-attach.py"

run_test() {
    local python="$1"
    local name="$2"
    local output="$3"
    input="$(mktemp '/tmp/'"$name"'-XXXXX')"
    cd "$(dirname "$input")"
    yes dummy | nl | head -c $((1024 * 1024)) >"$input"
    if [ -z "$output" ]; then
        "$python" "$script" "$input"
        output="$input.png"
    else
        "$python" "$script" "$input" "$output"
    fi
    file "$output" | grep -q 'PNG image data'
    mv "$input" "$input.bak"
    "$python" "$script" "$output"
    cmp "$input" "$input.bak"
    rm "$input" "$input.bak"
    cd -
}

# check PEP 8 compliance
hash pep8 && pep8 "$script"

# test wrong arguments
"$script" &>/dev/null && exit 1 || true
"$script" a b c &>/dev/null && exit 1 || true
"$script" a.png b &>/dev/null && exit 1 || true

# test file not found
"$script" not_exists && exit 1 || true
"$script" not_exists not_exists.png && exit 1 || true
"$script" not_exists.png && exit 1 || true

# test features
for python in python2 python3; do
    run_test "$python" 'file_in'
    run_test "$python" 'FÌLÈ_IN'
    run_test "$python" 'file_in' 'file_out.png'
    run_test "$python" 'FÌLÈ_IN' 'file_out.png'
    run_test "$python" 'file_in' 'FÌLÈ_OUT.png'
    run_test "$python" 'FÌLÈ_IN' 'FÌLÈ_OUT.png'
done
