noduplicate-archiving
=====================

Does simple yet efficient archiving of entire directory trees by storing
duplicate files only once.

Original author: Timothy P. Egbert
First written in a usable form: 2012-07-07.

Author's note:

This program, nodup_archiving.py, is an efficient and simple archiving
solution for cases in which there may be file duplication in the directory
structures to be archived. It was inspired by the backup/archiving solution
backuppc, but without all the bells and whistles. You may back up any
number (within reason) of directory trees in a single archive. This is a
recommended way to use this app in cases where directory trees to be
archived are similar and contain some or many of the same files.

And the app does all this in only one file's worth of Python code.

Several features are not yet implemented and the app is most likely bug ridden.
If you use it, you will probably lose data and have a very bad day. You have
been warned! On the other hand, I've successfully used it "as is" to archive
several hundred GB of files and Have successfully recreated at least one 147
GB tree structure from the archive.

Here is the usage note that is output by the app when the "-h" switch is used:

"""
USE: effback OPTIONS ACTION

Version 0.21 (2012-07-08)

Synopsis: an efficient and simple backup solution for directory trees
in which there may be file duplication.  More than one directory tree
may be backed up to a single repository, which may result in greater
efficiencies, in that duplicate files all point to the same backup file
within the repository.

NOTE: this program is not smart enough to do incremental backups and
restores, so directory trees will either be backed up in total or
restored in total.

OPTIONS:

    -b <BackupRepositoryPath>
        Designate the backup directory repository into which files to be
        backed up will be copied and into which the directory structures
        will be created that mimic the directory being backed up. Create
        it if it does not exist. Default is "None". If the directory
        already exists, verify that it has the correct tree structure.

    -d <DirThatIsBackedUp>
        The path to a directory to be backed up, or the path to where
        the designated restore directory is being restored.

    -r <DirNameInBackupRepository>
        The name of the directory within the backup repository to which
        the directory tree being backed up will be saved, or the name of
        the directory tree that is going to the restored.

    -S
        Ignore symbolic links, to both directories and files. The
        default is to preserve symbolic links.

    -H  
        ***** NOTE: this option is not yet implemented *****
        During a RESTORE of a backup up directory tree, duplicate files
        within the repository will be restored as hard links after the
        initial first copy is restored. This option is ignored in all
        actions other than RESTORE.

ACTION:

    <ActionToBePerformed - required>. May be one of the following (not
    case sensitive):

    NONE: the default. No action taken.

    NEW: create a new backup repository to the path given in the -b
        option, but do not back up anything. If the directory path
        already exists, verify that it has the proper structure,

    BACKUP: backup the directory provided with the -d option to the
        backup repository designated with the -b option, into the
        tree designated by the -r option. If the -r option is not
        given, name it the same as the directory being backed up.

    RESTORE: restore the directory in the -r option from the backup
        repository designated by the -b option to the directory
        designated by the -d option.
        
    CULL: **** NOTE: this action not yet implemented *****
        cull out a backed up directory tree within the repository
        as designated by the -r option and remove the backed up
        files that are not pointed to by other trees within the
        repository. If the -r option is not given, simply remove
        the unreferenced files.
"""

To do:

1. Add INFO action to query the archive for useful information.
2. Add DELETE action to remove an archived directory tree.
3. Preserve file permissions.
4. Preserve file ownership.
5. Handle symbolic links better.
6. Implement missing features, such as "CULL".
7. Create better documentation.
8. Add a progress bar.
