set -e
git pull --rebase origin main
last_release_number=$(python -c "from gazu import __version__; print(__version__)")
release_number=$(echo ${last_release_number} | awk -F. -v OFS=. '{$NF += 1 ; print}')
echo "__version__ = \"$release_number\"" > gazu/__version__.py
git commit gazu/__version__.py -m $release_number
git tag v$release_number
git push origin main --follow-tags
