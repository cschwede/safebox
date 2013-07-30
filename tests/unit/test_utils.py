import os
import shutil
import tempfile
import unittest

from safebox import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.string = 'sample'
        self.reference = \
            'af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf'
        self.tempdir = tempfile.mkdtemp()
        self.tempfile = os.path.join(self.tempdir, 'sample')
        with open(self.tempfile, "wb") as tmpfile:
            tmpfile.write(self.string)
        self.subdir = os.path.join(self.tempdir, 'sub')
        self.subfile = os.path.join(self.subdir, 'file')
        os.mkdir(self.subdir)
        with open(self.subfile, "wb") as tmpfile:
            tmpfile.write(self.string)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_hmac_file(self):
        """ Test if file SHA256 is computed correctly """

        checksum = utils.sha256_file(self.tempfile)
        self.assertEqual(self.reference, checksum)

        checksum = utils.sha256_file(self.tempfile + ' ')
        self.assertEqual(None, checksum)

    def test_find_files(self):
        """ Test if all files in directory tree are found """
        files = utils.find_modified_files(self.tempdir)
        self.assertTrue('sample' in files)
        self.assertTrue('sub/' in files)
        self.assertTrue('sub/file' in files)


if __name__ == '__main__':
    unittest.main()
