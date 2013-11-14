from contextlib import nested

from fabric.api import env, hide, local
from fabric.context_managers import quiet


def push_tag(tag, remote='origin'):
    """
    Pushes the given tag to the given remote.
    """
    local('git push {remote} {tag}'.format(
        remote=remote,
        tag=tag)
    )


def update_remote_project_root(tag):
    """
    Fetches the latest git objects on the remote, checks out the given tag and
    updates the submodules if necessary.
    """
    with nested(env.cd(env.project_root), hide('commands')):
        env.run('git fetch -t -p')
        env.run('git checkout {tag}'.format(tag=tag))
        env.run('git submodule sync')
        env.run('git submodule update')


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

    with nested(hide('commands'), quiet()):
        if run_locally:
                tag = local(git_command, capture=True)
        else:
            with env.cd(env.project_root):
                tag = env.run(git_command)

    # For strange reasons the above call to env.run returns git's stderr in
    # case of failure (eg. if there are no tags yet) even with combine_stderr
    # set to False. This is a temporary hack to avoid returning git's error
    # message as the tag name
    if tag.return_code != 0:
        tag = ''

    return tag


def get_commit_messages(first_commit, last_commit):
    """
    Returns all commit messages between first_commit and last_commit in an
    abbreviated form.
    """
    with hide('commands'):
        changes = local(
            'git log --reverse --oneline {first_commit}..{last_commit}'
            .format(
                first_commit=first_commit,
                last_commit=last_commit
            ), capture=True
        )

    return changes