from contextlib import nested

from fabric import api
from fabric.context_managers import quiet


def ls(path):
    """
    Return the list of the files in the given directory, omitting . and ...

    Arguments:
        path -- The path of the directory to get the files from
    """
    with nested(api.cd(path), quiet()):
        files = api.run('for i in *; do echo $i; done')
        files_list = files.replace('\r', '').split('\n')

    return files_list


def file_exists(path):
    """
    Checks if the given path exists on the host and returns True if that's the
    case, False otherwise.
    """
    with quiet():
        exists = api.run('test -e {path}'.format(path=path)).succeeded

    return exists
