.. image:: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/badges/master/pipeline.svg
   :target: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release
   :alt: Pipeline Status

.. image:: https://img.shields.io/pypi/l/gitlab-auto-release.svg
   :target: https://pypi.org/project/gitlab-auto-release/
   :alt: PyPI Project License

.. image:: https://img.shields.io/pypi/v/gitlab-auto-release.svg
   :target: https://pypi.org/project/gitlab-auto-release/
   :alt: PyPI Project Version

.. image:: https://readthedocs.org/projects/gitlab-auto-release/badge/?version=latest
   :target: https://gitlab-auto-release.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

GitLab Auto Release
===================
An example CI using this can be found `here <https://gitlab.com/stegappasaurus/stegappasaurus-app/blob/master/.gitlab-ci.yml>`_. This package was intended to be used by GitLab CI hence using environments provided by the GitLab CI. You can however use it as a CLI tool if you would like.

Usage
-----

First you need to create a personal access token,
`more information here <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>`_.
With the scope ``api``, so it can create the release for you.

.. code-block:: bash

  pip install gitlab-auto-release
  gitlab_auto_release --help

  Usage: gitlab_auto_release [OPTIONS]

    Gitlab Auto Release Tool.

  Options:
    --private-token TEXT    Private GITLAB token, used to authenticate when
                            calling the Release API.  [required]
    --project-url TEXT      The project URL on GitLab to create the Release for.
                            [required]
    --project-id INTEGER    The project ID on GitLab to create the Release for.
                            [required]
    --tag-name TEXT         The tag the release should be created from.
                            [required]
    --release-name TEXT     The name of the release.  [required]
    -c, --changelog TEXT    Path to file to changelog file, will overwrite
                            description with tag matching changelog. Must be in
                            keepachangelog format.
    -d, --description TEXT  Path to file to use as the description for the Release.
    -a, --asset TEXT        An asset to include in the release, i.e.
                            name=link_to_asset.
    --artifacts TEXT        Will include artifacts from jobs specified in
                            current pipeline. Use job name.
    --help                  Show this message and exit.

.. code-block:: bash

  gitlab_auto_release --private-token xxxx --project-id 8593636 \
    --project-url https://gitlab.com/stegappasaurus/stegappasaurus-app \
    --tag-name v0.1.0 --release-name v0.1.0 --changelog CHANGELOG.md

GitLab CI
*********

Set a secret variable in your GitLab project with your private token. Name it ``GITLAB_PRIVATE_TOKEN`` (``CI/CD > Environment Variables``).
This is necessary to create the release on your behalf.
More information `click here <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>`_. An example CI using this can be `found here <https://gitlab.com/stegappasaurus/stegappasaurus-app/blob/master/.gitlab-ci.yml>`_.

Add the following to your ``.gitlab-ci.yml`` file:

.. code-block:: yaml

  stages:
    - post

  publish:release:
    image: registry.gitlab.com/gitlab-automation-toolkit/gitlab-auto-release
    stage: post
    only:
      - /^release/.*$/
    before_script: []
    script:
      - gitlab_auto_release --changelog CHANGELOG.md --artifacts lint --artifacts report

Changelog
=========

You can find the `changelog here <https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/blob/master/CHANGELOG.md>`_.
