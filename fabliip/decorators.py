from functools import wraps

from fabric import api


def multisite(func):
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
