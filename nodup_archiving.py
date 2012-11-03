#!/usr/bin/env python
##
##    nodups_archiving.py - directory archiving that eliminates duplicate files
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

FILE_ARCHIVE_NAME = '_nodups_file_pool_'
BUFSZ = 10*1024*1024
DIRPERMS = 0775
FILEPERMS = 0664

def chomp_right( s ):
    while os.sep == s[-1]:
        s = s[:-1]
    return s

def get_file_md5( fnpath ):
    m = hashlib.md5()
    fin = open(fnpath,'rb')
    while True:
        buf = fin.read( BUFSZ )
        if 0 == len(buf):
            break
        else:
            m.update( buf )
    fin.close()
    hexhash = m.hexdigest()
    return hexhash

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

def get_and_normalize_paths( argd ):
    if None == argd['repopath']:
        raise Exception('you must designate an archive repository path with the -b option.')
    if None == argd['toarchpath']:
        raise Exception('you must designate directory be to archived, or where to restore or copy an archive, with the -d option.')
    repopath = chomp_right( argd['repopath'] )
    toarchpath = chomp_right( argd['toarchpath'] )
    repotree = argd['repotree']
    if None == repotree:
        repotree = os.path.split(toarchpath)[1]
    else:
        repotree = chomp_right( repotree )
    repotree_fullpath = repopath + os.sep + repotree
    return repopath, toarchpath, repotree, repotree_fullpath

class Actions:
    
    def __init__(self, argd=None):
        self.argd = argd

    def action_new( self ):
        repopath = chomp_right( self.argd['repopath'] )
        archive_fpname = repopath + os.sep + FILE_ARCHIVE_NAME
        if os.path.exists( repopath ):
            if not os.path.exists( archive_fpname ):
                raise Exception("'%s' does not appear to be a valid archive repository." % repopath)
        else:
            os.mkdir( repopath, DIRPERMS )
            os.mkdir( archive_fpname, DIRPERMS)
            for ch1 in '0123456789abcdef':
                p1 = archive_fpname + os.sep + ch1
                os.mkdir( p1, DIRPERMS )
                for ch2 in '0123456789abcdef':
                    p2 = p1 + os.sep + ch2
                    os.mkdir( p2, DIRPERMS )
    
    def action_archive( self ):
        self.action_new()
        repopath, toarchpath, repotree, repotree_fullpath = get_and_normalize_paths( self.argd )
        if os.path.exists( repotree_fullpath ):
            raise Exception("repository tree directory '%s' already exists." % repotree)
        base_dirpath, ll_dirs, ll_files = walk_dir( toarchpath )
        ## create repository tree
        len_base_dirpath = len(base_dirpath) + 1
        for isLink, linkref, archive_dirpath in ll_dirs:
            repo_dirpath = repopath + os.sep + repotree + os.sep + archive_dirpath[len_base_dirpath:]
            if True == isLink:
                if False == self.argd['ignore_symlinks']:
                    os.symlink(linkref, repo_dirpath)
            else:
                if not os.path.exists(repo_dirpath):
                    os.makedirs(repo_dirpath, DIRPERMS)
                else:
                    raise Exception("repository directory '%s' already exists." % repo_dirpath)
        ## copy files to tree and archive
        for isLink, linkref, toarchivefnpath in ll_files:
            repo_fnpath = repopath  + os.sep + repotree + os.sep + toarchivefnpath[len_base_dirpath:]
            repo_fpath, fname = os.path.split( repo_fnpath )
            if True == isLink:
                if False == self.argd['ignore_symlinks']:
                    os.symlink(linkref, repo_fnpath)
            else:
                try:
                    fhash = get_file_md5( toarchivefnpath )
                except IOError, ioe:
                    print "%s\nbad file encountered and skipped: '%s'" % (ioe.__repr__(),toarchivefnpath)
                    continue
                archive_fnpath = repopath + os.sep + FILE_ARCHIVE_NAME
                archive_fnpath += os.sep + fhash[0] + os.sep + fhash[1] + os.sep + fhash
                if not os.path.exists( archive_fnpath ):
                    shutil.copy(toarchivefnpath, archive_fnpath)
                archive_fnpath = repo_fpath + os.sep + fhash + "_" + fname
                ##os.link(archive_fnpath, archive_fnpath) ## creates hard link, but copying the archive re-duplicates the files.
                fout = open(archive_fnpath,'w') ## creates empty file with name pointing to md5sum of file in the pool 
                fout.close()
    
    def action_restore( self ):
        repopath, restorepath, repotree, repotree_fullpath = get_and_normalize_paths( self.argd )
        if os.path.exists(restorepath):
            raise Exception("restore path '%s' already exists." % restorepath)
        if not os.path.exists(repopath):
            raise Exception("archive repository '%s' does not exist." % repopath)
        
        ## restore directory tree
        os.mkdir( restorepath, DIRPERMS )
        nodups_prefix = repopath + os.sep + FILE_ARCHIVE_NAME
        base_dirpath, ll_dirs, ll_files = walk_dir( repotree_fullpath )
        precut = len(repotree_fullpath) + 1
        for isLink, linkref, archive_dirpath in ll_dirs:
            restoree = restorepath + os.sep + archive_dirpath[precut:]
            os.makedirs(restoree, DIRPERMS)
    
        ## restore files
        prefix_repo = repopath + os.sep + repotree
        cut_fnpath = len(prefix_repo) + 1
        for isLink, linkref, archive_fnpath in ll_files:
            intree_path, fname_with_hash = os.path.split( archive_fnpath[cut_fnpath:] )
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
    actions = Actions( argd )
    if 'ARCHIVE' == action:
        actions.action_archive()
    elif 'RESTORE' == action:
        actions.action_restore()
    elif 'COPY' == action:
        actions.action_copy()
    elif 'CULL' == action:
        print "Action: 'CULL' is not implemented."
    else:
        print "'%s' is an unknown action." % action

def usage( argd ):
    msg = """
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
        'toarchpath'          : None,
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
            argd['toarchpath'] = v
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
    main()
#    try:
#        main()
#    except Exception, ex:
#        print "Error:",ex
