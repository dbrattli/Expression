#!/usr/bin/env bash
# Update the package version when EasyBuild.ShipIt prepares a release.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <semver-version>" >&2
  exit 64
fi

semver="$1"
pep440=$(printf '%s\n' "$semver" | sed -E \
  -e 's/-alpha\.([0-9]+)$/a\1/' \
  -e 's/-beta\.([0-9]+)$/b\1/' \
  -e 's/-rc\.([0-9]+)$/rc\1/')

poetry version "$pep440" >/dev/null
printf '__version__ = "%s"\n' "$pep440" > expression/_version.py

echo "Bumped version to $pep440 (from SemVer $semver)"
