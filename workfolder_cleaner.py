import os
import shutil
import logging
import datetime
import argparse
from pathlib import Path


def main():
    desc = '''Workfolder & Desktop Cleaner\nArchives your desktop files to the 
    last day Workfolder, creates a new Workfolder and archives old workfolders 
    that exceed the cutoff limit.'''

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-workfolder",
        help="Main Workfolder. One subdirectory will be created, in every run.",
        required=True,
        type=Path
    )
    parser.add_argument(
        "-archive",
        help="Archive directory name. Will be a subdirectory of Workfolder. "
             "Defaults to ARCHIVE.",
        default="ARCHIVE",
        type=str
    )
    parser.add_argument(
        "-desktop",
        help="Desktop directory. Files will be moved from there to Workfolder.",
        required=True,
        type=Path
    )
    parser.add_argument(
        "-cutoff",
        help="Cutoff limit in days. Any directory with modification date prior "
             "to this will be moved to archive. "
             "Defaults to 30 days.",
        default=30,
        type=int
    )
    parser.add_argument(
        "-ds_fmt",
        help="Date format for workfolder created directory. Defaults to: "
             "'%%Y-%%m-%%d'",
        default="%Y-%m-%d",
        type=str
    )
    parser.add_argument(
        "-exceptions",
        help="Except desktop files list. files separated with comma",
        default="",
        type=str
    )
    args = parser.parse_args()

    cutoff_limit = args.cutoff
    ds_fmt = args.ds_fmt
    desktop = args.desktop
    desktop_exceptions = args.exceptions.split(",")
    workfolder = args.workfolder
    workfolder_archive = workfolder / args.archive
    workfolder_today = workfolder / datetime.date.today().strftime(ds_fmt)

    # configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Archive old folders
    for folder in workfolder.iterdir():
        modified_at = datetime.datetime.fromtimestamp(os.path.getmtime(folder))
        if (datetime.date.today() - modified_at.date()).days > cutoff_limit:
            folder.rename(workfolder_archive / folder.name)
            logging.info("Archived %s to %s" % (folder, workfolder_archive))

    # Delete empty folders
    for folder in workfolder.iterdir():
        try:
            folder.rmdir()
        except OSError:
            pass
        else:
            logging.info("Deleted empty folder: {}".format(folder))

    # Create Dir for Today
    try:
        workfolder_today.mkdir()
    except FileExistsError:
        logging.info("Already exists: {}".format(workfolder_today))
    else:
        logging.info("Created folder: {}".format(workfolder_today))

    # Clean Desktop
    for item in (i for i in desktop.glob("*") if i.name not in desktop_exceptions):
        logging.info("Moving %r to %r", item.name, str(workfolder_today))
        try:
            shutil.move(str(item), str(workfolder_today))
        except (OSError, shutil.Error):
            logging.warning("Failed to move %s", item, exc_info=True)


if __name__ == "__main__":
    main()
