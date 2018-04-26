import os
from os.path import isdir
import datetime
import shutil
from contextlib import contextmanager
from glob import glob

# Setup path
wfPath = os.path.realpath('')
archivePath = os.path.join(wfPath, 'ARCHIVE')
dayLimit = 30
folderFormat = '%Y-%m-%d'
desktopPath = os.path.realpath('')
desktopExceptions = ['']
todayPath = os.path.join(wfPath, str(datetime.date.today().strftime(folderFormat)))


@contextmanager
def ignored(*exceptions):
   try:
      yield
   except exceptions:
      pass


def superArchive(sources, destination):
   """Moves all directories in sources to destination. Ignores OSError exceptions."""
   for source in sources:
      with ignored(OSError):
         shutil.move(source, destination)
         print 'Archived %s to %s' % (source, destination)


def isOldDirectory(path):
   """Returns True if path was last modified > 30 days ago. False otherwise."""
   if not isdir(path):
      return False
   else:
      with ignored(OSError):
         modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(path))
         return (datetime.date.today() - modifDate.date()).days > dayLimit


def archiveDailyWorkfolders(dirsFromPath, archivePath):
   """Archives all directories in dirsFromPath to archivePath, as long as their modification date
   was prior to dayLimit global var"""
   dirs = [d for d in glob(os.path.join(dirsFromPath, '*')) if isOldDirectory(path=d)]
   superArchive(sources=dirs, destination=archivePath)


def removeEmptyFolders(fromPath):
   """Deletes any empty folder in provided path. Ignores OSError exceptions."""
   for dir in os.listdir(fromPath):
      with ignored(OSError):
         os.removedirs(os.path.join(fromPath, dir))
         print 'Deleted empty dir: %s' % (dir)


def createDirectory(directory):
   """Creates directory given its full path. Ignores OSError exceptions."""
   with ignored(OSError):
      os.makedirs(directory)
      print 'Created dir: %s' % (directory)


def archiveDesktopItems(fromPath, toPath, exceptions):
   """Archives any item from fromPath to toPath, unless in exceptions"""
   itemsToArchive = [i for i in glob(os.path.join(fromPath, '*')) if i not in exceptions]
   superArchive(sources=itemsToArchive, destination=toPath)


if __name__ == '__main__':

   # Archive old folders
   archiveDailyWorkfolders(dirsFromPath=wfPath, archivePath=archivePath)

   # Delete empty folders
   removeEmptyFolders(fromPath=wfPath)

   # Create Dir for Today
   createDirectory(directory=todayPath)

   # Clean Desktop
   archiveDesktopItems(fromPath=desktopPath, toPath=todayPath, exceptions=desktopExceptions)
