<!--
SPDX-FileCopyrightText: 'Copyright Contributors to the [name_open_source_project] project' 

SPDX-License-Identifier: Apache-2.0
-->

# How to contribute

We'd love to accept your patches and contributions to this project. There are just a few guidelines you need to follow.

## Filing bugs and feature requests

You can file bugs against and feature requests for the project via GitHub Issues. Read [GitHub Help](https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/creating-an-issue) for more information on using GitHub Issues.

## Community guidelines

This project follows the following [Code of Conduct](CODE_OF_CONDUCT.md).

## Development

### Setup

To set up the development environment, go through the following steps:

1. Install [uv](https://docs.astral.sh/uv/). This tool replaces pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and more. It also manages your python version, so you don't need tools like pyenv.
2. `uv sync`

### Development scripts

- To run all linters and formatters with automatic fixes applied
```sh
uv run task fix
```

- To run tests
```sh
uv run task test
```

- To dry run ci locally (no automatic fixes applied)
```sh
uv run task local-ci
```

### Testing

#### Prerequisites

- Allow usage of the Docker Socket
    - MacOS: advanced settings ??
    - Linux: check if you are part of the Docker user group `groups $USER | grep docker`, otherwise add yourself to it `sudo usermod -aG docker $USER`

### Running the tests

1. Have the Docker Deamon running
2. (`uv sync`)
3. `uv run task test`

## Pre-commit

This repository includes pre-commit hooks. To install the pre-commit hooks, run `uvx pre-commit`. There is a preference for running pre-commit hooks locally, so that all tooling (CI and pre-commit hooks) use the same environment and tool versions.

## REUSE compliance and source code headers

All the files in the repository need to be [REUSE compliant](https://reuse.software/).
We use the pipeline to automatically check this.
If there are files which are not complying, the pipeline will fail the pull request will be blocked.

This means that every file containing source code must include copyright and license information. This includes any JS/CSS files that you might be serving out to browsers. (This is to help well-intentioned people avoid accidental copying that doesn't comply with the license.)

To automatically apply the headers, run `uv run task reuse-fix` or `uv run task fix`

## Git branching

This project uses the [Trunk Based Development](https://trunkbaseddevelopment.com/) and branching model.
The `main` branch always contains the latest code. When a change is being made a branch should be created from the `main` branch.
Ideally, this branch is focused on making a specific change in the codebase or documentation and is therefore:

1. A short-lived branch
2. Easy to review due to small changes in each PR

When a feature is finished and approved it is merged back into `main`.

New releases are made using Githubs Release feature, by adding a git tag to a commit.

## Commit messages

Commit messages should follow https://www.conventionalcommits.org/en/v1.0.0/


## Signing the Developer Certificate of Origin (DCO)

This project uses a Developer Certificate of Origin (DCO) to ensure that each commit was written by the author or that the author has the appropriate rights necessary to contribute the change.
Specifically, we use [Developer Certificate of Origin, Version 1.1](http://developercertificate.org/), which is the same mechanism that the Linux® Kernel and many other communities use to manage code contributions.
The DCO is considered one of the simplest tools for sign-offs from contributors as the representations are meant to be easy to read and indicating signoff is done as a part of the commit message.

This means that each commit must include a DCO which looks like this:

`Signed-off-by: Joe Smith <joe.smith@email.com>`

The project requires that the name used is your real name and the e-mail used is your real e-mail.
Neither anonymous contributors nor those utilizing pseudonyms will be accepted.

There are other great tools out there to manage DCO signoffs for developers to make it much easier to do signoffs:

* Git makes it easy to add this line to your commit messages. Make sure the `user.name` and `user.email` are set in your git configs. Use `-s` or `--signoff` to add the Signed-off-by line to the end of the commit message.
* [GitHub UI automatic signoff capabilities](https://github.blog/changelog/2022-06-08-admins-can-require-sign-off-on-web-based-commits/) for adding the signoff automatically to commits made with the GitHub browser UI. This one can only be activated by the GitHub org or repo admin.
* [GitHub UI automatic signoff capabilities via custom plugin]( https://github.com/scottrigby/dco-gh-ui ) for adding the signoff automatically to commits made with the GitHub browser UI.
* Additionally, it is possible to use shell scripting to automatically apply the sign-off. For an example for bash to be put into a .bashrc file, see [here](https://wiki.lfenergy.org/display/HOME/Contribution+and+Compliance+Guidelines+for+LF+Energy+Foundation+hosted+projects).
* Alternatively, you can add `prepare-commit-msg hook` in .git/hooks directory. [See an example](https://github.com/Samsung/ONE-vscode/wiki/ONE-vscode-Developer's-Certificate-of-Origin).

In case of major version release with new features and/or breaking changes, we might temporarily create a `release/` branch to hold all the changes until they are merged into `main`.

## Code reviews

All patches and contributions, including patches and contributions by project members, require review by one of the maintainers of the project.
We use GitHub pull requests for this purpose.
See [GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information on using pull requests.

## Pull request process

Contributions should be submitted as GitHub pull requests. See [Creating a pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) if you're unfamiliar with this concept.

Follow this process for a code change and pull request:

1. Create a topic branch in your local repository, following the naming format "feature-[description]". For more information see the Git branching guideline.
1. Make changes, compile, and test thoroughly. Ensure any install or build dependencies are removed before the end of the layer when doing a build. Code style should match existing style and conventions, and changes should be focused on the topic the pull request will be addressed. For more information see the style guide.
1. Push commits to your branch.
1. Create a GitHub pull request from your topic branch.
1. Pull requests will be reviewed by one of the maintainers who may discuss, offer constructive feedback, request changes, or approve the work. For more information see the Code review guideline.
1. Upon receiving the sign-off from one of the maintainers you may merge your changes. If you do not have permission to do that, you may request a maintainer to merge it for you.

## Attribution

This CONTRIBUTING.md is adapted from Google, available at https://github.com/google/new-project/blob/master/docs/contributing.md.
