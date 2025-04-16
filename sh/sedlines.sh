#!/bin/sh
# (1) Print the lines between the patterns; (2) Filter out the '# \{\{\{' pattern; (3) filter-out
# leading and trailing empty lines; (4) replace space-only lines with empty lines.

C=n
N=0
B=""
E=""

# Parse arguments
while [ $# -gt 0 ]; do
  case $1 in
    -C) C=y ;;
    -f|--filter)
      shift
      if [ -n "$1" ]; then
        N=$1
      else
        echo "Error: -n requires an integer argument" >&2
        exit 1
      fi
      ;;
    -*)
      echo "Invalid option: $1" >&2
      exit 1
      ;;
    *)
      if [ -z "$B" ]; then
        B=$1
      elif [ -z "$E" ]; then
        E=$1
      else
        echo "Usage: sedlines.sh [-n INT] (PAT|START STOP)" >&2
        exit 1
      fi
      ;;
  esac
  shift
done

# Handle setting B and E when only B is provided
if [ -z "$E" ]; then
  if [ -n "$B" ]; then
    E="}}}"
    B="${B}.*{{{"
  else
    echo "Usage: sedlines.sh (PAT|START STOP)" >&2
    exit 1
  fi
fi

filterN() {
  n=$1 # the number of spaces to filter
}


# (1) \
sed -n "/$B/,/$E/{ /^#.*$B/b; /$E/{q;}; p; }" | \
# (2) \
sed "s/#[[:space:]]*{{{//" | \
# (3) \
sed -e :a -e '/^\n*$/{$d;N;ba' -e '}' | \
# (4) \
sed '/./,$!d' | \
{
  if test "$N" != "0"; then
    sed "/^ \{$N\}/,/^$/d"
  else
    cat
  fi
} | \
{
  if test "$C" = "y" ; then
    sed 's/:$//'
  else
    cat
  fi
}
