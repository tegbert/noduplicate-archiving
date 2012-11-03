'''
Created on Jul 14, 2012

@author: tpe
'''
import os
import shutil
import unittest
import nodup_archiving

class Test(unittest.TestCase):

    REPO_TEST_DIR = "DELETEME_test_repo"
    TEST_DATA_DIR = "test_data"
    REPO_TREE = "test_data_1"
    RESTORED_DATA_DIR = "DELETEME_restored_repo"

    def setUp(self):
        self._remove_test_repo()

    def tearDown(self):
        self._remove_test_repo()

    def _get_argd(self):
        argd = {
            'repopath'            : self.REPO_TEST_DIR,
            'toarchpath'          : self.TEST_DATA_DIR,
            'repotree'            : self.REPO_TREE,
            'ignore_symlinks'     : True,
            'hardlinkdups'        : False,
            'help'                : False,
            }
        return argd

    def _setup_test_repo(self):
        if os.path.exists(self.REPO_TEST_DIR):
            raise Exception("'%s' already exists. Delete it before running unit tests." % self.REPO_TEST_DIR)
        argd = self._get_argd()
        self.sut = nodup_archiving.Actions(argd)
        self.sut.action_new() ## create the new empty archive

    def _remove_test_repo(self):
        if os.path.exists(self.REPO_TEST_DIR):
            shutil.rmtree( self.REPO_TEST_DIR ) ## be careful with this one!!!

    def testActionRestore(self):
        ## setup
        self._setup_test_repo()
        self.sut.action_archive()
        save_path = self.sut.argd['toarchpath'] ## for subsequent tests
        self.sut.argd['toarchpath'] = self.RESTORED_DATA_DIR
        self.sut.action_restore()

        ## test whether restored directory is OK
        base_dirpath, ll_dirs, ll_files = nodup_archiving.walk_dir(self.RESTORED_DATA_DIR)
        actual = self.RESTORED_DATA_DIR
        self.assertEqual(base_dirpath, actual, "Expected base path to be '%s' but got '%s'." % (actual,base_dirpath))
        self.assertEqual(3, len(ll_dirs), 'Expected %d directories but got %d.' % (2,len(ll_dirs)))
        self.assertEqual(7, len(ll_files), 'Expected %d files but got %d.' % (6,len(ll_files)))

        ## cleanup
        self._remove_test_repo()
        shutil.rmtree(self.RESTORED_DATA_DIR)
        self.sut.argd['toarchpath'] = save_path ## for subsequent tests

    def testActionArchive(self):
        self._setup_test_repo()
        self.sut.action_archive()
        base_dirpath, ll_dirs, ll_files = nodup_archiving.walk_dir(self.REPO_TEST_DIR)
        self.assertEqual(self.REPO_TEST_DIR, base_dirpath, "Expected '%s' but got '%s'" % (self.REPO_TEST_DIR, base_dirpath))
        lendirs = len(ll_dirs)
        expected_dirs = 277
        self.assertEqual(lendirs, expected_dirs, "Expected %d directories, but got %d." % (lendirs, expected_dirs))
        lenfiles = len(ll_files)
        expected_files = 11
        self.assertEqual(lenfiles, expected_files, "Expected %d files, but got %d." % (lenfiles, expected_files))
        self._remove_test_repo()

    def testNewEmptyRepositoryByWalking(self):
        self._setup_test_repo()
        base_dirpath, ll_dirs, ll_files = nodup_archiving.walk_dir(self.REPO_TEST_DIR)
        self.assertEqual(base_dirpath, self.REPO_TEST_DIR, "Expected base path to be '%s' but got '%s'." % (self.REPO_TEST_DIR,base_dirpath))
        self.assertEqual(273, len(ll_dirs), 'Expected %d directories but got %d.' % (2,len(ll_dirs)))
        self.assertEqual(0, len(ll_files), 'Expected %d files but got %d.' % (6,len(ll_files)))
        self._remove_test_repo()

    def testNewRepositoryHasBeenSetUp(self):
        self._setup_test_repo()
        expected = True
        if not os.path.exists(self.REPO_TEST_DIR):
            expected = False
        self.assertTrue(expected, "Test repository has not been created for testing.")
        self._remove_test_repo()

    def testGetNormalizedPaths(self):
        self._setup_test_repo()
        repopath, toarchpath, repotree, repotree_fullpath = nodup_archiving.get_and_normalize_paths( self._get_argd() )
        expected = 'DELETEME_test_repo'
        self.assertEqual(expected, repopath, "Expected repopath '%s' but got '%s'." % (expected,repopath))
        expected = 'test_data'
        self.assertEqual(expected, toarchpath, "Expected toarchpath '%s' but got '%s'." % (expected,toarchpath))
        expected = 'test_data_1'
        self.assertEqual(expected, repotree, "Expected repotree '%s' but got '%s'." % (expected,repotree))
        expected = 'DELETEME_test_repo/test_data_1'
        self.assertEqual(expected, repotree_fullpath, "Expected repotree_fullpath '%s' but got '%s'." % (expected,repotree_fullpath))
        self._remove_test_repo()

    def testWalkDirectory(self):
        base_dirpath, ll_dirs, ll_files = nodup_archiving.walk_dir(self.TEST_DATA_DIR)
        self.assertEqual(base_dirpath, self.TEST_DATA_DIR, "Expected base path to be '%s' but got '%s'." % (self.TEST_DATA_DIR,base_dirpath))
        self.assertEqual(3, len(ll_dirs), 'Expected %d directories but got %d.' % (2,len(ll_dirs)))
        self.assertEqual(7, len(ll_files), 'Expected %d files but got %d.' % (6,len(ll_files)))

    def testDoMd5sum(self):
        expected = 'c3f83cc9949dfa4f823bfc9c1c7c7543'
        actual = nodup_archiving.get_file_md5(self.TEST_DATA_DIR + '/lorem.txt')
        self.assertEqual(expected, actual, "Expected MD5SUM of lorem.txt to be '%s', but got '%s'." % (expected, actual))

    def testChompRight(self):
        s = os.sep+'now'+os.sep+'is'+os.sep+'the'+os.sep+'time'+os.sep+os.sep+os.sep
        swant = os.sep+'now'+os.sep+'is'+os.sep+'the'+os.sep+'time'
        sgot = nodup_archiving.chomp_right(s)
        self.assertEqual(sgot, swant, "Did not chomp all right side path separators")
        sgot2 = nodup_archiving.chomp_right(sgot)
        self.assertEqual(sgot2, sgot, "")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    