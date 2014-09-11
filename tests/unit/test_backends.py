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

from safebox import backends


class TestLocalStorage(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.backend = backends.LocalStorage(self.tempdir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_put_get(self):
        """ Test if object put/get is handled correctly """

        self.backend.put("name", "content")
        data = self.backend.get("name")
        self.assertEqual("content", data)

        # Non-existing object
        self.assertRaises(Exception, self.backend.get, "nonexisting")

    def test_fullname(self):
        objname = "c-af2bdbe1aa9b6ec1e2ade1d694f41f"
        reference = os.path.join(self.tempdir, "c/f4/1f", objname)
        pathname, fullname = self.backend.fullname(objname)
        self.assertEqual(reference, fullname)


if __name__ == '__main__':
    unittest.main()
