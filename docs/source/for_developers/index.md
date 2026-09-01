# For developers

!!! note

    The content of this section is under continuous improvement as the project gathers
    more contributors. It is highly inspired by [Scikit-Learn](https://scikit-learn.org/dev/developers/contributing.html#ways-to-contribute)
    and [Scipy](https://scipy.github.io/devdocs/dev/index.html) contributing
    documentation. We highly encourage newcomers to read these documentations if ours
    do not answer their questions.

## Local set up

1. Fork ReLife repository

First, you need to [create an account](https://github.com/join) on GitHub
(if you do not already have one) and fork the project repository by clicking on the
'Fork' button near the top of the page. This creates a copy of the code under your
GitHub account. For more details on how to fork a repository see
[this guide](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).
It explains how to set up a local clone of your forked git repository.

2. Set up a local clone of your fork

Clone your fork of the ReLife repo from your GitHub account to your
local disk. The url to use with the clone command can be found by clicking on the green
'Code' button of the GitHub repo. When you clone a project, you get a local copy of an
existing git repository that is uploaded on a server. The command below will create a
relife directory on your computer with the codebase and every version of every file for
the history of the project:

```console
$ git clone https://github.com/YourLogin/relife.git  # add --depth 1 if your connection is slow
$ cd relife # go into the directory
```

Next, add the `upstream` remote. This saves a reference to the main ReLife
repository, which you can use to keep your repository synchronized with the latest
changes (you'll need this later in the [development workflow](#development-workflow)):

```console
$ git remote add upstream https://github.com/rte-france/relife.git
```

Check that the `upstream` and `origin` remote aliases are configured correctly
by running:

```console
$ git remote -v
```

This should display:

```text
origin    https://github.com/YourLogin/relife.git (fetch)
origin    https://github.com/YourLogin/relife.git (push)
upstream  https://github.com/rte-france/relife.git (fetch)
upstream  https://github.com/rte-france/relife.git (push)
```

3. ReLife local installation

Make sure Python `3.11+` is installed on your machine. Using this Python, create
a [Python virtual environment](https://docs.python.org/3/library/venv.html) with
the name of your choice. **Activate your virtual environment**. Install ReLife in
[editable mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html)
from the source code with the **dev** dependencies group, which covers both code and
documentation contributions.

```console
$ (YourEnv) python -m pip install -e . --group dev
```

For **uv** users, it is possible to install ReLife in developer mode with the following command.
Note that uv uses [editable installation](https://docs.astral.sh/uv/concepts/projects/dependencies/#editable-dependencies)
for workspace packages by default.

```console
$ (YourEnv) uv sync --group dev
```

4. Configure your IDE

If you installed the **dev** dependencies group, the commands above should have installed [ruff](https://docs.astral.sh/ruff/).
Ruff is a powerful all-in-one tool for code linting and formatting.

- The [Ruff formatter](https://docs.astral.sh/ruff/formatter/) is an extremely fast Python code formatter designed as a drop-in replacement for Black.
  This tool allows you to automatically [format your code](https://en.wikipedia.org/wiki/Pretty-printing#Formatting_of_program_source_code).
  Ensure that your IDE is configured to call them to format on save so that you don't have
  to call them manually.
- The [Ruff Linter](https://docs.astral.sh/ruff/linter/) is an extremely fast Python [linter](https://en.wikipedia.org/wiki/Lint_(software)) designed as a drop-in replacement of well-known linters like flake8. Ensure that your IDE captures diagnostics from this tool while you are coding.

## Static type checking

Additionally, [static type checkers](https://en.wikipedia.org/wiki/Type_system#Type_checking)
have been installed:

- [basedpyright](https://github.com/detachhead/basedpyright).
  Again, ensure that your IDE communicates with the basedpyright language server ([LSP](https://en.wikipedia.org/wiki/Language_Server_Protocol))
  to receive feedback on your type annotations. Type checking can be challenging and may
  not be desired at first, so consider flagging your modules with `#pyright: basic` to start.
  Once you feel comfortable, gradually enhance your type annotations by removing `#pyright: basic`
  and enabling strict mode in basedpyright configurations.
- After successfully passing all Pyright analyses, use [mypy](https://github.com/python/mypy)
  to validate or supplement the diagnostics provided by basedpyright.

## Development workflow

The next steps describe the process of modifying code and submitting a PR:

1. Synchronize your `main` branch with the `upstream/main` branch,
   more details on [GitHub Docs](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork):

```console
$ git checkout main
$ git pull upstream main
```

2. Create a feature branch to hold your development changes:

```console
$ git checkout -b my_feature
```

and start making changes. Always use a feature branch. It's good
practice to never work on the `main` branch!

3. Develop the feature on your feature branch on your computer, using Git to
   do the version control. When you're done editing, add changed files using
   `git add` and then `git commit`:

```console
$ git add modified_files
$ git commit
```

You will be prompted to enter a commit message. Please, as much as possible,
start your message with the dedicated [commit message markers](#commit-message-markers). Your message must
look like this

```text
<commit_marker>: commit title

commit description
```

Then push the changes to your GitHub account with:

```console
$ git push -u origin my_feature
```

4. Before opening a pull request, please verify that your work meets our [pull request checklist](#pull-request-checklist).

5. Follow [these](https://help.github.com/articles/creating-a-pull-request-from-a-fork)
   instructions to create a pull request from your fork. This will send a
   notification to potential reviewers.

It is often helpful to keep your local feature branch synchronized with the
latest changes of the main ReLife repository. To do that, regularly check the evolution
of ReLife codebase, pull main changes and merge them in your feature branch.

```console
$ git pull upstream main
$ git checkout my_feature
$ git merge main
```

Subsequently, you might need to solve the conflicts. You can refer to the
[Git documentation related to resolving merge conflict using the command line](https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/)
or the [Git documentation itself (Basic Merge Conflicts)](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)

!!! note

    One very helpful tool to manage git commands is [Lazygit](https://github.com/jesseduffield/lazygit).
    It comes with a very user-friendly TUI and preconfigured set of useful commands to manage
    commits and branches.

## Commit message markers

Please follow and use these standard acronyms to start your commit messages:

```text
BUG: bug fix
DEP: deprecate something, or remove a deprecated object
DEV: development tool or utility
DOC: documentation
ENH: enhancement
MAINT: maintenance commit (refactoring, typos, etc.)
REV: revert an earlier commit
STY: style fix (PEP8, reformat, etc.)
TYP: typing
TEST: addition or modification of tests
REL: related to releasing ReLife
CI: related to CI
```

## Pull request checklist

Before a pull request can be merged, it needs to be approved by 1 core developer.
An incomplete contribution -- where you expect to do more work before receiving
a full review -- should be marked as a [draft pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request)
and changed to "ready for review" when it matures.

In order to ease the reviewing process, we recommend that your contribution
complies with the following rules before marking a PR as "ready for review". The
**bolded** ones are especially important:

1. **Give your pull request a helpful title** that summarizes what your
   contribution does. This title will often become the commit message once
   merged so it should summarize your contribution for posterity. In some
   cases "Fix &lt;ISSUE TITLE&gt;" is enough. "Fix #&lt;ISSUE NUMBER&gt;" is never a
   good title.

2. **Do not include unnecessary/unjustified commits** that don't have direct relations
   with the issue. Do not include unnecessary line rewritings or modifications of code style
   unless it is clearly motivated. Also, remove personal comments in your code.

3. **Make sure to address the whole issue**. Don't propose code that resolves the issue partly.
   In case you have any doubt, discuss it directly in the corresponding issue post.

4. **Make sure your code passes the tests**. The whole test suite can be run
   with `pytest`, but it is usually not recommended since it takes a long
   time. It is often enough to only run the tests related to your changes:
   for example, if you changed something in `relife/lifetime_model/_conditional_model.py`,
   running the following commands will usually be enough:

    - `pytest relife/lifetime_model/tests/test_conditional_model.py` to run the tests specific to the file
    - `pytest relife/lifetime_model` to test the whole `relife.lifetime_model` module

5. **Make sure your code is properly commented and documented**, and **make
   sure the documentation renders properly**. To build the documentation locally, please
   refer to [Build the documentation](#build-the-documentation).

6. Typing your code is not necessary at first, but make sure it is logical. The typing can be handled by
   the core team of ReLife. It is still a work in progress.

## About conception

If you want to address a conception problem, you're welcome.
**But these issues must be carefully motivated and well justified**. More precisely, we
won't accept any modifications that would be too subjective,
e.g. *only because you think it is more readable*.

!!! warning

    We are aware that overall ReLife code base *design* can be improved. Especially, we
    are currently having a special care on typing and are *stubifying* the code base.
    This work is done in addition to feature enhancements and progress at its own pace.
    It will be tested against mypy and it complements development principles that we study.
    At the end, we expect this static type checking will get the overall code base
    quality in the right direction.

## Build the documentation

The documentation is built with [Zensical](https://zensical.org). To build it locally, run the
following command from the repository root:

```console
$ zensical build -f docs/zensical.toml
```

To run a local documentation server with live reload while you edit:

```console
$ zensical serve -f docs/zensical.toml -o
```

For **uv** users, prefix the command with `uv run` so it runs inside the project
environment:

```console
$ uv run zensical serve -f docs/zensical.toml -o
```

The built site lands in `docs/site`, which is git-ignored. Delete it if the output looks
stale after moving or renaming pages.

The documentation uses the NumPy documentation style and renders API pages directly from
docstrings via [mkdocstrings](https://mkdocstrings.github.io/). The pages under
`docs/source/api/` list the public objects with the `::: relife.<module>.<object>` syntax,
so adding a new public object to the reference is one line in the relevant page. Here are
important points to have in mind if you want to **contribute to the documentation**:

* Read the [NumPy documentation style guide](https://numpydoc.readthedocs.io/en/latest/format.html)
* Take a special care to attributes class documentation. One must reference them manually in the object class under the `Attributes` field of the docstring. As it is mentioned in the [NumPy documentation style guide](https://numpydoc.readthedocs.io/en/latest/format.html), property methods (getter and/or setter) can be listed there. Their attached docstring will be loaded automatically. One more thing, some IDE (like PyCharm) may raise warnings about unreferenced variables. It is a bug... ignore or disable it at the statement level.
* Methods decorated with `document_args` (see `src/relife/lifetime_models/_base.py`) compose part of their docstring at import time rather than in the source docstring literal. They render correctly because of the `docs/_ext/dynamic_docstrings.py` Griffe extension, which re-imports the live object and reads its `__doc__` after decoration. If you add a similarly dynamic docstring elsewhere in the codebase, it needs the same treatment to show up in the API reference.

## Versioned documentation

The published site is versioned with [mike](https://github.com/jimporter/mike). The `main`
branch is continuously deployed as the `latest` alias, which is also the default landing
version. Pushing a `v*` tag runs `docs/deploy_versions.py`, which deploys the retained
tagged versions and prunes the stale ones. `docs/select_versions.py` decides what is
retained: the latest patch of the last three minor-version families, skipping the tags that
predate the Zensical migration and therefore have no `docs/zensical.toml` to build from.

## Doctests

Code blocks in the user guide (`docs/source/getting_started.md` and
`docs/source/user_guides/`) are written as real doctests, not illustrative snippets: every
`>>>` block is executed and its output checked. Run them with:

```console
$ pytest --doctest-glob="*.md" docs/source/getting_started.md docs/source/user_guides
```

For **uv** users:

```console
$ uv run pytest --doctest-glob="*.md" docs/source/getting_started.md docs/source/user_guides
```

`--doctest-glob="*.md"` is what makes pytest collect the Markdown files; without it they are
ignored. Every `>>>` block of a collected file is run, including the ones that produce a
figure. `docs/conftest.py` forces the matplotlib `Agg` backend so no window
is opened during collection. Run the doctests **before every documentation pull request**:
a renamed argument or a changed default silently breaks them, and the Zensical build itself
does not check outputs.

When an example's output depends on an iterative solver that isn't bit-exact run to run
(e.g. `SemiParametricProportionalHazard`), round the printed value to a stable precision
rather than asserting on full-precision output.

## Plots

Zensical has no equivalent of Sphinx's matplotlib plot directive, so the figures of the user
guide are **pre-rendered PNG files committed under `docs/source/_static/plots/`**. Each one
is paired, in the page, with the doctest block that produced it: the block is still executed
and checked by the doctest run, and the image right below it is what the reader sees.

~~~markdown
```python
>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> from relife.datasets import load_power_transformer
>>> from relife.lifetime_models import Weibull
>>> dataset = load_power_transformer()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"])
>>> timeline = np.arange(0, 145)
>>> _ = weibull.plot("sf", timeline, label="Weibull")
>>> _ = plt.xlabel("Time")
>>> _ = plt.legend()
>>> plt.show()

```

![Fitted Weibull survival function](../../../_static/plots/my_page_plot_1.png)
~~~

Conventions used across the documentation:

* Each block repeats its own imports and data loading. A page must stay readable for someone
  landing in the middle of it, and a self-contained block also survives being reordered.
* Assign the return value of the plotting calls to `_` (`>>> _ = plt.xlabel("Time")`).
  Otherwise the repr of the matplotlib artist is printed and the doctest fails.
* End with `plt.show()`. The `Agg` backend emits a harmless `UserWarning` under pytest.
* Name the image after the page and its rank in it (`<page>_plot_<n>.png`), and always give
  it alternative text describing what the figure shows.
* When you change the plotting code, regenerate the PNG: run the block yourself and save the
  figure over the existing file (`fig.savefig(path, dpi=110, bbox_inches="tight")` is what
  the committed images were produced with). An image that no longer matches its code block
  is worse than no image.

Hand-drawn or externally produced figures (the observation scheme, the censoring bias
comparison) live in `docs/source/_static/figures/` instead, and have no code block.

## Typing

Most of ReLife methods are Numpy compatible. For typing, we use [optype](https://github.com/jorenham/optype). It offers more functionalities to type Numpy code and it is compatible with `scipy-stubs`, the official typing of Scipy.

By default, many methods use either:

* `ST`: stands for Scalar Type, alias of `float` and `int`.
* `NumpyST`: stands for Numpy Scalar Type, alias of `np.floating` and `np.uint`.
* `ArrayND[NumpyST]`: stands for `np.ndarray` of `NumpyST` values.

The return types are generally narrowed to either `np.float64` or `ArrayND[np.float64]`.

Additionally, when it makes sense, the shape of arrays are specified with e.g. `Array1D` or `Array[AtMost{}D, ...]`.

!!! note

    Technically, the output type values could be different with Numpy
    operations. For instance, it could be `np.floating | np.integer |
    np.bool` depending on the types of the inputs. In practice, we don't know
    how to type the code in a more generic way without being too heavy or
    clumsy. So, at runtime, we force the output to be always `np.float64`
    that is used most often. It aligns with the typing and simplifies
    definitions.

!!! note

    `freeze` methods don't accept `ArrayND[NumpyST]` as input like other
    methods. Inputs are narrowed to `Array[AtMost2D, NumpyST]` because frozen
    models are meant to be used in stochastic processes or policies where
    additional args can't have more than 2 dimensions. That's why `freeze`
    is not part of `ParametricLifetimeModel` interface by default but is
    specific to derived classes.

## Linting

In many places, docstrings can be longer than 80 characters. In this case, we add a `# noqa: E501` mark to deactivate `ruff` warning.
