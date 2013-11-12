from fabric.api import env, local
from fabric.context_managers import quiet


def local_run_wrapper(*args, **kwargs):
    """
    Wrapper around fabric's `local` command with the capture parameter always
    enabled.
    """
    kwargs['capture'] = True

    return local(*args, **kwargs)


def file_exists(path):
    """
    Checks if the given path exists on the host and returns True if that's the
    case, False otherwise.
    """
    with quiet():
        exists = env.run('test -e {path}'.format(path=path)).succeeded

    return exists
