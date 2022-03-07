### Release Procedure

#### Bump version

1. Open a branch for the release
    - `git checkout -b releases/0.19.0rc1`
1. Update [`CHANGELOG.md`](CHANGELOG.md) with the most recent changes
1. Bump the version using [`bump2version`](https://github.com/c4urself/bump2version/#bump2version):
    1. Dry run first by running `bumpversion --dry-run --verbose --new-version <desired-version> <part>`. Some examples:
        - Release candidates: `--new-version 0.10.2rc1 num`
        - Alpha releases: `--new-version 0.10.2a1 num`
        - Patch releases: `--new-version 0.10.2.1 patch`
        - Minor releases: `--new-version 0.11.0.1 minor`
        - Major releases: `--new-version 1.0.0.1 major`
    1. Actually modify the files: `bumpversion --no-tag --new-version <desired-version> <part>`
  1. Check the diff with `git diff`
  1. Add the files that were changed with `git add --update`
  1. Commit with message `Release dbt-mysql v<desired-version>`
  1. `git push`
  1. Merge back into `{minor-version}.latest` branch
  1. If appropriate, merge back into `main` branch

#### PyPI

1. Build source distribution
    - `python setup.py sdist bdist_wheel`
1. Deploy to Test PyPI
    - `twine upload -r testpypi dist/*`
    - Check at https://test.pypi.org/project/dbt-mysql/
1. Deploy to PyPI
    - `twine upload dist/*`
    - Confirm at https://pypi.org/project/dbt-mysql/

PyPI recognizes [pre-release versioning conventions](https://packaging.python.org/guides/distributing-packages-using-setuptools/#pre-release-versioning) and will label "pre-releases" as-such.

#### GitHub

1. Click the [Create a new release](https://github.com/dbeatty10/dbt-mysql/releases/new) link on the project homepage in GitHub
1. Click the "Choose a tag" drop-down
    1. Type `v{semantic_version}` (e.g., `v0.18.0rc2`) and click "+ Create a new tag"
1. Update the "Target" to be the name of the release branch
1. Type `dbt-mysql {semantic_version}` as the "release title" (e.g. `dbt-mysql 0.18.0rc2`)
1. Leave the description blank
1. For pre-releases:
    - Tick the "This is a pre-release" checkbox
1. Click the "Publish release" button
