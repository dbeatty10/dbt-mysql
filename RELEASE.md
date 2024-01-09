# Release Procedure

1. [Bump version](#bump-version)
1. [PyPI](#pypi)
1. [GitHub](#github)
1. [Post-release](#post-release)

## Bump version

1. Open a branch for the release
    - `git checkout -b releases/1.5.0`
1. Update [`CHANGELOG.md`](CHANGELOG.md) with the most recent changes
1. Bump the version using [`bump-my-version`](https://github.com/callowayproject/bump-my-version):
    1. Dry run first by running `bump-my-version bump --dry-run --verbose --new-version <desired-version> <part>`. Some examples:
        - Release candidates: `--new-version 1.5.0rc1 num`
        - Alpha releases: `--new-version 1.5.0a1 num`
        - Patch releases: `--new-version 1.5.1 patch`
        - Minor releases: `--new-version 1.5.0 minor`
        - Major releases: `--new-version 2.0.0 major`
    1. Actually modify the files: `bump-my-version bump --no-tag --new-version <desired-version> <part>`. An example:
        - Minor releases: `bump-my-version bump --no-tag --new-version 1.5.0 minor`
  1. Check the diff with `git diff`
  1. Add the files that were changed with `git add --update`
  1. Commit with message `Release dbt-mysql v<desired-version>`
  1. `git push`
  1. Merge back into `main` branch

## PyPI

1. Build source distribution
    - `python setup.py sdist bdist_wheel`
1. Deploy to Test PyPI
    - `twine upload -r testpypi dist/*`
    - Check at https://test.pypi.org/project/dbt-mysql/
1. Deploy to PyPI
    - `twine upload dist/*`
    - Confirm at https://pypi.org/project/dbt-mysql/

PyPI recognizes [pre-release versioning conventions](https://packaging.python.org/guides/distributing-packages-using-setuptools/#pre-release-versioning) and will label "pre-releases" as-such.

## GitHub

1. Click the [Create a new release](https://github.com/dbeatty10/dbt-mysql/releases/new) link on the project homepage in GitHub
1. Click the "Choose a tag" drop-down
    1. Type `v{semantic_version}` (e.g., `v1.5.0rc2`) and click "+ Create a new tag: {version} on publish"
1. Update the "Target" to be the name of the release branch
1. Type `dbt-mysql {semantic_version}` as the "release title" (e.g. `dbt-mysql 1.5.0rc2`)
1. Leave the description blank
1. For pre-releases:
    - Tick the "This is a pre-release" checkbox
1. Click the "Publish release" button

## Post-release
  1. Create `{minor-version}.latest` branch. Example:
    - `git checkout -b 1.5.latest`
    - Update the branch names in `dev-requirements.txt` from `@{previous-version}.latest` (or `@main`) to `@{minor-version}.latest`
    - `git push`
  1. Bump the version in `main` to be the next minor alpha. Example:
    - `git checkout main`
    - `git pull`
    - `git checkout -b bump-1.6.0a1`
    - Minor releases:
        `bump-my-version bump --no-tag --new-version 1.6.0a1 num`
    - Update the branch names in `dev-requirements.txt` from `@{previous-version}.latest` to `@{minor-version}.latest` (or `@main`)
    - Commit with message `Bump dbt-mysql 1.6.0a1`
    - `git push`
