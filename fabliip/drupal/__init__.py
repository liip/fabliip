"""
Functions for Drupal sites.

The `drupal_root` environment variable is used in some functions of this module
to run the commands in the correct directory. Make sure it is set to the root
directory of your Drupal project.

This module requires `drush` to be installed on the remote server.
"""
from contextlib import nested

from fabric import api

from fabliip.file import file_exists


def drush(command):
    """
    Runs a drush command on the server.

    Requires the `drupal_root` environment variable to be set.
    """
    with api.cd(api.env.drupal_root):
        output = api.run('drush -y {command}'.format(command=command))

    return output


def enable_disable_modules(site=None):
    """
    Enables and disables modules on the Drupal install to reflect the status of
    the modules.enabled/disabled files.

    The optional `site` parameter allows you to have a multisite project
    with a global modules.enabled/disabled file and a site-specific
    modules.site.enabled/disabled file.
    """
    with nested(api.cd(api.env.project_root), api.hide('commands')):
        enabled_modules = set(api.run('cat modules.enabled').splitlines())
        disabled_modules = set(api.run('cat modules.disabled').splitlines())

        if site is not None:
            site_enabled_modules_file = 'modules.%s.enabled' % site
            site_disabled_modules_file = 'modules.%s.disabled' % site

            if (not file_exists(site_enabled_modules_file)
                    or not file_exists(site_disabled_modules_file)):
                raise Exception("Couldn't find the site-specific modules files"
                                " (modules.{site}.enabled and"
                                " modules.{site}.disabled)".format(site=site))

            site_enabled_modules = set(
                api.run('cat modules.%s.enabled' % site).splitlines()
            )
            site_disabled_modules = set(
                api.run('cat modules.%s.disabled' % site).splitlines()
            )

            enabled_modules |= site_enabled_modules
            disabled_modules |= site_disabled_modules

        enabled_modules -= disabled_modules

        current_enabled_modules = set(
            drush('pm-list --status=enabled --pipe').splitlines()
        )

        current_disabled_modules = set(
            drush('pm-list --status="disabled,not installed" --pipe')
            .splitlines()
        )

    modules_to_enable = current_disabled_modules & enabled_modules
    if modules_to_enable:
        print("The following modules are being enabled: {modules}".format(
            modules=", ".join(modules_to_enable))
        )
    else:
        print("No modules to enable")

    for module in modules_to_enable:
        drush('pm-enable %s' % module)
        clear_cache()

    modules_to_disable = current_enabled_modules & disabled_modules
    if modules_to_disable:
        print("The following modules are being disabled: {modules}".format(
            modules=", ".join(modules_to_disable))
        )
    else:
        print("No modules to disable")

    for module in modules_to_disable:
        drush('pm-disable %s' % module)
        clear_cache()


def set_maintenance_mode(enabled):
    """
    Enables or disables the maintenance mode.
    """
    drush('vset maintenance_mode %s' % ('1' if enabled else '0'))


def clear_cache():
    """
    Clears the Drupal cache.
    """
    drush('cc all')
