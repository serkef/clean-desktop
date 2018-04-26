import os
from os.path import isdir
import datetime
import shutil
from contextlib import contextmanager
from glob import glob

# Setup path
cutoff_limit = 30
ts_format = '%Y-%m-%d'
desktop = os.path.realpath('')
desktop_exceptions = ['']
workfolder = os.path.realpath('')
workfolder_archive = os.path.join(workfolder, 'ARCHIVE')
workfolder_today = os.path.join(workfolder, str(datetime.date.today().strftime(ts_format)))


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def super_archive(sources, destination):
    """Moves all directories in sources to destination. Ignores OSError exceptions."""
    for source in sources:
        with ignored(OSError):
            shutil.move(source, destination)
            print('Archived %s to %s' % (source, destination))


def is_old_directory(path):
    """Returns True if path was last modified > 30 days ago. False otherwise."""
    if not isdir(path):
        return False
    else:
        with ignored(OSError):
            modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            return (datetime.date.today() - modifDate.date()).days > cutoff_limit


def archive_daily_workfolders(dirsFromPath, archivePath):
    """Archives all directories in dirsFromPath to workfolder_archive, as long as their modification date
    was prior to cutoff_limit global var"""
    dirs = [d for d in glob(os.path.join(dirsFromPath, '*')) if is_old_directory(path=d)]
    super_archive(sources=dirs, destination=archivePath)


def remove_empty_folders(fromPath):
    """Deletes any empty folder in provided path. Ignores OSError exceptions."""
    for dir in os.listdir(fromPath):
        with ignored(OSError):
            os.removedirs(os.path.join(fromPath, dir))
            print('Deleted empty dir: %s' % (dir))


def create_directory(directory):
    """Creates directory given its full path. Ignores OSError exceptions."""
    with ignored(OSError):
        os.makedirs(directory)
        print('Created dir: %s' % (directory))


def archive_desktop_items(fromPath, toPath, exceptions):
    """Archives any item from fromPath to toPath, unless in exceptions"""
    itemsToArchive = [i for i in glob(os.path.join(fromPath, '*')) if i not in exceptions]
    super_archive(sources=itemsToArchive, destination=toPath)


def main():
    # Archive old folders
    archive_daily_workfolders(dirsFromPath=workfolder, archivePath=workfolder_archive)

    # Delete empty folders
    remove_empty_folders(fromPath=workfolder)

    # Create Dir for Today
    create_directory(directory=workfolder_today)

    # Clean Desktop
    archive_desktop_items(fromPath=desktop, toPath=workfolder_today, exceptions=desktop_exceptions)


if __name__ == '__main__':
    main()
