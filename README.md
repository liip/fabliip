Fabliip
=======

Fabliip is a set of functions aimed at helping developers deploy their
websites.

Installation
============

Add it as a submodule in the same directory as your `fabfile.py`:

```
git submodule add git@gitlab.liip.ch:sylvain.fankhauser/fabliip.git
```

Usage
=====

You should read the annotated source to get an idea on the different helpers
Fabliip provides, but here's a minimal example that will allow you to
easily enable/disable the maintenance mode on your site:

```python
from fabric.api import cd, env, run, task
from fabliip import drupal


@task
def prod():
    env.run = run
    env.cd = cd
    env.project_root = '/var/www/mysite'
    env.drupal_root = os.path.join(env.project_root, 'src')
    env.hosts = ['yourhost.com']


@task
def enable_maintenance_mode():
    drupal.set_maintenance_mode(True)
```

You should now be able to call `fab prod enable_maintenance_mode` to enable the
maintenance mode on your prod instance.

The `env.project_root` and `env.drupal_root` are important and must be set to
ensure that all commands work. The `project_root` should be the root of your
git/hg/svn/whatever project, and the `drupal_root` should be Drupal's top-level
(ie. where you can run drush commands).

Also it's very important to set the `env.run` and `env.cd` because they're used
everywhere in Fabliip for command execution. The reason why it uses `env.run`
instead of `run` is that it allows you to create a dev environment and set
`env.run` to `local` (actually you're better setting it to `local_run_wrapper`,
see the source for details) to be able to use fabric commands locally.
