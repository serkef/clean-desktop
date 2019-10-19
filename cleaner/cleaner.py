import argparse
from contextlib import suppress
import datetime as dt
import logging
import os
from pathlib import Path
import shutil


def safe_directory_name(string: str):
    """Checks if a string can be used as a directory name"""
    safe_characters = {".", ",", "+", "-", "_", " "}
    for char in string:
        if not char.isalnum() and char not in safe_characters:
            return False
    return True


def main():
    desc = """Workfolder & Desktop Cleaner\nArchives your desktop files to the
    last day Workfolder, creates a new Workfolder and archives old workfolders
    that exceed the cutoff limit."""

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-workfolder",
        help="Main Workfolder. One subdirectory will be created, in every run.",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "-archive",
        help="Archive directory name. Will be a subdirectory of Workfolder. "
        "Defaults to ARCHIVE.",
        default="ARCHIVE",
        type=str,
    )
    parser.add_argument(
        "-clean_folders",
        help="Directories that will be cleaned in each run. Contents will be moved to "
        "daily workfolder.",
        default=[],
        nargs="*",
        type=Path,
    )
    parser.add_argument(
        "-cutoff",
        help="Cutoff limit in days. Any directory with modification date prior "
        "to this will be moved to archive. "
        "Defaults to 30 days.",
        default=30,
        type=int,
    )
    parser.add_argument(
        "-ds_fmt",
        help="Date format for workfolder created directory. Defaults to: "
        "'%%Y-%%m-%%d'",
        default="%Y-%m-%d",
        type=str,
    )
    parser.add_argument(
        "-rel_link",
        help="Will create relative link for today in Workfolder path",
        default=True,
        type=bool,
    )
    args = parser.parse_args()

    cutoff_limit = args.cutoff
    ds_fmt = args.ds_fmt
    workfolder = args.workfolder.expanduser()
    workfolder_archive = args.archive
    if not safe_directory_name(workfolder_archive):
        raise ValueError(f"Archive folder cannot be named {workfolder_archive!r}")
    workfolder_archive = workfolder / args.archive
    workfolder_today = workfolder / dt.date.today().strftime(ds_fmt)
    link_workfolder_today = workfolder / "today"
    clean_folders = (folder.expanduser() for folder in args.clean_folders)

    # configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Archive old folders
    workfolder_archive.mkdir(exist_ok=True, parents=True)
    for folder in workfolder.iterdir():
        if folder.is_symlink():
            continue
        modified_at = dt.datetime.fromtimestamp(os.path.getmtime(folder))
        if (dt.date.today() - modified_at.date()).days > cutoff_limit:
            folder.rename(workfolder_archive / folder.name)
            logging.info("Archived %s to %s", folder, workfolder_archive)

    # Delete empty folders
    for folder in workfolder.iterdir():
        if folder == workfolder_today or folder == workfolder_archive:
            continue
        with suppress(OSError):
            folder.rmdir()
            logging.info("Deleted empty folder: %s", folder)

    # Create Dir for Today
    workfolder_today.mkdir(exist_ok=True)

    # Create home link
    if args.rel_link:
        with suppress(FileNotFoundError):
            os.unlink(link_workfolder_today)
        with suppress(OSError):
            os.symlink(workfolder_today, link_workfolder_today)
            logging.info("Created link: %s", link_workfolder_today)

    # Clean Workfolder
    for item in workfolder.glob("*"):
        if item == link_workfolder_today or item == workfolder_archive:
            continue
        # If parse date, then should not move.
        try:
            dt.datetime.strptime(item.name, ds_fmt)
        except ValueError:
            pass
        else:
            continue
        shutil.move(str(item), str(workfolder_today))

    # Clean every other folder
    for folder in clean_folders:
        for item in folder.glob("*"):
            shutil.move(str(item), str(workfolder_today))
        logging.info("Cleaned %r", folder)


if __name__ == "__main__":
    main()
