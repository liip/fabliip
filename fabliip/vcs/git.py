from contextlib import nested

from fabric import api
from fabric.context_managers import quiet


def push_tag(tag, remote='origin'):
    """
    Pushes the given tag to the given remote.
    """
    api.local('git push {remote} {tag}'.format(
        remote=remote,
        tag=tag)
    )


def update_remote_repository_root(tag):
    """
    Fetches the latest git objects on the remote, checks out the given tag and
    updates the submodules if necessary.

    Requires the `repository_root` environment variable to be set.
    """
    with nested(api.cd(api.env.repository_root), api.hide('commands')):
        api.run('git fetch -t -p')
        api.run('git checkout {tag}'.format(tag=tag))
        api.run('git submodule sync')
        api.run('git submodule update --init')


def get_latest_tag(commit='HEAD', run_locally=True):
    """
    Return the latest reachable tag from the given commit.

    Arguments:
    commit -- The name of the commit to use (tag, hash, etc) (default HEAD)
    run_locally -- Whether to get the latest local or remote tag (default True)

    """
    git_command = 'git describe --tag --abbrev=0 {commit}'.format(
        commit=commit if commit is not None else ''
    )

    with nested(api.hide('commands'), quiet()):
        if run_locally:
            tag = api.local(git_command, capture=True)
        else:
            with api.cd(api.env.repository_root):
                tag = api.run(git_command)

    # For strange reasons the above call to run returns git's stderr in
    # case of failure (eg. if there are no tags yet) even with combine_stderr
    # set to False. This is a temporary hack to avoid returning git's error
    # message as the tag name
    if tag.return_code != 0:
        tag = ''

    return tag


def get_latest_commit(run_locally=True):
    """
    Return the commit identified by the current HEAD.

    Arguments:
        run_locally -- Whether to get the latest local or remote HEAD (default
        True)

    """
    git_command = 'git rev-parse HEAD'

    with nested(api.hide('commands'), quiet()):
        if run_locally:
            commit = api.local(git_command, capture=True)
        else:
            with api.cd(api.env.repository_root):
                commit = api.run(git_command)

    return commit


def get_commit_messages(first_commit, last_commit):
    """
    Returns all commit messages between first_commit and last_commit in an
    abbreviated form.
    """
    with api.hide('commands'):
        changes = api.local(
            'git log --reverse --oneline {first_commit}..{last_commit}'
            .format(
                first_commit=first_commit,
                last_commit=last_commit
            ), capture=True
        )

    return changes
