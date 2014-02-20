"""
This module allows you to send/receive signals during your deployment process.
"""

from collections import defaultdict
from functools import wraps

from fabric.api import task as fabric_task


_callbacks = defaultdict(list)


def emit(signal):
    """
    Make all the receivers of this signal aware that it's been sent.
    """
    for callback in _callbacks[signal]:
        callback()


def register(function):
    """
    Decorator that will emit pre_ and post_ signals before and after the
    function is executed.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        emit("pre_%s" % function.__name__)
        ret = function(*args, **kwargs)
        emit("post_%s" % function.__name__)

        return ret

    return wrapper


def on(signal):
    """
    Decorator that will call the given function when the given signal is
    emitted.
    """
    def wrapper(function):
        """
        Add the given callback to the list of receivers of the given signal.
        """
        _callbacks[signal].append(function)

    return wrapper


def task(function):
    """
    Convenience decorator that overrides the default Fabric task decorator and
    adds pre_ and post_ signals to it.
    """
    return register(fabric_task(function))
