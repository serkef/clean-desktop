import os
from os.path import isdir
import datetime
import shutil
from contextlib import contextmanager
from glob import glob
import argparse
from typing import List
from pathlib import Path


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def super_archive(sources: List[Path], destination: Path) -> None:
    """Moves all directories in sources to destination. Ignores OSError exceptions."""
    for source in sources:
        with ignored(OSError):
            shutil.move(str(source), str(destination))
            print('Archived %s to %s' % (source, destination))


def is_old_directory(path: Path, cutoff_limit: int) -> bool:
    """Returns True if path was last modified > 30 days ago. False otherwise."""
    if not isdir(path):
        return False
    else:
        with ignored(OSError):
            modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(str(path)))
            return (datetime.date.today() - modifDate.date()).days > cutoff_limit


def archive_daily_workfolders(dirsFromPath: Path, archivePath: Path, cutoff_limit: int) -> None:
    """Archives all directories in dirsFromPath to workfolder_archive, as long as their modification date
    was prior to cutoff_limit global var"""
    dirs = [Path(d) for d in glob(os.path.join(str(dirsFromPath), '*')) if
            is_old_directory(path=d, cutoff_limit=cutoff_limit)]
    super_archive(sources=dirs, destination=archivePath)


def remove_empty_folders(fromPath: Path) -> None:
    """Deletes any empty folder in provided path. Ignores OSError exceptions."""
    for dir in os.listdir(str(fromPath)):
        with ignored(OSError):
            os.removedirs(os.path.join(str(fromPath), dir))
            print('Deleted empty dir: %s' % (dir))


def create_directory(directory: Path) -> None:
    """Creates directory given its full path. Ignores OSError exceptions."""
    with ignored(OSError):
        os.makedirs(str(directory))
        print('Created dir: %s' % (directory))


def archive_desktop_items(fromPath: Path, toPath: Path, exceptions: List[Path]):
    """Archives any item from fromPath to toPath, unless in exceptions"""
    itemsToArchive = [Path(i) for i in glob(os.path.join(str(fromPath), '*')) if Path(i) not in exceptions]
    super_archive(sources=itemsToArchive, destination=toPath)


def main():
    desc = '''Workfolder & Desktop Cleaner
    Archives your desktop files to the last day Workfolder, creates a new Workfolder and archives old workfolders
    that exceed the cutoff limit.'''

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        '-workfolderf',
        help="Main Workfolder. One subdirectory will be created, every day this script is run.",
        type=Path
    )
    parser.add_argument(
        '-archive',
        help="Archive directory name. Will be a subdirectory of Workfolder. Defaults to ARCHIVE.",
        default='ARCHIVE',
        type=str
    )
    parser.add_argument(
        '-desktop',
        help="Desktop directory. Files will be moved from there to Workfolder.",
        type=Path
    )
    parser.add_argument(
        '-cutoff',
        help="Cutoff limit in days. Any directory with modification date prior to this will be moved to archive. "
             "Defaults to 30 days.",
        default=30,
        type=int
    )
    parser.add_argument(
        '-ds_fmt',
        help="Datestamp format for workfolder created directory. Defaults to: '%Y-%m-%d'",
        default='%Y-%m-%d',
        type=int
    )
    parser.add_argument(
        '-exceptions',
        help="Except desktop files list. files seperated with comma",
        type=str
    )
    args = parser.parse_args()

    workfolder = args.workfolderf
    workfolder_archive = workfolder / args.archive
    cutoff_limit = args.cutoff_limit
    ds_fmt = args.ds_fmt
    desktop = args.desktop
    desktop_exceptions = args.exceptions.split(',')
    workfolder_today = workfolder / str(datetime.date.today().strftime(ds_fmt))

    # Archive old folders
    archive_daily_workfolders(dirsFromPath=workfolder, archivePath=workfolder_archive, cutoff_limit=cutoff_limit)

    # Delete empty folders
    remove_empty_folders(fromPath=workfolder)

    # Create Dir for Today
    create_directory(directory=workfolder_today)

    # Clean Desktop
    archive_desktop_items(fromPath=desktop, toPath=workfolder_today, exceptions=desktop_exceptions)


if __name__ == '__main__':
    main()
