from fabric.api import env


def ls(path):
    """
    Return the list of the files in the given directory, omitting . and ...

    Arguments:
        path -- The path of the directory to get the files from
    """
    with env.cd(path):
        files = env.run('for i in *; do echo $i; done')
        files_list = files.replace('\r', '').split('\n')

    return files_list
