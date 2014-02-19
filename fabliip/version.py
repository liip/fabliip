from distutils.version import LooseVersion
import glob
import os


def get_version_files(from_version, to_version, directory):
    """
    Get a list of the files named after a version number (eg. 0.1.py, 0.1.2.py,
    etc) from the given directory and return a sorted list of tuples (version,
    file) of files which version number match the from_version (non inclusive)
    and to_version (inclusive) limits.

    Arguments:
    from_version -- A string representing the low version number (eg. 1.0)
    to_version -- A string representing the high version number (eg. 1.2.6)
    directory -- The path to the directory that holds the version files
    """

    files = []

    from_version = LooseVersion(from_version)
    to_version = LooseVersion(to_version)

    for file in glob.glob(os.path.join(directory, '*.py')):
        version, _ = os.path.splitext(os.path.basename(file))
        v = LooseVersion(version)

        if from_version < v <= to_version:
            files.append((v, file))

    files = sorted(files, key=lambda version: version[0])

    return files
