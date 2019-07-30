# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##[Unreleased]
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