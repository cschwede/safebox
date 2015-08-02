#!/usr/bin/python
"""
Copyright 2013 Christian Schwede.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os
import shutil
import tempfile
import unittest
from filecmp import dircmp

import mock
from safebox import backends, common, utils


class TestBackupRestore(unittest.TestCase):
    def setUp(self):
        self.backup_dir = tempfile.mkdtemp()
        self.storage_dir = tempfile.mkdtemp()
        self.restore_dir = tempfile.mkdtemp()
        self.tempfile = os.path.join(self.backup_dir, 'x')
        self.tempfile2 = os.path.join(self.backup_dir, 'z')
        part_1 = os.urandom(200000)
        part_2a = os.urandom(10000)
        part_2b = os.urandom(10000)
        part_3 = os.urandom(200000)
        self.original_size = len(part_1) + len(part_2a) + len(part_3)
        self.original_size += len(part_1) + len(part_2b) + len(part_3)
        with open(self.tempfile, "wb") as tmpfile:
            tmpfile.write(part_1 + part_2a + part_3)
        self.subdir = os.path.join(self.backup_dir, 'sub')
        os.mkdir(self.subdir)
        self.subfile = os.path.join(self.subdir, 'o\xcc\x88')
        with open(self.subfile, "wb") as tmpfile:
            tmpfile.write(part_1 + part_2b + part_3)
        with open(self.tempfile2, "wb") as tmpfile:
            tmpfile.write("")

        self.backend = backends.LocalStorage(self.storage_dir)

    def tearDown(self):
        shutil.rmtree(self.backup_dir)
        shutil.rmtree(self.storage_dir)
        shutil.rmtree(self.restore_dir)

    def test_backup_restore(self):
        """ Test if backup and restore works correctly """

        backup_id = common.backup(self.backend, self.backup_dir)
        old_file = os.path.join(self.storage_dir, backup_id)

        # Create new backup, this should reuse the last metadata set and the
        # checksum should be reused. Metadata set should be identical
        with mock.patch('logging.info') as mock_log:
            backup_id = common.backup(self.backend, self.backup_dir)
            mock_log.assert_any_call('Skipped unchanged sub/o\xcc\x88')
        new_file = os.path.join(self.storage_dir, backup_id)
        self.assertEqual(utils.sha256_file(old_file), utils.sha256_file(new_file))

        # Check if data deduplication works
        chunks = utils.find_modified_files(self.storage_dir)
        storage_size = 0
        for filename, stat in chunks.items():
            if filename.startswith('c-'):
                storage_size += stat['s']
        self.assertTrue(storage_size < self.original_size)

        common.restore(self.backend, self.restore_dir, backup_id)

        # Compare original file content to restored file content
        for fn in ['x', 'sub/y']:
            old_filename = os.path.join(self.backup_dir, fn)
            old_hash = utils.sha256_file(old_filename)
            new_filename = os.path.join(self.restore_dir, fn)
            new_hash = utils.sha256_file(new_filename)
            self.assertEqual(old_hash, new_hash)

    def test_gc(self):
        """ Test if deletion of no longer required chunks works correctly

        1. Create a backup
        2. Delete a file
        3. Delete old backup
        4. Create another backup
        5. Run garbage collector
        6. Restore and ensure backup is identical to files from step 4 """

        backup_id = common.backup(self.backend, self.backup_dir)
        backup_path, backup_file = self.backend.fullname(backup_id)
        os.remove(backup_file)
        os.remove(os.path.join(self.backup_dir, "x"))
        backup_id = common.backup(self.backend, self.backup_dir)
        removed = common.gc(self.backend)
        self.assertTrue(removed)

        common.restore(self.backend, self.restore_dir, backup_id)

        result = dircmp(self.restore_dir, self.backup_dir)
        self.assertFalse(result.diff_files)
        for _, entry in result.subdirs.items():
            self.assertFalse(entry.diff_files)


if __name__ == '__main__':
    unittest.main()
