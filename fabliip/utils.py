from fabric import api


def local_run_wrapper(*args, **kwargs):
    """
    Wrapper around fabric's `local` command with the capture parameter always
    enabled.
    """
    kwargs['capture'] = True

    return api.local(*args, **kwargs)
