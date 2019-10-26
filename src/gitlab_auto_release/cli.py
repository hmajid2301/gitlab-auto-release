# -*- coding: utf-8 -*-
r"""This module is used to use the GitLab API to automatically create a release for a specific project at a specific tag. You can include artifacts
with your release. You can also include descriptions from your changelog.
The script will look for the latest.

Example:
    ::
        $ pip install -e .
        $ gitlab_auto_release --private-token xxxx --project-id 8593636 --project-url https://gitlab.com/stegappasaurus/stegappasaurus-app \
        --tag-name v0.1.0 --release-name v0.1.0 --changelog CHANGELOG.md


.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
import os
import re
import sys

import click
import gitlab


@click.command()
@click.option(
    "--private-token",
    envvar="GITLAB_PRIVATE_TOKEN",
    required=True,
    help="Private GITLAB token, used to authenticate when calling the Release API.",
)
@click.option("--gitlab-url", envvar="CI_PROJECT_URL", required=True, help="The GitLab URL i.e. gitlab.com.")
@click.option("--project-url", envvar="CI_PROJECT_URL", required=True, help="The project URL.")
@click.option(
    "--project-id",
    envvar="CI_PROJECT_ID",
    required=True,
    type=int,
    help="The project ID on GitLab to create the Release for.",
)
@click.option("--tag-name", envvar="CI_COMMIT_TAG", required=True, help="The tag the release should be created from.")
@click.option("--release-name", envvar="CI_COMMIT_TAG", required=True, help="The name of the release.")
@click.option(
    "--changelog",
    "-c",
    help="Path to file to changelog file, will overwrite description with tag matching changelog. Must be in keepachangelog format.",
)
@click.option("--description", "-d", type=str, help="Path to file to use as the description for the Release.")
@click.option("--asset", "-a", multiple=True, help="An asset to include in the release, i.e. name=link_to_asset.")
@click.option(
    "--artifacts", multiple=True, help="Will include artifacts from jobs specified in current pipeline. Use job name."
)
def cli(
    private_token, project_id, gitlab_url, project_url, tag_name, release_name, changelog, description, asset, artifacts
):
    """Gitlab Auto Release Tool."""
    if gitlab_url == os.environ["CI_PROJECT_URL"]:
        gitlab_url = re.search("^https?://[^/]+", gitlab_url).group(0)

    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    try:
        project = gl.projects.get(project_id)
    except gitlab.exceptions.GitlabGetError as e:
        print(f"Unable to get project {project_id}. Error: {e}.")
        sys.exit(1)

    exists = check_if_release_exists(project, tag_name)
    if exists:
        print(f"Release already exists for tag {tag_name}.")
        sys.exit(0)

    try:
        assets = add_assets(asset)
    except IndexError:
        print(f"Invalid input format asset {asset}. Format should be `name=link_to_asset.")
        sys.exit(1)

    try:
        artifacts = add_artifacts(project, project_url, artifacts)
        assets += artifacts
    except IndexError:
        print(f"One of the jobs specified is not found cannot link artifacts {artifacts}")
        sys.exit(1)

    if changelog:
        try:
            description += f"\n\n {get_changelog(changelog, tag_name)}"
        except (IndexError, AttributeError):
            print(f"Invalid tag name doesn't contain a valid semantic version {tag_name}.")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Unable to find changelog file at {changelog}. No description will be set.")
            sys.exit(1)
        except OSError:
            print(f"Unable to open changelog file at {changelog}. No description will be set.")
            sys.exit(1)

    description = description if description else f"Release for {tag_name}"
    project.releases.create(
        {"name": release_name, "tag_name": tag_name, "description": description, "assets": {"links": assets}}
    )
    print(f"Created a release for tag {tag_name}.")


def check_if_release_exists(project, tag_name):
    """Checks if the release already exsists for that project.

    Args:
        project (Gitlab.project): Gitlab project object, to make API requests.
        tag_name (str): The tag name i.e. release/0.1.0, must contain semantic versioning somewhere in the tag (0.1.0).

    Returns
        bool: True if the release already exists.

    """
    exists = False
    try:
        gitlab_release = project.releases.get(tag_name)
        if gitlab_release:
            exists = True
    except gitlab.exceptions.GitlabGetError:
        pass

    return exists


def add_assets(asset):
    """Gets the asset in the correct format for the API request to create the release and include these extra assets
    with the release.

    Args:
        asset (list): A list of tuples in the format name=link. These will be included in the release.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the realse.

    Raises
        IndexError: When format is incorrect

    """
    assets = []
    for item in asset:
        asset_hash = {"name": item.split("=")[0], "url": item.split("=")[1]}
        assets.append(asset_hash)

    return assets


def add_artifacts(project, project_url, artifacts):
    """Gets the artifacts from the job name specified. Gets the current pipeline id,
    then matches the jobs we are looking finds the job id.

    Args:
        project (Gitlab.project): Gitlab project object, to make API requests.
        project_url (str): The url of the gitlab project.
        artifacts (list): A list Of jobs from current pipeline to link artifacts from.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the release.

    Raises
        IndexError: When the job doesn't exist in the pipeline jobs list.

    """
    assets = []

    if artifacts:
        pipeline_id = os.environ["CI_PIPELINE_ID"]
        pipeline = project.pipelines.get(pipeline_id)
        jobs = pipeline.jobs.list()

        for artifact in artifacts:
            matched = [job for job in jobs if job.name == artifact][0]
            job_id = matched.id
            artifact_link = {
                "name": f"Artifact: {artifact}",
                "url": f"{project_url}/-/jobs/{job_id}/artifacts/download",
            }
            assets.append(artifact_link)

    return assets


def get_changelog(changelog, tag_name):
    """Gets details from the changelog to include in the description of the release.
    The changelog must adhere to the keepachangelog format.

    Args:
        changelog (str): Path to changelog file.
        tag_name (str): The tag name i.e. release/0.1.0, must contain semantic versioning somewhere in the tag (0.1.0).

    Returns
        str: The description to use for the release

    Raises:
        AttributeError: If the tag_name doesn't contain semantic versioning somewhere within the name.
        FileNotFoundError: If the file couldn't be found.
        OSError: If couldn't open file for some reason.

    """
    with open(changelog, "r") as change:
        content = change.read()
        semver = r"((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)"
        semver_tag = re.search(semver, tag_name).group(0)
        if semver_tag:
            semver_changelog = f"## [{semver_tag}]"
            description = "\n"

            position_start = content.find(semver_changelog)
            if position_start:
                position_end = content[position_start + 2 :].find("## [")
                position_end = (position_end + position_start + 2) if position_end != -1 else -1
                description = content[position_start:position_end]

    return description
