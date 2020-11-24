### Release Procedure

#### PyPI

1. Open a branch for the release
1. Update CHANGELOG.md with the most recent changes
1. Bump the version using [`bump2version`](https://github.com/c4urself/bump2version/#bump2version):
    1. Dry run first by running `bumpversion --dry-run --verbose --new-version <desired-version> <part>`. Some examples:
        - Release candidates: `--new-version 0.10.2rc1 num`
        - Alpha releases: `--new-version 0.10.2a1 num`
        - Patch releases: `--new-version 0.10.2.1 patch`
        - Minor releases: `--new-version 0.11.0.1 minor`
        - Major releases: `--new-version 1.0.0.1 major`
    1. Actually modify the files: `bumpversion --commit --no-tag --new-version <desired-version> <part>`
    1. Check the diff with `git diff`
    1. Add the files that were changed with `git add --update`
    1. Copy and paste the commit message from the dry run `git commit -m 'COPY_PASTE_HERE'`
1. Merge to `main`
1. Build source distribution
    - `python setup.py sdist bdist_wheel`
1. Deploy to Test PyPi
    - `twine upload -r testpypi dist/*`
    - Check at https://test.pypi.org/project/dbt-mysql/
1. Deploy to PyPi
    - `twine upload dist/*`
    - Confirm at https://pypi.org/project/dbt-mysql/

PyPi recognizes [pre-release versioning conventions](https://packaging.python.org/guides/distributing-packages-using-setuptools/#pre-release-versioning) and will label "pre-releases" as-such.

#### GitHub

1. Click the [Create a new release](https://github.com/dbeatty10/dbt-mysql/releases/new) link on the project homepage in GitHub
1. Type `v{semantic_version}` as the "tag version" (e.g., `v0.18.0rc2`)
1. Leave the "target" as `main`
1. Type `dbt-mysql {semantic_version}` as the "release title" (e.g. `dbt-mysql 0.18.0rc2`)
1. For pre-releases:
    - leave the description blank
    - Tick the "this is a pre-release" checkbox
1. Click the "publish release" button
