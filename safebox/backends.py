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
import glob
import os


class LocalStorage(object):
    """ Storage backend using local files.

    Useful for testing and backing up to external disks. """
    def __init__(self, path):
        self.path = path

    def put(self, name, data):
        """ Write an object if not yet existing """
        filename = os.path.join(self.path, name)

        data = self._convert_data_in(data)

        if not os.path.exists(filename):
            with open(filename, "wb") as outfile:
                outfile.write(data)

    def get(self, name):
        """ Read an object """
        filename = os.path.join(self.path, name)
        with open(filename) as infile:
            return infile.read()

    def delete(self, name):
        """ Delete an object """
        filename = os.path.join(self.path, name)
        os.remove(filename)

    def list(self, prefix=""):
        """ List objects, filtering with prefix if given """
        path = os.path.join(self.path, prefix)
        return glob.glob(path)
