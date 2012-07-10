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
number (within reason) of directory trees in a single archive. And it does
all this in only one file's worth of Python code.

This is version 0.21, 2012-07-08. Several features are not yet implemented
in and it is most likely bug ridden. If you use it, you will probably lose
data and have a very bad day. You have been warned! On the other hand, I've
successfully used it "as is" to archive several hundreds of GB of files and
Have successfully recreated at least one 147 GB tree structure from the archive.

To do:

1. Preserve file permissions.
2. Preserve file ownership.
3. Handle symbolic links better.
4. Implement missing features, such as "CULL".
5. Create better documentation.
6. Add a progress bar.
