'''
Created on Jul 14, 2012

@author: tpe
'''
import os
import shutil
import unittest
import nodup_archiving

class Test(unittest.TestCase):

    TEST_TMP_DIR = "test_tmp_dir"

    def setUp(self):
        if os.path.exists(self.TEST_TMP_DIR):
            raise Exception("'%s' already exists. Delete it before running unit tests." % self.TEST_TMP_DIR)

    def tearDown(self):
        if os.path.exists(self.TEST_TMP_DIR):
            os.removedirs( self.TEST_TMP_DIR )


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
    