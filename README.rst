.. image:: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/badges/master/pipeline.svg
   :target: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release
   :alt: Pipeline Status

.. image:: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/badges/master/coverage.svg
   :target: https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release
   :alt: Coverage

.. image:: https://img.shields.io/pypi/l/gitlab-auto-release.svg
   :target: https://pypi.org/project/gitlab-auto-release/
   :alt: PyPI Project License

.. image:: https://img.shields.io/pypi/v/gitlab-auto-release.svg
   :target: https://pypi.org/project/gitlab-auto-release/
   :alt: PyPI Project Version

GitLab Auto Release
===================

This is a simple Python cli script that allows you create releases in GitLab automatically. It is intended to be
used during your CI/CD. However you can chose to use it however you wish.

Usage
-----

First you need to create a personal access token,
`more information here <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>`_.
With the scope ``api``, so it can create the release for you. This access token is passed
to the script with the ``--private-token`` argument.

.. code-block:: bash

  pip install gitlab-auto-release
  gitlab_auto_release --help

  Usage: gitlab_auto_release [OPTIONS]

    Gitlab Auto Release Tool.

  Options:
    --private-token TEXT    Private GITLAB token, used to authenticate when
                            calling the Release API.  [required]
    --gitlab-url TEXT       The gitlab URL i.e. gitlab.com.
                            [required]
    --project-id INTEGER    The project ID on GitLab to create the Release for.
                            [required]
    --tag-name TEXT         The tag the release should be created from.
                            [required]
    --release-name TEXT     The name of the release.  [required]
    -c, --changelog TEXT    Path to file to changelog file, will append itself to the
                            description with tag matching changelog. Must be in
                            keepachangelog format.
    -d, --description TEXT  Path to file to use as the description for the Release.
    -a, --asset TEXT        An asset to include in the release, i.e.
                            name=link_to_asset.
    --artifacts TEXT        Will include artifacts from jobs specified in
                            current pipeline. Use job name.
    --help                  Show this message and exit.

.. code-block:: bash

  gitlab_auto_release --private-token $(private_otken) --project-id 8593636 \
    --gitlab-url https://gitlab.com/stegappasaurus/stegappasaurus-app \
    --tag-name v0.1.0 --release-name v0.1.0 --changelog CHANGELOG.md

GitLab CI
*********

Set a secret variable in your GitLab project with your private token. Name it ``GITLAB_PRIVATE_TOKEN`` (``CI/CD > Environment Variables``).
This is necessary to create the release on your behalf.
An example CI using this can be found
`here <https://gitlab.com/hmajid2301/stegappasaurus/blob/a22b7dc80f86b471d8a2eaa7b7eadb7b492c53c7/.gitlab-ci.yml>`_,
look for the ``post:create:gitlab:release:`` job.

Add the following to your ``.gitlab-ci.yml`` file:

.. code-block:: yaml

  stages:
    - post

  publish:release:
    image: registry.gitlab.com/gitlab-automation-toolkit/gitlab-auto-release
    stage: post
    before_script: []
    script:
      - gitlab_auto_release --changelog CHANGELOG.md --artifacts lint --artifacts report


Predefined Variables
^^^^^^^^^^^^^^^^^^^^

Please note some of the arguments can be filled in using environment variables defined during GitLab CI.
For more information `click here <https://docs.gitlab.com/ee/ci/variables/predefined_variables.html>_`.

* If ``--private-token`` is not set the script will look for the ENV variable ``GITLAB_PRIVATE_TOKEN``
* If ``--gitlab-url`` is not set it will look for for the ENV variable ``CI_PROJECT_URL``
* If ``--project-id`` is not set it will look for for the ENV variable ``CI_PROJECT_ID``
* If ``--tag-name`` is not set it will look for for the ENV variable ``CI_COMMIT_TAG``

Setup Development Environment
=============================

.. code-block:: bash

  git clone git@gitlab.com:gitlab-automation-toolkit/gitlab-auto-release.git
  cd gitlab-auto-release
  pip install tox
  make install-venv
  source .venv/bin/activate
  make install-dev

Changelog
=========

You can find the `changelog here <https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-release/blob/master/CHANGELOG.md>`_.
