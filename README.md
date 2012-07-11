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

To do:

1. Add INFO action to query the archive for useful information.
2. Add DELETE action to remove an archived directory tree.
3. Preserve file permissions.
4. Preserve file ownership.
5. Handle symbolic links better.
6. Implement missing features, such as "CULL".
7. Create better documentation.
8. Add a progress bar.
