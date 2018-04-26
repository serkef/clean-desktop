import os
import datetime
import argparse
from typing import List
from pathlib import Path


def archive_daily_workfolders(workfolder: Path, archive: Path, cutoff_limit: int) -> None:
    """Archives all directories in workfolder to workfolder_archive,
    as long as their modification date was prior to cutoff limit."""
    for dir in workfolder.iterdir():
        modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(dir))
        if (datetime.date.today() - modifDate.date()).days > cutoff_limit:
            dir.rename(archive / dir.name)
            print('Archived %s to %s' % (dir, archive))


def remove_empty_folders(workfolder: Path) -> None:
    """Deletes any empty folder in provided path. Ignores OSError."""
    for dir in workfolder.iterdir():
        try:
            dir.rmdir()
            print('Deleted empty dir: %s' % (dir))
        except OSError:
            pass


def create_directory(directory: Path) -> None:
    """Creates directory given its full path. Ignores FileExistsError."""
    try:
        directory.mkdir()
        print('Created dir: %s' % (directory))
    except FileExistsError:
        pass


def archive_desktop_items(desktop: Path, workfolder: Path, exceptions: List[Path]) -> None:
    """Archives any item from desktop to workfolder, unless in exceptions"""
    for item in (i for i in desktop.glob('*') if i.name not in exceptions):
        item.rename(workfolder / item.name)


def main():
    desc = '''Workfolder & Desktop Cleaner\nArchives your desktop files to the 
    last day Workfolder, creates a new Workfolder and archives old workfolders 
    that exceed the cutoff limit.'''

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        '-workfolder',
        help="Main Workfolder. One subdirectory will be created, in every run.",
        type=Path
    )
    parser.add_argument(
        '-archive',
        help="Archive directory name. Will be a subdirectory of Workfolder. "
             "Defaults to ARCHIVE.",
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
        help="Cutoff limit in days. Any directory with modification date prior "
             "to this will be moved to archive. "
             "Defaults to 30 days.",
        default=30,
        type=int
    )
    parser.add_argument(
        '-ds_fmt',
        help="Datestamp format for workfolder created directory. Defaults to: "
             "'%%Y-%%m-%%d'",
        default='%Y-%m-%d',
        type=str
    )
    parser.add_argument(
        '-exceptions',
        help="Except desktop files list. files seperated with comma",
        default='',
        type=str
    )
    args = parser.parse_args()

    cutoff_limit = args.cutoff
    ds_fmt = args.ds_fmt
    desktop = args.desktop
    desktop_exceptions = args.exceptions.split(',')
    workfolder = args.workfolder
    workfolder_archive = workfolder / args.archive
    workfolder_today = workfolder / datetime.date.today().strftime(ds_fmt)

    # Archive old folders
    archive_daily_workfolders(workfolder=workfolder, archive=workfolder_archive,
                              cutoff_limit=cutoff_limit)

    # Delete empty folders
    remove_empty_folders(workfolder=workfolder)

    # Create Dir for Today
    create_directory(directory=workfolder_today)

    # Clean Desktop
    archive_desktop_items(desktop=desktop, workfolder=workfolder_today,
                          exceptions=desktop_exceptions)


if __name__ == '__main__':
    main()
