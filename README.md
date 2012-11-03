noduplicate-archiving
=====================

Does simple yet efficient archiving of entire directory trees by storing
duplicate files only once.

Original author: Timothy P. Egbert
First written in a usable form: 2012-07-07.
Release 0.70 2012-11-03 (Sat)

Author's note:

This program, nodup_archiving.py, is an efficient and simple archiving 
solution for cases in which there may be file duplication in the 
directory structures to be archived. It was inspired by the 
backup/archiving solution backuppc, but without all the bells and 
whistles. You may back up any number (within reason) of directory trees 
in a single archive. This is a recommended way to use this app in cases 
where directory trees to be archived are similar and contain some or 
many of the same files.

This version now comes with unit testin, and the app itself still comes 
in only one file's worth of Python code.

As of the 0.70 release, archving and restoration appear to be working 
just fine. You can now create an archive and copy it onto other media, 
and it will still restore from the copy. Keep in mind, however, that 
this is still a pre-1.0 release.

Here is the usage note that is output by the app when the "-h" switch is used:

"""
USE: nodup_archiving OPTIONS ACTION

Version 0.7 (2012-11-03)

Synopsis: an efficient and simple backup/archiving solution for directory
trees in which there may be file duplication.  More than one directory
tree may be archived to a single repository, which may result in greater
efficiencies, in that duplicate files all point to the same archived file
within the repository by means of hard links.

NOTE: this program is not smart enough to do incremental archiving and
restores, so directory trees will either be archived in total or
restored in total.

OPTIONS:

    -b <RepositoryPath>
        Designate the path of the repository into which files to be
        archived will be copied and into which the directory structures
        of the original directory trees will be created to mimic the
        directory being archived.

    -d <DirThatIsToBeArchived>
        The path to a directory to be archived, or the path to where
        the designated directory structure to be restored is being
        restored.

    -r <DirNameInArchiveRepository>
        The name of the directory within the archive repository into which
        the directory tree being archived will be saved, or the name of
        the directory tree that is going to the restored.

    -S
        Ignore symbolic links, to both directories and files. The
        default is to preserve symbolic links.

ACTION:

    <ActionToBePerformed - required>. May be one of the following (not
    case sensitive):

    NONE: the default. No action taken.

    ARCHIVE: archive the directory designated with the -d option to
        the archive repository designated with the -b option, into
        the tree designated by the -r option. If the -r option is
        not given, the archive directory name will be the same as
        the directory being archived.

    RESTORE: restore the archived directory structure designated with
        the -r option from the archive repository designated by the -b
        option to the directory designated by the -d option.
"""

To do:

1. Add INFO action to query the archive for useful information.
3. Preserve file permissions.
4. Preserve file ownership.
5. Handle symbolic links better.
6. Implement missing features, such as "CULL".
7. Create better documentation.
8. Add a progress bar.
