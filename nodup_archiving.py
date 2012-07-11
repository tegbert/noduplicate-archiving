#!/usr/bin/env python
##
##    nodups_archiving.py - archiving that eliminates duplicate files
##    Copyright (C) 2012 Timothy P. Egbert.
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
## Original author: Timothy P. Egbert
## First written in a usable form: 2012-07-07.
#
import sys
import os
import getopt
import hashlib
import shutil

FILE_ARCHIVE_NAME = 'nodups_file_archive'
BUFSZ = 1024*1024
DIRPERMS = 0775

def chomp_right( s ):
    while os.sep == s[-1]:
        s = s[:-1]
    return s

def walk_dir( base_dirpath ):
    base_dirpath = chomp_right( base_dirpath )
    genpaths = os.walk( base_dirpath )
    ll_dirs = []
    ll_files = []
    for dirpath, dirs, files in genpaths:
        for d in dirs:
            dpath = os.path.join(dirpath, d)
            if os.path.islink( dpath ):
                flag_link = True
                lpath = os.readlink( dpath )
            else:
                lpath = ''
                flag_link = False
            ll_dirs.append( (flag_link, lpath, dpath) )
        for f in files:
            fpath = os.path.join(dirpath, f)
            if os.path.islink( fpath ):
                flag_link = True
                lpath = os.readlink( fpath )
            else:
                flag_link = False
                lpath = ''
            ll_files.append( (flag_link, lpath, fpath) )
    return base_dirpath, ll_dirs, ll_files

def get_file_md5( fnpath ):
    m = hashlib.md5()
    fin = open(fnpath,'rb')
    while True:
        buf = fin.read( BUFSZ )
        if 0 == len(buf):
            break
        else:
            m.update( buf )
    hash = m.hexdigest()
    return hash

def action_new( argd ):
    repopath = chomp_right( argd['repopath'] )
    archive_fpname = repopath + os.sep + FILE_ARCHIVE_NAME
    if os.path.exists( repopath ):
        if not os.path.exists( archive_fpname ):
            raise Exception("'%s' does not appear to be a valid backup repository." % repopath)
    else:
        os.mkdir( repopath, DIRPERMS )
        os.mkdir( archive_fpname, DIRPERMS)
        for ch1 in '0123456789abcdef':
            p1 = archive_fpname + os.sep + ch1
            os.mkdir( p1, DIRPERMS )
            for ch2 in '0123456789abcdef':
                p2 = p1 + os.sep + ch2
                os.mkdir( p2, DIRPERMS )

def _get_and_normalize_paths( argd ):
    if None == argd['repopath']:
        raise Exception('you must designate a backup repository path with the -b option.')
    if None == argd['tobackpath']:
        raise Exception('you must designate directory be to backed up with the -d option.')
    repopath = chomp_right( argd['repopath'] )
    tobackpath = chomp_right( argd['tobackpath'] )
    repotree = argd['repotree']
    if None == repotree:
        repotree = os.path.split(tobackpath)[1]
    else:
        repotree = chomp_right( repotree )
    repotree_fullpath = repopath + os.sep + repotree
    return repopath, tobackpath, repotree, repotree_fullpath

def action_backup( argd ):
    repopath, tobackpath, repotree, repotree_fullpath = _get_and_normalize_paths( argd )
    action_new( argd )
    if os.path.exists( repotree_fullpath ):
        raise Exception("repository tree directory '%s' already exists." % repotree)
    base_dirpath, ll_dirs, ll_files = walk_dir( tobackpath )
    ## create repository tree
    len_base_dirpath = len(base_dirpath) + 1
    for isLink, linkref, backup_dirpath in ll_dirs:
        repo_dirpath = repopath + os.sep + repotree + os.sep + backup_dirpath[len_base_dirpath:]
        if True == isLink:
            if False == argd['ignore_symlinks']:
                os.symlink(linkref, repo_dirpath)
        else:
            if not os.path.exists(repo_dirpath):
                os.makedirs(repo_dirpath, DIRPERMS)
            else:
                raise Exception("repository directory '%s' already exists." % repo_dirpath)
    ## copy files to tree and archive
    for isLink, linkref, tobackupfnpath in ll_files:
        repo_fnpath = repopath  + os.sep + repotree + os.sep + tobackupfnpath[len_base_dirpath:]
        repo_fpath, fname = os.path.split( repo_fnpath )
        if True == isLink:
            if False == argd['ignore_symlinks']:
                os.symlink(linkref, repo_fnpath)
        else:
            try:
                hash = get_file_md5( tobackupfnpath )
            except IOError, ioe:
                print "bad file encountered and skipped: '%s'" % tobackupfnpath
                continue
            archive_fnpath = repopath + os.sep + FILE_ARCHIVE_NAME
            archive_fnpath += os.sep + hash[0] + os.sep + hash[1] + os.sep + hash
            if not os.path.exists( archive_fnpath ):
                shutil.copy(tobackupfnpath, archive_fnpath)
            back_fnpath = repo_fpath + os.sep + hash + "_" + fname
            os.link(archive_fnpath, back_fnpath)

