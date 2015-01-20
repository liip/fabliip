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

`shared_files`
    Dictionary of shared files {target: link_name}

The following variable should be defined if you want to use the various methods
of this module without having to pass it around :

`release_name`
    Name of the release
"""

from contextlib import nested
import logging
import os

from fabric.api import cd, env, run
from fabric.context_managers import quiet

from . import signals
from .file import ls


FAILED_RELEASE_SUFFIX = '_failed'


logger = logging.getLogger(__name__)


def determine_release_name(release_name):
    """
    Try to get ``release_name`` from :py:attr:`fabric.api.env.release_name`.
    """
    if release_name is None:
        if hasattr(env, 'release_name'):
            release_name = env.release_name
        else:
            raise AttributeError

    return release_name


def get_release_path(release_name=None):
    """
    Return the absolute path to the directory of the given release.

    If ``release_name is`` not given, try to get it from :py:attr:`fabric.api.env.release_name`.

    Arguments:
        release_name -- The name of the release (usually a date like YmdHMS)
    """
    release_name = determine_release_name(release_name)
    return os.path.join(env.releases_root, release_name)


@signals.register
def create_release(tag, release_name=None):
    """
    Create the directory for a new release and extract the contents from the
    git repository at the given tag and put them in this directory.

    Arguments:
        release_name -- The name of the release (usually a date like YmdHMS)
        tag -- The tag to install in this release
    """
    release_path = get_release_path(release_name)

    run("mkdir %s" % release_path)
    tmpfile = run("mktemp")
    run("git archive --output={tmpfile} --remote={remote} {version}"
        " && tar xf {tmpfile} -C {release_path}".format(
            remote=env.repository_root,
            version=tag,
            release_path=release_path,
            tmpfile=tmpfile))
    run("rm -f {tmpfile}".format(tmpfile=tmpfile))


@signals.register
def link_shared_files(release_name=None):
    """
    Create or update links to shared files defined in the ``shared_files`` env
    variable.

    If ``release_name is`` not given, try to get it from :py:attr:`fabric.api.env.release_name`.

    Arguments:
        release_name -- The name of the release (usually a date like YmdHMS)
    """
    release_path = get_release_path(release_name)

    for target, link_path in env.shared_files.iteritems():
        target_abspath = os.path.join(env.shared_root, target)
        link_path = os.path.join(release_path, link_path)

        run("ln -s {target} {link_path}".format(
            target=target_abspath, link_path=link_path))


@signals.register
def activate_release(release_name=None):
    """
    Activate the given release by making the ``current`` symlink point to it.

    If ``release_name is`` not given, try to get it from :py:attr:`fabric.api.env.release_name`.

    Arguments:
        release_name -- The name of the release (usually a date like YmdHMS)
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
    result = True

    for release in releases[:-keep]:
        status = run("rm -rf %s" % get_release_path(release), warn_only=True)
        if status.return_code != 0:
            logger.debug("Failed with status code [%s]" % status.return_code)
            result = False
    return result


def invalidate_last_release():
    """
    Invalidate the last made release so that it won't be a target for a rollback.
    """
    releases = get_releases()
    last_release = releases[-1]
    run("mv {release} {release}{suffix}".format(
        release=get_release_path(last_release),
        suffix=FAILED_RELEASE_SUFFIX))


def get_releases():
    """
    Return the list of releases on the server, sorted by oldest to newest.
    """
    return filter(
        lambda f: not f.endswith(FAILED_RELEASE_SUFFIX),
        sorted(ls(os.path.join(env.releases_root)))
    )


def get_currently_installed_version():
    """
    Return the currently installed version (tag) by reading the contents of the
    VERSION file, or None if the VERSION file could not be read.
    """
    with nested(cd(env.project_root), quiet()):
        version = run("cat VERSION")

    return version if version.succeeded else None


@signals.register
def update_version_file(version):
    """
    Update the VERSION file with the given version.
    """
    with nested(cd(env.project_root), quiet()):
        run("echo %s > VERSION" % version)
