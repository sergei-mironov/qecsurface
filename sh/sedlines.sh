#!/bin/sh
# (1) Print the lines between the patterns; (2) Filter out the '# \{\{\{' pattern; (3) filter-out
# leading and trailing empty lines; (4) replace space-only lines with empty lines.

if test -n "$2" ; then
  B=$1
  E=$2
elif test -n "$1" ; then
  B="${1}.*{{{"
  E="}}}"
else
  echo "Usage: sedlines.sh (PAT|START STOP)" >&2
  exit 1
fi

# (1) \
sed -n "/$B/,/$E/{ /^#.*$B/b; /$E/{q;}; p; }" | \
# (2) \
sed "s/#[[:space:]]*{{{//" | \
# (3) \
sed -e :a -e '/^\n*$/{$d;N;ba' -e '}' | \
# (4) \
sed '/./,$!d'
