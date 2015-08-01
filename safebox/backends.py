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
import fnmatch
import os


class LocalStorage(object):
    """ Storage backend using local files.

    Useful for testing and backing up to external disks. """
    def __init__(self, path):
        self.path = path

    def fullname(self, name):
        """ Return the full name of an object

        Using small chunk sizes results in millions of files, and they should
        not be stored in a single directory.  This method spreads them to a tree
        of subdirectories by using first and last four characters as
        identifiers.  For example, using an object with a name of
        c-af2bdbe1aa9b6ec1e2ade1d694f41f will be stored in
        c/f4/1f/c-af2bdbe1aa9b6ec1e2ade1d694f41f.  """
        if name[0] != "b":
            subpath = "%s/%s/%s" % (name[0], name[-4:-2], name[-2:])
        else:
            subpath = "%s" % name[0]
        pathname = os.path.join(self.path, subpath)
        fullname = os.path.join(pathname, name)
        return (pathname, fullname)

    def put(self, name, data):
        """ Write an object if not yet existing """
        pathname, filename = self.fullname(name)
        if not os.path.exists(pathname):
            os.makedirs(pathname)
        if not os.path.exists(filename):
            with open(filename, "wb") as outfile:
                outfile.write(data)
                return True
        return False

    def get(self, name):
        """ Read an object """
        pathname, filename = self.fullname(name)
        with open(filename) as infile:
            return infile.read()

    def delete(self, name):
        """ Delete an object """
        pathname, filename = self.fullname(name)
        os.remove(filename)

    def list(self, prefix=""):
        """ List objects, filtering with prefix if given """
        matches = []
        for root, dirnames, filenames in os.walk(self.path):
            for filename in fnmatch.filter(filenames, prefix):
                matches.append(os.path.join(root, filename))
        return matches
