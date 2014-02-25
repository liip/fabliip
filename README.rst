=======
Fabliip
=======

Fabliip is a set of functions aimed at helping developers deploy their
websites. It is meant to be used as part of Fabric scripts to ease for example
the backup of a database, the upgrade of a remote git repository, etc.

Installation
============

Install it with pip::

    pip install fabliip

Usage
=====

Docs are hosted on readthedocs: http://fabliip.rtfd.org/

You should be able to to get an idea on the different helpers Fabliip provides
by browsing the source code, but here's a minimal example that will allow you
to easily enable/disable the maintenance mode on a Drupal site::

    from fabric.api import env, task
    from fabliip import drupal


    @task
    def prod():
        env.project_root = '/var/www/mysite'
        env.drupal_root = os.path.join(env.project_root, 'src')
        env.hosts = ['yourhost.com']


    @task
    def enable_maintenance_mode():
        drupal.set_maintenance_mode(True)

You should now be able to call ``fab prod enable_maintenance_mode`` to enable
the maintenance mode on your prod instance.

The ``env.project_root`` variable is important here because it's needed by the
``drupal`` module. Please refer to the docs of any module you use to check if
there's any env variable that must be defined.
