import os
import re

import gitlab
import pytest

from gitlab_auto_release.cli import cli


@pytest.mark.parametrize(
    "tag_name, extra_args, expected_description, expected_changelog",
    [
        (
            "release/1.0.0",
            {"--release-name": "release/1.0.0", "-c": "tests/data/CHANGELOG.md", "-d": "This a test"},
            "This a test",
            "[1.0.0]",
        ),
        (
            "release/1.0.4",
            {
                "--release-name": "release/1.0.4",
                "-c": "tests/data/CHANGELOG.md",
                "-a": "link=https://i.imgur.com/0Xe8502.gifv",
            },
            "Release for release/1.0.4",
            "[1.0.4]",
        ),
    ],
)
def test_success(runner, tag_name, extra_args, expected_description, expected_changelog):
    os.environ["CI_PROJECT_ID"] = "17422070"
    project_id = "17422070"
    gitlab_url = "https://gitlab.com/"
    private_token = os.environ["GITLAB_PRIVATE_TOKEN"]

    args = [
        "--private-token",
        private_token,
        "--gitlab-url",
        gitlab_url,
        "--tag-name",
        tag_name,
        "--project-id",
        project_id,
    ]
    [args.extend([k, v]) for k, v in extra_args.items()]
    args = filter(None, args)

    try:
        gitlab_url = re.search("^https?://[^/]+", gitlab_url).group(0)
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        project = gl.projects.get(project_id)
        project.tags.create({"tag_name": tag_name, "ref": "master"})
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        release = project.releases.get(tag_name)
        check_release_created_correctly(release, tag_name, expected_description, expected_changelog, extra_args)
    finally:
        project.tags.delete(tag_name)


def check_release_created_correctly(release, tag_name, expected_description, expected_changelog, extra_args):
    assert release.attributes["name"] == tag_name

    if "-c" in extra_args:
        assert expected_changelog in release.attributes["description"]

    if "-d" in extra_args:
        assert release.attributes["description"].startswith(expected_description)

    if "-a" in extra_args:
        name, asset = extra_args["-a"].split("=")
        asset_on_gitlab = release.attributes["assets"]["links"][0]
        assert {"name": asset_on_gitlab["name"], "url": asset_on_gitlab["url"]} == {"name": name, "url": asset}
