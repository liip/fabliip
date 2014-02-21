from getpass import getpass

from fabric import api

DEFAULT_HOST = '127.0.0.1'


def dump(backup_path, database_name, user='root', host=None, password=None):
    """
    Backup MySQL database as a MySQL archive.
    If host is set to None, 127.0.0.1 will be used.
    If password is set to None, a prompt will ask a password.
    """
    if host is None:
        host = DEFAULT_HOST

    if password is None:
        password = get_password(user)

    api.run('mysqldump {database_name} -h{host} -u{user} -p{password} > {backup_path}'
            .format(
                database_name=database_name,
                host=host,
                user=user,
                password=password,
                backup_path=backup_path,
            ))


def restore(backup_path, database_name, user='root', host=None, password=None):
    """
    Restore MySQL database.
    If host is set to None, 127.0.0.1 will be used.
    If password is set to None, a prompt will ask a password.
    """
    if host is None:
        host = DEFAULT_HOST

    if password is None:
        password = get_password(user)

    api.run('mysql -h{host} -u{user} -p{password} {database_name} < {backup_path}'
            .format(
                database_name=database_name,
                host=host,
                user=user,
                password=password,
                backup_path=backup_path,
            ))


def get_password(user):
    """
    Ask a password in the prompt
    """
    return getpass('Enter database password for {user}: '
                   .format(user=user))
