from getpass import getpass

from fabric import api


def dump(backup_path, database_name, user='root', host=None, password=None):
    """
    Backup MySQL database as a MySQL archive.
    If host is set to None, 127.0.0.1 will be used.
    If password is set to None, a prompt will ask a password.
    """
    if host is None:
        host = '127.0.0.1'

    if password is None:
        password = getpass('Enter database password for {user}: '
                           .format(user=user))

    api.run('mysqldump {database_name} -h{host} -u{user} -p{password} > {backup_path}'
            .format(
                database_name=database_name,
                host=host,
                user=user,
                password=password,
                backup_path=backup_path,
            ))
