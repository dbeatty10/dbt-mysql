# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

---

### Report Bugs

Report bugs at https://github.com/dbeatty10/dbt-mysql/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

dbt-mysql could always use more documentation, whether as part of the
official dbt-mysql docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/dbeatty10/dbt-mysql/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project and contributions are
  welcome :)

## Get Started!

---

Ready to contribute? [Here's](https://jarv.is/notes/how-to-pull-request-fork-github/) how to set up `dbt-mysql` for local development.

1. Fork the `dbt-mysql` repo on GitHub.
2. Clone your fork locally:
    ```shell
    $ git clone git@github.com:your_name_here/dbt-mysql.git
    ```

3. Installation:
    ```shell
    $ python3 -m venv env
    $ source env/bin/activate
    $ python3 -m pip install --upgrade pip
    $ python3 -m pip install -r requirements-dev.txt -r requirements-editable.txt
    $ pre-commit install
    $ source env/bin/activate
    ```

4. Create a branch for local development:

    ```shell
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

   Now you can make your changes locally.

5. Run tests:

    ```shell
    $ python -m pytest -v tests/unit
    ```

   Instructions for running integration tests in `tests/README.md`.

6. Commit your changes and push your branch to GitHub:

    ```shell
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.