def action_restore( argd ):
    repopath, restorepath, repotree, repotree_fullpath = _get_and_normalize_paths( argd )
    if os.path.exists(restorepath):
        raise Exception("restore path '%s' already exists." % restorepath)
    if not os.path.exists(repopath):
        raise Exception("backup repository '%s' does not exist." % repopath)
    
    ## restore directory tree
    os.mkdir( restorepath, DIRPERMS )
    nodups_prefix = repopath + os.sep + FILE_ARCHIVE_NAME
    base_dirpath, ll_dirs, ll_files = walk_dir( repotree_fullpath )
    precut = len(repotree_fullpath) + 1
    for isLink, linkref, backup_dirpath in ll_dirs:
        restoree = restorepath + os.sep + backup_dirpath[precut:]
        os.makedirs(restoree, DIRPERMS)

    ## restore files
    prefix_repo = repopath + os.sep + repotree
    cut_fnpath = len(prefix_repo) + 1     
    for isLink, linkref, backup_fnpath in ll_files:
        intree_path, fname_with_hash = os.path.split( backup_fnpath[cut_fnpath:] )
        if True == isLink:
            pass ## do links later
        else:
            hash = fname_with_hash[:32]
            fname = fname_with_hash[33:]
            repofnpath = repopath + os.sep + FILE_ARCHIVE_NAME + os.sep + hash[0] + os.sep + hash[1] + os.sep + hash
            if '' == intree_path:
                itp = ''
            else:
                itp = intree_path + os.sep
            restorefnpath = restorepath + os.sep + itp + fname 
            shutil.copy(repofnpath, restorefnpath)

def run( argd ):
    action = argd['action']
    if 'NEW' == action:
        action_new( argd )
    elif 'BACKUP' == action:
        action_backup( argd )
    elif 'RESTORE' == action:
        action_restore( argd )
    elif 'CULL' == action:
        print "Action: 'CULL' is not implemented."
    else:
        print "'%s' is an unknown action." % action

def usage( argd ):
    msg = """
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
        it if it does not exist. Default is "%(repopath)s". If the directory
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
    print msg % argd
    sys.exit(0)

def main():
    ## parse the CL
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'b:d:r:SHh')
    except getopt.GetoptError, exc:
        print >>sys.stderr, exc
        print >>sys.stderr, usage
        sys.exit(-1)
    argd = {
        'action'              : None,
        'repopath'            : None,
        'tobackpath'          : None,
        'repotree'            : None,
        'ignore_symlinks'     : True,
        'hardlinkdups'        : False,
        'help'                : False,
        }
    for o, v in opts:
        if o == "-b":
            argd['repopath'] = v
        elif o == "-r":
            argd['repotree'] = v
        elif o == "-d":
            argd['tobackpath'] = v
        elif o == "-S":
            argd['ignore_symlinks'] = False
        elif o == "-S":
            argd['hardlinkdups'] = True
        elif o == '-h':
            argd['help'] = True
    ## do the work
    if True == argd['help']:
        usage(argd)
    if 1>len(args):
        print "====>>>>> You must indicate which action is to be performed"
        usage(argd)
    else:
        argd['action'] = args[0].upper()
    run( argd )

if __name__ == '__main__':
    try:
        main()
    except Exception, ex:
        print "Error:",ex
