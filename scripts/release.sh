#!/usr/bin/env bash
git pull --rebase origin main

last_release_number=$(python -c "from gazu import __version__; print(__version__)")
release_number=$(echo "${last_release_number}" | awk -F. -v OFS=. '{$NF += 1 ; print}')

if git rev-parse "v${release_number}" >/dev/null 2>&1; then
    echo "Tag v${release_number} already exists, aborting." >&2
    exit 1
fi

echo "__version__ = \"${release_number}\"" > gazu/__version__.py
git commit gazu/__version__.py -m "${release_number}"
git tag -a -m "Release v${release_number}" "v${release_number}"
git push origin main --follow-tags
