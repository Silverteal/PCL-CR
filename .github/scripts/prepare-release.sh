set -euo pipefail
version="${RELEASE_VERSION#v}"
tag="v$version"
git check-ref-format "refs/tags/$tag"
if [ "$GITHUB_REF_TYPE" = tag ]; then
  if [ "$UPDATE_VERSION" = true ]; then
    echo 'Cannot modify source versions when releasing from a tag' >&2
    exit 1
  fi
  if [ "$GITHUB_REF_NAME" != "$tag" ]; then
    echo 'Release version must match the selected tag' >&2
    exit 1
  fi
fi
args=("$version" "$CONFIGURATION" --code "$VERSION_CODE")
if [ "$UPDATE_VERSION" != true ]; then args+=(--check); fi
python3 .github/scripts/prepare-release.py "${args[@]}"
if [ "$UPDATE_VERSION" = true ]; then
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
  git add -- 'Plain Craft Launcher 2/metadata.json' 'Plain Craft Launcher 2/Plain Craft Launcher 2.csproj'
  git -c commit.gpgsign=false commit -m "chore(release): set version $version"
  git push origin "HEAD:refs/heads/$GITHUB_REF_NAME"
fi
echo "sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
echo "version=$version" >> "$GITHUB_OUTPUT"
