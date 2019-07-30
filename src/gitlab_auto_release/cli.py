# -*- coding: utf-8 -*-
r"""This module is used to use the GitLab API to automatically create a release for a specific project at a specific tag. You can include artifacts
with your release. You can also include descriptions from your changelog.
The script will look for the latest.

Example:
    ::
        $ pip install -e .
        $ gitlab_auto_release --private-token xxxx --project-id 8593636 --project-url https://gitlab.com/stegappasaurus/stegappasaurus-app \
        --tag-name v0.1.0 --release-name v0.1.0 --link-artifacts false --changelog CHANGELOG.md


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
    help="Private GITLAB token, used to authenticate when calling the MR API.",
)
@click.option(
    "--project-url", envvar="CI_PROJECT_URL", required=True, help="The project URL on GitLab to create the MR for."
)
@click.option(
    "--project-id",
    envvar="CI_PROJECT_ID",
    required=True,
    type=int,
    help="The project ID on GitLab to create the MR for.",
)
@click.option("--tag-name", envvar="CI_COMMIT_TAG", required=True, help="The tag the release should be created from.")
@click.option("--release-name", envvar="CI_COMMIT_TAG", required=True, help="The name of the release.")
@click.option(
    "--changelog",
    "-c",
    help="Path to file to changelog file, will overwrite description with tag matching changelog. Must be in keepachangelog format.",
)
@click.option("--description", "-d", type=str, help="Path to file to use as the description for the MR.")
@click.option("--asset", "-a", multiple=True, help="An asset to include in the release, i.e. name=link_to_asset.")
@click.option("--link-artifacts", is_flag=True, help="If set to true will link artifacts from current job.")
def cli(private_token, project_id, project_url, tag_name, release_name, changelog, description, asset, link_artifacts):
    """Gitlab Auto Release Tool."""
    gitlab_url = re.search("^https?://[^/]+", project_url).group(0)
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
        assets = get_asset_links(gitlab_url, project_id, asset, link_artifacts)
    except IndexError:
        print(f"Invalid input format asset {asset}. Format should be `name=link_to_asset.")
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


def get_asset_links(gitlab_url, project_id, asset, link_artifacts):
    """Gets the asset in the correct format for the API request to create the release and include these extra assets
    with the release.

    Args:
        gitlab_url (str): The base url to gitlab i.e. https://gitlab.com.
        project_id (int): The project id on that gilab instance, where we will create release.
        asset (tuple): A list of tuples in the format name=link. These will be included in the release.
        link_artifacts (bool): If set to true we will link all artifacts in the current CI job with the release.

    Returns
        list: (of dicts), which includes a name and url for the asset we will include in the realse.

    """
    assets = []
    for item in asset:
        asset_hash = {"name": item.split("=")[0], "url": item.split("=")[1]}
        assets.push(asset_hash)

    if link_artifacts:
        job_id = os.environ["CI_JOB_ID"]
        artifact = {"name": "artifact", "url": f"{gitlab_url}/api/v4/projects/{project_id}/jobs/{job_id}/artifacts"}
        assets.append(artifact)

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
                position_end = content[position_start:].find("##")
                position_end = position_end if position_end else -1
                description = content[position_start:position_end]

    return description
