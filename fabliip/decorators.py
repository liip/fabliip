from functools import wraps

from fabric import api


def multisite(func):
    """
    Mark a task as being multisite.

    Multisite tasks allow you to define a global configuration for multiple
    sites and specify the site to use when you run your command. All the
    dictionary keys of the given site will then be made available in the `env`
    variable. The structure is
    `env.sites[site_name][env_name][configuration_key] = configuration_value`,
    where `env_name` is the name of the decorated function. Also the decorated
    function must take a parameter `site`.

    Here's an example with sites A and B, both having prod and staging
    environments::

        env.sites = {
            'site_a': {
                'prod': {
                    'project_root': '/var/www/site_a/prod/'
                },
                'staging': {
                    'project_root': '/var/www/site_a/staging/'
                }
            },
            'site_b': {
                'prod': {
                    'project_root': '/var/www/site_b/prod/'
                },
                'staging': {
                    'project_root': '/var/www/site_b/staging/'
                }
            }
        }

        @task
        @multisite
        def prod(site):
            # You could also define hosts in the `env.sites` dictionary if
            # they're different from one site to another
            # If the site is set to `site_a`, the decorator will take the
            # contents from env.sites['site_a']['prod'] and make it available
            # in the `env` variable
            env.hosts = ['www.my_host.com']

        @task
        @multisite
        def staging(site):
            # You could also define hosts in the `env.sites` dictionary if
            # they're different from one site to another
            env.hosts = ['staging.my_host.com']
    """

    if 'sites' not in api.env:
        raise RuntimeError("To use the multisite decorator you need to set the"
                           " `env.sites` variable.")

    @wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            site = args[0]
        elif func.__defaults__:
            site = func.__defaults__[0]
        else:
            site = None

        selected_environment = func.__name__

        if site is not None:
            if site not in api.env.sites:
                raise Exception(
                    "Site {site} is not part of the possible sites ({sites})"
                    .format(site=site, sites=api.env.sites.keys())
                )

            if selected_environment not in api.env.sites[site]:
                raise Exception(
                    "Site {site} has no {env} environment"
                    .format(site=site, env=selected_environment)
                )

            for setting, value in api.env.sites[site][selected_environment].iteritems():
                api.env[setting] = value

            api.env.site = site

        return func(*args, **kwargs)
    return wrapper
