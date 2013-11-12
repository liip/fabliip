from contextlib import nested

from fabric.api import env, hide, local


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


def get_latest_tag(commit=None):
    """
    Returns the latest reachable tag from the given commit, or HEAD if not
    specified.
    """
    with nested(env.cd(env.project_root), hide('commands')):
        tag = local('git describe --tag --abbrev=0 {commit}'.format(
            commit=commit if commit is not None else ''
        ), capture=True)

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
