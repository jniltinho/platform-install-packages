---
name: create-release
description: Cut a versioned release of kaltura-console (the Go console in kaltura-console/ of this monorepo) on GitHub — bump its CHANGELOG, tag kaltura-console/vX.Y.Z, push (GitHub Actions builds and publishes tar.gz/.deb/.rpm), then enrich the release notes with gh. Use when the user asks to "create a release", "release vX" of the console, "fechar a release" or "publicar a versão".
license: MIT
compatibility: Requires git + gh (GitHub CLI, authenticated). Artifacts are built by .github/workflows/kaltura-console-release.yml.
---

# Releasing kaltura-console (monorepo, GitHub + gh)

The console lives in `kaltura-console/` inside `github.com/jniltinho/platform-install-packages`, next to the Kaltura packaging. Its releases are **tag-prefixed** so they never collide with the Kaltura package releases (`noble-deb-*`, `sources-*`):

- tag: `kaltura-console/vX.Y.Z`
- package version: `X.Y.Z` (pre-releases `X.Y.Z-rc1` → package `X.Y.Z~rc1`)

A release is: update `kaltura-console/CHANGELOG.md`, commit, tag, push, **wait for Actions**, then **enrich the release notes with `gh`** (step 8, every time).

> ⚠️ The version comes from the tag (`Makefile`: `git describe --tags --match 'kaltura-console/v*'` → ldflags `-X kaltura-console/internal/buildinfo.Version=…`). There is **no version constant in code**.

## Project facts

```bash
OWNER=jniltinho
REPO=platform-install-packages
PREFIX=kaltura-console/
LAST=$(git describe --tags --abbrev=0 --match "${PREFIX}v*" 2>/dev/null || echo "")
echo "Last tag: ${LAST:-none}"
```

### Versioning

Series `0.x` (pre-1.0):

- **Feature** → bump **minor**: `v0.1.0` → `v0.2.0`
- **Fix / docs / infra only** → bump **patch**
- **First release** → `v0.1.0`

```bash
if [ -z "$LAST" ]; then NEXT=${PREFIX}v0.1.0; else
  V=${LAST#${PREFIX}v}; IFS=. read -r MAJ MIN PAT <<< "$V"
  NEXT="${PREFIX}v${MAJ}.$((MIN+1)).0"      # feature
  # NEXT="${PREFIX}v${MAJ}.${MIN}.$((PAT+1))"  # fix only
fi
echo "Next: $NEXT"
```

## Process

### 1. Prerequisites

```bash
gh auth status
git fetch origin && git status          # clean except the release changes
cd kaltura-console && make lint test build && cd ..
```

### 2. Review changes since the last console tag (console paths only)

```bash
git log ${LAST:+$LAST..}HEAD --oneline -- kaltura-console/ .github/workflows/kaltura-console-release.yml
```

### 3. Update `kaltura-console/CHANGELOG.md`

Keep a Changelog, **English**, keep `## [Unreleased]` on top:

```markdown
## [Unreleased]

## [0.2.0] — YYYY-MM-DD
**One- or two-line summary.**
### Added / ### Changed / ### Fixed / ### Security   (omit empty ones)
```

### 4. Commit + annotated tag

```bash
git add kaltura-console/CHANGELOG.md   # plus intentional release docs only
git commit -m "chore(release): $NEXT — <short summary>"
git tag -a "$NEXT" -m "Release $NEXT — <short summary>"
```

Never stage `.agents/`, `.claude/`, `kaltura-console/web/dist/`, `config.toml`, `*.db`, or secrets.

### 5. Push branch + tag (triggers Actions)

```bash
git push origin HEAD
git push origin "$NEXT"
```

### 6. Wait for the workflow

```bash
gh run list -R "$OWNER/$REPO" --workflow=kaltura-console-release.yml --limit 5
gh run watch -R "$OWNER/$REPO"
```

### 7. Verify assets

```bash
gh release view "$NEXT" -R "$OWNER/$REPO" --json assets,url,tagName
```

Expect (`VER=${NEXT#${PREFIX}v}`): `kaltura-console_${VER}_linux_amd64.tar.gz`, `kaltura-console_${VER}_amd64.deb`, `kaltura-console-${VER}-1.x86_64.rpm`, `SHA256SUMS`.

### 8. Enrich release notes — REQUIRED

Title: the tag. Body starts with `# Release <tag>`, sections with emoji headers (omit empty): `## ✨ New Features`, `## 🔧 Improvements`, `## 🐛 Fixes`, `## 🔒 Security`, `## 📚 Documentation`, `## 📦 Package` (asset names + install one-liners), and a **Full Changelog** compare link (`compare/${LAST}...${NEXT}` or `commits/${NEXT}` for the first release).

```bash
gh release edit "$NEXT" -R "$OWNER/$REPO" --title "$NEXT" --notes-file /tmp/notes.md
```

### 9. (Optional) OpenSpec

If the release closes an OpenSpec change (e.g. `add-kaltura-console-go`), archive it and commit separately.

## Guardrails

- Never treat "tag pushed" as done — enrich the notes every release.
- Never push a tag before `make lint test build` is green.
- Never reuse or move a published tag; cut a new patch instead.
- Never hardcode tokens; rely on `gh auth`.
- Only `kaltura-console/v*` tags belong to this skill; do not touch the Kaltura package releases.
