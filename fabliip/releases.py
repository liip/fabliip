"""
This module provides a deployment structure similar to what Capistrano does. By
default, the project layout looks like that::

    current -> releases/20140830180015_1.2.3  -- Symlink to the current release
    releases/
        20140830151210_1.2.2/
        20140831180015_1.2.3/
    repository.git/                           -- Git repository containing the project
    shared/                                   -- Shared files not specific to a release
        config.yml
        media/
    VERSION                                   -- The version of the current release

When you create a new release, the code from the `repository.git` directory
is archived in a new directory named after the current date and the version
you're deploying. After that, the symlink `current` is switched to the new
release.

The following variables must be defined in Fabric's env for this module to
work:

`releases_root`
    Path to the releases/ directory

`repository_root`
    Path to the repository.git/ directory

`shared_root`
    Path to the shared/ directory
"""

from contextlib import nested
import logging
import os
import uuid

from fabric.api import cd, env, run
from fabric.context_managers import quiet

from . import signals
from .file import ls


logger = logging.getLogger(__name__)


def get_release_path(release_name):
    """
    Return the absolute path to the directory of the given release.
    """
    return os.path.join(env.releases_root, release_name)


@signals.register
def create_release(release_name, tag):
    """
    Create the directory for a new release and extract the contents from the
    git repository at the given tag and put them in this directory.

    Arguments:
        release_name -- The name of the release (usually a date like YmdHMS)
        tag -- The tag to install in this release
    """
    release_path = get_release_path(release_name)

    run("mkdir %s" % release_path)
    run("git archive --remote={remote} {version}"
        " | tar -x -C {release_path}".format(
            remote=env.repository_root,
            version=tag,
            release_path=release_path))


@signals.register
def link_shared_files(release_name):
    """
    Create or update links to shared files defined in the ``shared_files`` env
    variable.
    """
    release_path = get_release_path(release_name)

    with cd(env.shared_root):
        for target, link_name in env.shared_files.iteritems():
            tmp_link_name = str(uuid.uuid4())

            target_abspath = os.path.join(release_path, target)

            run("ln -s {target} {tmp_link_name}".format(
                target=target_abspath, tmp_link_name=tmp_link_name))
            run("mv -Tf {tmp_link_name} {link_name}".format(
                tmp_link_name=tmp_link_name, link_name=link_name))


@signals.register
def activate_release(release_name):
    """
    Activate the given release by making the ``current`` symlink point to it.
    """
    logger.debug("""

              ~ RELEASE THE KRAKEN!!! ~
                        ___
                     .-'   `'.
                    /         \\
                    |         ;
                    |         |           ___.--,
           _.._     |0) ~ (0) |    _.---'`__.-( (_.
    __.--'`_.. '.__.\\    '--. \\_.-' ,.--'`     `""`
   ( ,.--'`   ',__ /./;   ;, '.__.'`    __
   _`) )  .---.__.' / |   |\\   \\__..--""  \"\""--.,_
  `---' .'.''-._.-'`_./  /\\ '.  \\ _.-~~~````~~~-._`-.__.'
        | |  .' _.-' |  |  \\  \\  '.               `~---`
         \\ \\/ .'     \\  \\   '. '-._)
          \\/ /        \\  \\    `=.__`~-.
     jgs  / /\\         `) )    / / `"".`\\
    , _.-'.'\\ \\        / /    ( (     / /
     `--~`   ) )    .-'.'      '.'.  | (
            (/`    ( (`          ) )  '-;
             `      '-;         (-'
    """)

    with cd(env.project_root):
        run("ln -s {target} new_current".format(
            target=get_release_path(release_name)))
        run("mv -Tf new_current current")


@signals.register
def clean_old_releases(keep=5):
    """
    Remove the old release directories from the releases directory, keeping x
    releases defined by the ``keep`` parameter.

    Arguments:
        keep -- The number of releases to keep
    """
    releases = get_releases()

    for release in releases[:-keep]:
        run("rm -rf %s" % get_release_path(release))


def get_releases():
    """
    Return the list of releases on the server, sorted by oldest to newest.
    """
    return sorted(ls(os.path.join(env.releases_root)))


def get_currently_installed_version():
    """
    Return the currently installed version (tag) by reading the contents of the
    VERSION file.
    """
    with nested(cd(env.project_root), quiet()):
        version = run("cat VERSION")

    return version


@signals.register
def update_version_file(version):
    """
    Update the VERSION file with the given version.
    """
    with nested(cd(env.project_root), quiet()):
        run("echo %s > VERSION" % version)
