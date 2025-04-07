#!/bin/sh

DELAY=3
unset VIRTUAL_ENV_PROMPT
unset PS1

# https://stackoverflow.com/a/77819553
# mln() { echo -en ""$'\033['${1}D${2}"" ; }


while true; do
  # echo -n '?'
  while ! make "$@" >>_make.log 2>&1 ; do
    # mln 1 1
    echo -n "F\a"
    sleep "$DELAY"
    # echo -n '?'
  done
  # mln 1 1
  echo -n .
  sleep "$DELAY"
  inotifywait \
    --exclude '_.*' \
    -r -e modify,move,create,delete \
    . \
    >_make.log 2>&1
done

