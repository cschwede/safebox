#!/usr/bin/python
"""
Copyright 2014 Christian Schwede.

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

import mock
import sys
import unittest
from cStringIO import StringIO

from safebox import shell


class TestShell(unittest.TestCase):
    def setUp(self):
        self.stdout, sys.stdout = sys.stdout, StringIO()
        self.stderr, sys.stderr = sys.stderr, StringIO()

    def tearDown(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    @mock.patch('safebox.common.backup')
    @mock.patch('safebox.backends.LocalStorage')
    def test_backup(self, mock_backend, mock_backup):
        """ Test if backup args are parsed correctly """

        # Not enough args
        argv = ["", "backup"]
        self.assertRaises(SystemExit, shell.main, argv)

        argv = ["", "backup", "src"]
        self.assertRaises(SystemExit, shell.main, argv)

        argv = ["", "backup", "src", "dst"]
        shell.main(argv)
        mock_backup.assert_called_once()
        self.assertEqual("src", mock_backup.call_args[0][1])
        self.assertEqual("default", mock_backup.call_args[0][2])
        self.assertEqual("dst", mock_backend.call_args[0][0])

        argv = ["", "--tag", "something", "backup", "src", "dst"]
        shell.main(argv)
        self.assertEqual("src", mock_backup.call_args[0][1])
        self.assertEqual("something", mock_backup.call_args[0][2])
        self.assertEqual("dst", mock_backend.call_args[0][0])

    @mock.patch('safebox.common.restore')
    @mock.patch('safebox.backends.LocalStorage')
    def test_restore(self, mock_backend, mock_restore):
        """ Test if restore args are parsed correctly """

        # Not enough args
        argv = ["", "restore"]
        self.assertRaises(SystemExit, shell.main, argv)

        argv = ["", "restore", "src"]
        self.assertRaises(SystemExit, shell.main, argv)

        argv = ["", "restore", "src", "dst"]
        self.assertRaises(SystemExit, shell.main, argv)

        argv = ["", "restore", "src", "dst", "backup_id"]
        shell.main(argv)
        mock_restore.assert_called_once()
        self.assertEqual("dst", mock_restore.call_args[0][1])
        self.assertEqual("backup_id", mock_restore.call_args[0][2])
        self.assertEqual("src", mock_backend.call_args[0][0])
