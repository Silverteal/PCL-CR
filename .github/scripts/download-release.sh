set -euo pipefail
gh release view "$RELEASE_TAG" --repo "$GITHUB_REPOSITORY" \
  --json tagName,isPrerelease,isDraft,publishedAt,body,assets > release.json
gh release download "$RELEASE_TAG" --repo "$GITHUB_REPOSITORY" \
  --dir release-assets --pattern '*.exe' --pattern '*.zip'
gh api --method GET -f ref="$RELEASE_TAG" \
  -H 'Accept: application/vnd.github.raw+json' \
  "repos/$GITHUB_REPOSITORY/contents/Plain%20Craft%20Launcher%202/metadata.json" \
  > release-metadata.json
