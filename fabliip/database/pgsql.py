from getpass import getpass

from fabric.api import env, shell_env, sudo


def dump(backup_path, database_name, user='postgres', host=None):
    """
    Backs up the given database to the given file as a PostgreSQL archive. If
    host is set to None, a local connection will be used, so you'll need to be
    able to sudo to the given user. Otherwise, a standard password connection
    will be used and the user will be asked for a password.
    """
    if host is None:
        sudo('pg_dump -Fc {database_name} > {backup_path}'
             .format(
                 database_name=database_name,
                 backup_path=backup_path,
             ), user=user)
    else:
        db_password = getpass('Enter database password for {user}: '
                              .format(user=user))

        with shell_env(PGPASSWORD=db_password):
            env.run('pg_dump -Fc -U {user} -h {host} {database} >'
                    ' {backup_path}'
                    .format(
                        user=user,
                        host=host,
                        database_name=database_name,
                        backup_path=backup_path,
                    ))
