---
name: changelog
description: Create or update CHANGELOG.md in the Keep a Changelog 1.1.0 format. Read the git changes since the last documented point, sort them into Added, Changed, Deprecated, Removed, Fixed and Security, and write short entries in Simplified Technical English (STE). If CHANGELOG.md does not exist, create it from the full git history. Use when the user invokes /changelog, or asks to write, create, update or release the changelog or the release notes.
argument-hint: "[release [<version>]]"
---

# Changelog

Keep `CHANGELOG.md` at the repository root. Follow [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Write every entry in Simplified Technical English (STE).

## 1. Modes

| Call | Mode | What it does |
| --- | --- | --- |
| `/changelog` | Update | Add the new changes to `## [Unreleased]`. If the file does not exist, create it. |
| `/changelog release <version>` | Release | Do an update. Then move the `[Unreleased]` entries into `## [<version>] - <YYYY-MM-DD>`. |
| `/changelog release` | Release | Same as above. Propose a version (see step 8) and ask the user to confirm it. |

## 2. Keep a Changelog rules

- A changelog is for people, not for machines. It is not a copy of the git log.
- Every version has a section. The newest version is first.
- Every version heading has a release date in ISO 8601 format: `YYYY-MM-DD`.
- `## [Unreleased]` is always at the top. It collects the changes for the next version.
- Each version groups its changes by type. Use only these types, in this order:
  1. `### Added`: new features.
  2. `### Changed`: changes to existing features.
  3. `### Deprecated`: features that will be removed in a later version.
  4. `### Removed`: features that are removed now.
  5. `### Fixed`: bug fixes.
  6. `### Security`: fixes for vulnerabilities.
- Do not write an empty type heading. Keep the `## [Unreleased]` heading even when it is empty.
- Every version heading is a link. Put the link references at the bottom of the file.
- State that the project follows Semantic Versioning (SemVer) only if its versions use the `MAJOR.MINOR.PATCH` form.
- Always record deprecations, removals and breaking changes. A user must see what can break.
- A yanked release stays in the file. Add ` [YANKED]` after its date: `## [0.0.5] - 2014-12-13 [YANKED]`.
- Do not change a released section unless the user asks. A rewrite is correct only to fix a mistake, for example a breaking change that the file does not show.

## 3. File layout

Use this layout when you create the file:

```markdown
# Changelog

All notable changes to this project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- changelog-skill: last-documented-commit <full-commit-sha> -->

## [Unreleased]

### Added

- Entry.

## [1.0.0] - 2026-10-20

### Fixed

- Entry.

[unreleased]: https://github.com/<owner>/<repo>/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/<owner>/<repo>/releases/tag/v1.0.0
```

- The HTML comment holds the newest commit that the file documents. Markdown viewers do not show it. Keep exactly one such comment, below the introduction.
- Put one blank line around each heading and around each list.

### Link references

- Get the remote with `git remote get-url origin`. Change `git@github.com:<owner>/<repo>.git` to `https://github.com/<owner>/<repo>`. Remove a `.git` suffix.
- Use the tag form of the existing tags (`v1.0.0` or `1.0.0`). If there are no tags, use `v<version>`.
- `[unreleased]` compares the newest version with `HEAD`: `.../compare/v<newest>...HEAD`. If there is no version yet, use `.../commits/<default-branch>`.
- Each version compares with the previous version: `.../compare/v<previous>...v<version>`. The oldest version uses `.../releases/tag/v<version>`.
- If there is no remote, do not write link references.

## 4. Read the state

Run these commands from the repository root (`git rev-parse --show-toplevel`):

```bash
ls CHANGELOG.md                                  # does the file exist?
git tag --list --sort=-v:refname                 # version tags, newest first
git remote get-url origin                        # base URL for the links
git status --porcelain                           # uncommitted changes
git log -1 --format=%H -- CHANGELOG.md           # last commit that changed the file
```

- If the repository has a file with a different name (`CHANGES.md`, `HISTORY.md`, `NEWS.md`, `changelog.md`), ask the user if you must use it or create `CHANGELOG.md`.
- Also read the version in the project metadata (`pyproject.toml`, `package.json`, or similar). Use it only to propose a version. Do not change it.

## 5. Find the commit range

### The file does not exist (create)

- If version tags exist: make one version section for each tag, from the oldest to the newest. Each section documents the commits between the previous tag and that tag. Its date is the tag date: `git log -1 --format=%as <tag>`. The commits after the newest tag go into `[Unreleased]`.
- If there are no version tags: all commits go into `[Unreleased]`. Tell the user that there are no version tags. Tell them that `/changelog release <version>` makes the first version.

### The file exists (update)

Use the first start point that applies:

1. The commit in the `last-documented-commit` comment, if `git merge-base --is-ancestor <sha> HEAD` succeeds.
2. The tag of the newest version in the file, if that tag exists.
3. The last commit that changed `CHANGELOG.md`.
4. The first commit of the repository.

The range is `<start>..HEAD`. For start points 2 to 4, some changes can already be in the file. Compare each new change with the current entries and do not add a change two times.

If the range has no commits, tell the user: "No new changes since `<start>`." Stop, except in release mode.

### Uncommitted changes

Do not document uncommitted changes. If `git status --porcelain` shows changes, tell the user that the changelog does not include them.

## 6. Read and select the changes

```bash
git log --reverse --no-merges --format='%h %as %s%n%b' <start>..HEAD
git diff --stat <start>..HEAD
git show --stat <sha>                            # one commit
git diff <start>..HEAD -- <path>                 # one file
```

- Commit messages can be short or wrong ("documentation created", "bugs fixed"). The diff is the source of truth. Read the diff when the message does not say what changed for the user.
- Write one entry for each change that a user sees. One entry can cover many commits. One commit can give many entries.
- Include: new or removed endpoints, fields, settings, commands and features. Changes to behavior, defaults, responses and errors. Bug fixes. Deprecations. Security fixes. Dependency changes that change behavior or fix a vulnerability.
- Do not include: changes to tests only, CI only, formatting, lint fixes, refactors with no change in behavior, typo fixes, and merge commits.
- Add documentation only when it is new for users, for example a new user guide. Put it in `Added`.

Use this table to choose the type:

| The change | Type |
| --- | --- |
| A new feature, endpoint, field, setting or command | Added |
| A change to existing behavior, a default, a response or a dependency | Changed |
| A feature that still works but will be removed | Deprecated |
| A feature that is removed | Removed |
| A bug fix | Fixed |
| A fix for a vulnerability | Security |

A commit prefix (`feat:`, `fix:`) is only a hint. The effect of the change decides the type.

## 7. Write the entries in STE

Write for the user of the project, not for its developer. Say what changed and what it does now. Do not tell how you did the work. Keep entries short. Do not give implementation details.

If the `asd-ste100` skill is available, use its STE-flavored mode. These rules always apply:

- One change in each bullet.
- One sentence in each bullet. Use two sentences only when the user must do something, for example after a breaking change.
- Not more than 20 words in each sentence.
- Use the active voice and the present tense.
- Do not repeat the type word. Under `### Added`, do not start with "Added".
- Use simple, common words. Use one word for one meaning in the full file.
- Do not use phrasal verbs ("set up", "get rid of"). Use one verb ("configure", "remove").
- Do not use semicolons.
- Do not use vague words ("various", "some", "improved", "better", "several fixes"). Say what changed.
- Do not stack more than three nouns.
- Put names of endpoints, fields, settings, files and commands in code format: `POST /api/v1/actuators`, `API_KEY`.
- Start a breaking change with `**Breaking:**`. Then tell the user what to do.

| Bad | Good |
| --- | --- |
| Added the content stuff and fixed data bugs. | (Added) Endpoints to create, read, list and delete contents. |
| Various improvements to actuators. | (Changed) `GET /api/v1/actuators` returns only active actuators. |
| Fixed bug where latest wasn't set up properly when creating. | (Fixed) `POST /api/v1/actuators` sets `latest` when the request has `set_latest`. |
| Refactored the repository layer; queries are faster now. | (Do not include. There is no change for the user.) |
| The `token` field has been removed. | (Removed) **Breaking:** The `token` field. Use the `X-API-Key` header. |

## 8. Release mode

1. Do steps 4 to 7 first.
2. If `[Unreleased]` is empty, tell the user. Stop.
3. Get the version from the argument. If there is no argument, propose a version with SemVer and ask the user to confirm it:
   - A breaking change or a `Removed` entry: increase MAJOR. For a `0.y.z` version, increase MINOR.
   - An `Added`, `Changed` or `Deprecated` entry: increase MINOR.
   - Only `Fixed` or `Security` entries: increase PATCH.
   - The first release: propose the version in the project metadata.
4. Make sure that the version is not in the file and is higher than the newest version.
5. Add `## [<version>] - <today>` below `## [Unreleased]`. Get the date with `date +%F`. Move all `[Unreleased]` entries into it. Keep `## [Unreleased]` empty.
6. Update the link references (step 3).
7. Do not create tags, commits or version changes. Tell the user the next steps: update the version in the project metadata, commit, and run `git tag v<version>`.

## 9. Write the file

- Add each new entry below the correct type heading in `[Unreleased]`. If the type heading does not exist, add it in the order of step 2.
- Do not change released sections (step 2).
- Set the `last-documented-commit` comment to the full SHA of `HEAD` (`git rev-parse HEAD`).
- Update the link references.
- Do not commit the file unless the user asks.

## 10. Report to the user

Give a short report:

- The mode (create, update or release) and the commit range.
- The number of entries for each type.
- The changes that you did not include, in one line. For example: "Not included: 3 test commits, 1 CI change."
- Uncommitted changes, if there are some.
- The next step, if there is one (for example, `/changelog release <version>`).

## 11. Check before you finish

- [ ] The file has the title, the introduction, the commit comment and `## [Unreleased]`.
- [ ] The versions go from the newest to the oldest. Each version has a `YYYY-MM-DD` date.
- [ ] The types use the six names only, in the correct order, with no empty type heading.
- [ ] Every entry is one change, one short sentence, active voice, and has no semicolon.
- [ ] No entry is a copy of a commit message. No change is in the file two times.
- [ ] Breaking changes, deprecations and removals are all in the file.
- [ ] Each version heading has a link reference at the bottom (when there is a remote).
- [ ] The `last-documented-commit` comment holds the SHA of `HEAD`.
