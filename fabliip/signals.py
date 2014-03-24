"""
This module allows you to send/receive signals during your deployment process.

You can use it to create modules separated from your main fabfile and make them
respond to certain signals. For example consider the following example, in your
``fabfile.py``::

    # This will trigger a pre_deploy and post_deploy signal
    @signals.register
    def deploy():
        deploy_my_app()

In your separate module, use the ``on`` decorator to hook on this signal::

    # This goes in your separate module
    @signals.on('fabfile.pre_deploy')
    def my_hook():
        print("This is called at the beginning of the deploy task")

You can also emit signals independently::

    def deploy():
        signals.emit('pre_deploy_my_app')
        deploy_my_app()
        signals.emit('hurray_my_app_is_deployed')

The :py:func:`task` decorator wraps the default :py:func:`fabric.api.task`
decorator with the :py:func:`register` signal, allowing you to intercept
pre/post signals without the need of adding the :py:func:`register` decorator
or firing the signals yourself.
"""

from collections import defaultdict
from functools import wraps
import inspect
import logging

from fabric.api import task as fabric_task


logger = logging.getLogger(__name__)


_callbacks = defaultdict(list)


def emit(signal):
    """
    Make all the receivers of this signal aware that it's been sent.
    """
    logger.debug("Emit signal %s" % signal)

    for callback in _callbacks[signal]:
        logger.debug("Execute function %s from %s" % (callback.__name__, inspect.getfile(callback)))
        callback()


def register(function):
    """
    Decorator that will emit pre and post signals before and after the
    function is executed. The signals are named after the function so if your
    function is named ``seek_the_holy_grail()``, the signal
    ``pre_seek_the_holy_grail`` will be fired before your function gets
    executed and the ``post_seek_the_holy_grail`` signal will be fired after
    your function has been executed.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        emit("{module}.pre_{function}".format(
            module=function.__module__,
            function=function.__name__
        ))

        return_value = function(*args, **kwargs)

        emit("{module}.post_{function}".format(
            module=function.__module__,
            function=function.__name__
        ))

        return return_value

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
    Convenience decorator that wraps the default Fabric task decorator with the
    :py:func:`register` decorator.
    """
    return fabric_task(register(function))
