# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.0.2] - 2020-04-08
### Fixed
- Typo in `README.rst`, `project-url` -> `gitlab-url`, #1.

## [4.0.1] - 2020-03-05
### Fixed
- `gitlab_release` referenced before it was assigned.

## [4.0.0] - 2020-03-01
### Added
- unit tests with 100% code coverage.
- `dev-requirements.txt` for development requirements such as black.
- `isort` to sort imports.
- `coverage` to detect code coverage from unit tests.
- `coverage` job in `.gitlab-ci.yml`.

### Changed
- Give docker image multiple tag in a single build comamnd.
- Updated README.rst with a setup dev environment section.
- `makefile` to `Makefile`.
- `MANIFEST.in` with recommended changes from `check-manifest`.
- `README.rst` added a coverage badge.
- `code-formatter` name in `tox.ini` to.
- `docker` publish job to pre-publish only on release tags.
- Refactored main `cli` function into smaller functions.

### Fixed
- Default `description` = `""` else the script crashes, #3.

### Removed
- `--project-url` argument, we can re use the `gitlab-url`.

## [3.0.0] - 2019-10-26
### Changed
- Updated README.rst, to include more useful information, about predefined variables.

### Fixed
- Tool only worked on GitLabs urls that were subdomains, now will work on any just specify gitlab-url, fixes #2.

### Removed
- Repeated sections from README.rst.

## [2.0.5] - 2019-10-21
### Changed
- All references to MR (merge request) changed to release.

## [2.0.4] - 2019-08-27
### Fixed
- Appending to list incorrectly, creating two lists `[[]]`.

## [2.0.3] - 2019-08-27
### Fixed
- Error typo `artifacts` should've been `artifact` in for loop.

## [2.0.2] - 2019-08-27
### Changed
- The function name from `get_asset_links` to `add_assets`.

### Fixed
- `add_assets` only expecting one argument.

## [2.0.1] - 2019-08-27
### Fixed
- Docstrings that were out of date with the code.

## [2.0.0] - 2019-08-26
### Changed
- To use artifacts not have to specify a job name.
- Use pipeline API to get all jobs and their ids.

### Fixed
- Linking artifacts still linking to a 404 page.

## [1.1.0] - 2019-08-26
### Fixed
- Linking assets incorrectly was trying to use GitLab API, now just using same link as in pipeline.

## [1.0.4] - 2019-08-24
### Fixed
- Same changelog error, should be check if find returns -1 instead of 0.

## [1.0.3] - 2019-08-24
### Fixed
- Changelog part was still broken, need to look for "## [" instead of "##".
- Mistake in README related to issue #1, calling it link-assets instead of link-artifacts.

## [1.0.2] - 2019-08-24
### Fixed
- When changelog including all of the changelog not just the part we want.

## [1.0.1] - 2019-07-30
### Changed
- README to include new short args i.e. -d instead of description.

## [1.0.0] - 2019-07-30
### Changed
- Removed unnecessary env variables from cli, some args should be provided as cli inputs. Such as description, changelog and link-artifacts.

## [0.2.1] - 2019-07-29
### Changed
- Changed any reference to hmajid2301/gitlab-auto-release to gitlab-automation-toolkit/gitlab-auto-release.

## [0.2.0] - 2019-07-28
### Added
- Two new lines after description when adding changelog.

### Changed
- Only one tox target for code formatters, makefile passes different parameters.

### Fixed
- Error when trying to append to description if it's not set (`TypeError`).

### Removed
- `code-formatter-check` from tox (target). Use `{posargs}` to pass `--check` if we want to check code is compliant with black.

## [0.1.0] - 2019-07-24
### Added
- Initial release.
- Create releases from within CI
- Use a changelog to fill in the description of the release. 

[Unreleased]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F4.0.2...master
[4.0.2]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F4.0.2...release%2F4.0.1
[4.0.1]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F4.0.1...release%2F4.0.0
[4.0.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F3.0.0...release%2F4.0.0
[3.0.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.5...release%2F3.0.0
[2.0.5]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.4...release%2F2.0.5
[2.0.4]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.3...release%2F2.0.4
[2.0.3]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.2...release%2F2.0.3
[2.0.2]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.1...release%2F2.0.2
[2.0.1]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F2.0.0...release%2F2.0.1
[2.0.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.1.0...release%2F2.0.0
[1.1.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.0.4...release%2F1.1.0
[1.0.4]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.0.3...release%2F1.0.4
[1.0.3]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.0.2...release%2F1.0.3
[1.0.2]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.0.1...release%2F1.0.2
[1.0.1]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F1.0.0...release%2F1.0.1
[1.0.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F0.2.1...release%2F1.0.0
[0.2.1]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F0.2.0...release%2F0.2.1
[0.2.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/compare/release%2F0.1.0...release%2F0.2.0
[0.1.0]: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/-/tags/release%2F0.1.0
