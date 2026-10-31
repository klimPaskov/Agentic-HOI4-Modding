#!/bin/sh
# Run the first Python 3.9 or newer found on this machine with the given arguments.
#
#     sh .tools/py.sh .tools/check.py quick
#
# The Claude Code hook in .claude/settings.json and the optional Git hook use it, because the
# interpreter has a different name on each machine (python3, python, or the Windows py launcher),
# and Windows can have Microsoft Store placeholders that only print an install hint.
# Exits 127 with a message when no usable Python is found.

check='import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'
if [ "${OS:-}" = "Windows_NT" ]; then
  candidates="py python3 python"
else
  candidates="python3 python py"
fi
for candidate in $candidates; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  if [ "$candidate" = "py" ]; then
    py -3 -c "$check" >/dev/null 2>&1 && exec py -3 "$@"
  else
    "$candidate" -c "$check" >/dev/null 2>&1 && exec "$candidate" "$@"
  fi
done
echo "No Python 3.9 or newer was found (tried python3, python and py -3). Install Python 3.9 or newer, then rerun: python $*" >&2
exit 127
