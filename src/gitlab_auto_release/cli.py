__VERSION__ = "4.0.4"

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
import requests


@click.command()
@click.option(
    "--private-token",
    envvar="GITLAB_PRIVATE_TOKEN",
    required=True,
    help="Private GITLAB token, used to authenticate when calling the Release API.",
)
@click.option("--gitlab-url", envvar="CI_SERVER_URL", required=True, help="The GitLab URL i.e. gitlab.com.")
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
    help="Path to file to changelog file, will append itself to the description with tag matching changelog. Must be in keepachangelog format.",
)
@click.option("--description", "-d", default="", type=str, help="String to use as the description for the release.")
@click.option("--asset", "-a", multiple=True, help="An asset to include in the release, i.e. name=link_to_asset.")
@click.option(
    "--artifacts", multiple=True, help="Will include artifacts from jobs specified in current pipeline. Use job name."
)
def cli(private_token, gitlab_url, project_id, tag_name, release_name, changelog, description, asset, artifacts):
    """Gitlab Auto Release Tool."""
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    project = get_gitlab_project(gl, project_id, gitlab_url)

    check_if_release_exists(project, tag_name)
    assets = add_assets(asset)

    if artifacts:
        project_artifacts = try_to_add_artifacts(project, artifacts, gitlab_url)
        assets += project_artifacts

    if changelog:
        changelog_data = try_to_get_changelog(changelog, tag_name)
        description += changelog_data

    description = description if description else f"Release for {tag_name}"
    project.releases.create(
        {"name": release_name, "tag_name": tag_name, "description": description, "assets": {"links": assets}}
    )
    print(f"Created a release for tag {tag_name}.")


def get_gitlab_project(gl, project_id, gitlab_url):
    """Gets the gitlab project object.

    Args:
        project (Gitlab): The Gitlab object.
        project_id (int): The id of the project to create the release for.
        gitlab_url (str): The FQDN of the project.

    Returns
        Gitlab.project: The Gitlab project object.

    """
    try:
        project = gl.projects.get(project_id)
    except gitlab.exceptions.GitlabAuthenticationError:
        print(f"Unable to get project {project_id}. Unauthorised access, check your access token is valid.")
        sys.exit(1)
    except gitlab.exceptions.GitlabGetError:
        print(f"Unable to get project {project_id}.")
        sys.exit(1)
    except requests.exceptions.MissingSchema:
        print(f"Incorrect --gitlab-url, missing schema i.e. https:// {gitlab_url}.")
        sys.exit(1)

    return project


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

    if exists:
        print(f"Release already exists for tag {tag_name}.")
        sys.exit(0)

    return exists


def add_assets(asset):
    """Gets the asset in the correct format for the API request to create the release and include these extra assets
    with the release.

    Args:
        asset (list): A list of tuples in the format name=link. These will be included in the release.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the release.

    """
    assets = []
    for item in asset:
        try:
            name, url = item.split("=")
        except ValueError:
            print(f"Invalid input format asset {asset}. Format should be `name=link_to_asset.")
            sys.exit(1)

        asset_hash = {"name": name, "url": url}
        assets.append(asset_hash)

    return assets


def try_to_add_artifacts(project, artifacts, gitlab_url):
    """Try to get the artifacts from the job name specified.

    Args:
        project (Gitlab.project): Gitlab project object, to make API requests.
        artifacts (list): A list Of jobs from current pipeline to link artifacts from.
        gitlab_url (str): The url of the gitlab project.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the release.

    """
    try:
        artifacts = add_artifacts(project, artifacts, gitlab_url)
    except gitlab.exceptions.GitlabGetError:
        print(f"Invalid pipeline id {os.environ['CI_PIPELINE_ID']}.")
        sys.exit(1)
    except IndexError:
        print(f"One of the jobs specified is not found cannot link artifacts {artifacts}.")
        sys.exit(1)
    except KeyError:
        print("Missing `CI_PIPELINE_ID` ENV variable.")
        sys.exit(1)

    return artifacts


def add_artifacts(project, artifacts, project_url):
    """Gets the artifacts from the job name specified. Gets the current pipeline id,
    then matches the jobs we are looking finds the job id.

    Args:
        project (Gitlab.project): Gitlab project object, to make API requests.
        artifacts (list): A list Of jobs from current pipeline to link artifacts from.
        project_url (str): The url of the gitlab project.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the release.

    Raises
        IndexError: When the job doesn't exist in the pipeline jobs list.
        KeyError: When `CI_PIPELINE_ID` ENV variable is not set.

    """
    assets = []

    pipeline_id = os.environ["CI_PIPELINE_ID"]
    pipeline = project.pipelines.get(pipeline_id)
    jobs = pipeline.jobs.list()

    for artifact in artifacts:
        matched = [job for job in jobs if job.name == artifact][0]
        job_id = matched.id
        artifact_link = {"name": f"Artifact: {artifact}", "url": f"{project_url}/-/jobs/{job_id}/artifacts/download"}
        assets.append(artifact_link)

    return assets


def try_to_get_changelog(changelog, tag_name):
    """Try to get details from the changelog to include in the description of the release.

    Args:
        changelog (str): Path to changelog file.
        tag_name (str): The tag name i.e. release/0.1.0, must contain semantic versioning somewhere in the tag (0.1.0).

    Returns
        str: The description to use for the release.

    """
    try:
        description = f"\n\n {get_changelog(changelog, tag_name)}"
    except (IndexError, AttributeError):
        print(f"Invalid tag name doesn't contain a valid semantic version {tag_name}.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Unable to find changelog file at {changelog}.")
        sys.exit(1)
    except OSError:
        print(f"Unable to open changelog file at {changelog}.")
        sys.exit(1)

    return description


def get_changelog(changelog, tag_name):
    """Gets details from the changelog to include in the description of the release.
    The changelog must adhere to the keepachangelog format.

    Args:
        changelog (str): Path to changelog file.
        tag_name (str): The tag name i.e. release/0.1.0, must contain semantic versioning somewhere in the tag (0.1.0).

    Returns
        str: The description to use for the release.

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
