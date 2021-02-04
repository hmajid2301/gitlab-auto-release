import os
from collections import namedtuple

import gitlab
import pytest

from gitlab_auto_release.cli import cli


@pytest.mark.parametrize(
    "args, exit_code",
    [
        ([], 2),
        (["--private-token", "ATOKEN1234", "--project-id", 213145, "--gitlab-url", "https://gitlab.com/", "-c"], 2),
        (
            [
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
            ],
            2,
        ),
        (["--project-id", 213145, "--gitlab-url", "https://gitlab.com/hmajid2301/gitlab-auto-release"], 2),
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
            ],
            1,
        ),
    ],
)
def test_fail_args(runner, args, exit_code):
    result = runner.invoke(cli, args)
    assert result.exit_code == exit_code


@pytest.mark.parametrize(
    "args, exception",
    [
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
            ],
            gitlab.exceptions.GitlabGetError,
        ),
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
            ],
            gitlab.exceptions.GitlabAuthenticationError,
        ),
    ],
)
def test_fail_invalid_project(mocker, runner, args, exception):
    mocker.patch("gitlab.v4.objects.ProjectManager.get", side_effect=exception)
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_assets(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "--asset",
        "abc=example.com",
        "--asset",
        "name",
    ]
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_assets_exception(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "--asset",
        "abc=example.com",
        "--asset",
        "name",
    ]
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.side_effect = gitlab.exceptions.GitlabGetError
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_add_artifacts_no_env_var(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "--artifacts",
        "job_name",
    ]
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mock.return_value.pipelines.get.side_effect = gitlab.exceptions.GitlabGetError
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_add_artifacts_get_error(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "--artifacts",
        "job_name",
    ]
    os.environ["CI_PIPELINE_ID"] = "79790"
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mock.return_value.pipelines.get.side_effect = gitlab.exceptions.GitlabGetError
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_add_artifacts_index_error(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "--artifacts",
        "job_name",
    ]
    os.environ["CI_PIPELINE_ID"] = "79790"
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mock.return_value.pipelines.get.return_value.jobs.list.return_value = []
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "args",
    [
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
                "-c",
                "data/not_a_file.md",
            ]
        ),
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/",
                "--release-name",
                "release/0.5.0",
                "-c",
                "tests/data/CHANGELOG.md",
            ]
        ),
    ],
)
def test_invalid_add_changelog_error(mocker, runner, args):
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_invalid_add_changelog_oserror(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/",
        "--release-name",
        "release/0.5.0",
        "-c",
        "tests/data/CHANGELOG.md",
    ]
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mocker.patch("builtins.open", side_effect=OSError)
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "args",
    [
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
                "-c",
                "tests/data/CHANGELOG.md",
            ]
        ),
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
                "-d",
                "A random description",
                "-a",
                "name=example.com/image.jpeg",
                "-c",
                "tests/data/CHANGELOG.md",
            ]
        ),
        (
            [
                "--private-token",
                "ATOKEN1234",
                "--project-id",
                213145,
                "--gitlab-url",
                "https://gitlab.com/hmajid2301/gitlab-auto-release",
                "--tag-name",
                "release/0.5.0",
                "--release-name",
                "release/0.5.0",
                "-d",
                "A random description",
                "-a",
                "name=example.com/image.jpeg",
                "-c",
                "tests/data/CHANGELOG.md",
                "--artifacts",
                "example_job",
            ]
        ),
    ],
)
def test_success(mocker, runner, args):
    os.environ["CI_PIPELINE_ID"] = "79790"
    Job = namedtuple("Job", "name id")
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mock.return_value.pipelines.get.return_value.jobs.list.return_value = [Job(name="example_job", id="1235")]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


def test_success_release_exists(mocker, runner):
    args = [
        "--private-token",
        "ATOKEN1234",
        "--project-id",
        213145,
        "--gitlab-url",
        "https://gitlab.com/hmajid2301/gitlab-auto-release",
        "--tag-name",
        "release/0.5.0",
        "--release-name",
        "release/0.5.0",
        "-c",
        "tests/data/CHANGELOG.md",
    ]
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = True
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


def test_envvars(mocker, runner):
    args = [
        "-d",
        "A random description",
        "-a",
        "name=example.com/image.jpeg",
        "-c",
        "tests/data/CHANGELOG.md",
        "--artifacts",
        "example_job",
    ]
    os.environ["GITLAB_PRIVATE_TOKEN"] = "NOTATOKEN"
    os.environ["CI_PROJECT_ID"] = "81236"
    os.environ["CI_SERVER_URL"] = "https://gitlab.com/"
    os.environ["CI_COMMIT_TAG"] = "release/0.5.0"
    os.environ["CI_PIPELINE_ID"] = "79790"

    Job = namedtuple("Job", "name id")
    mock = mocker.patch("gitlab.v4.objects.ProjectManager.get")
    mock.return_value.releases.get.return_value = None
    mock.return_value.pipelines.get.return_value.jobs.list.return_value = [Job(name="example_job", id="1235")]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
