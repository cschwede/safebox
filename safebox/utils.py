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
import collections
import hashlib
import os


def sha256_string(string, secret=""):
    """ Returns SHA256 hexdigest for given string. """
    return hashlib.sha256(string).hexdigest()


def sha256_file(filename, block_size=2 ** 20):
    """ Returns SHA256 hexdigest for given file. """
    my_sha256 = hashlib.sha256()
    try:
        with open(filename, 'rb') as infile:
            for chunk in iter(lambda: infile.read(block_size), ''):
                my_sha256.update(chunk)
            return my_sha256.hexdigest()
    except IOError:
        return None


def find_modified_files(path):
    """ Find all directories and files in path.

    Returns a dictionary composed of filesystem names as keys and their
    stat as values. """
    path = os.path.expanduser(path).encode("utf-8")
    filelist = collections.OrderedDict()
    for dirname, _, filenames in os.walk(path):
        stat = os.lstat(dirname)

        rel_dirname = dirname.replace(path, '')
        rel_dirname += os.path.sep
        rel_dirname = rel_dirname.lstrip('/')

        if rel_dirname:  # skip root entry
            filelist[rel_dirname] = stat2dict(stat)

        for filename in filenames:
            fullname = os.path.join(dirname, filename)
            stat = os.lstat(fullname)
            rel_filename = os.path.join(rel_dirname, filename)
            filelist[rel_filename] = stat2dict(stat)
    return filelist


def stat2dict(stat):
    return {'s': stat.st_size,
            'u': stat.st_uid,
            'g': stat.st_gid,
            'm': stat.st_mtime,
            'p': stat.st_mode}


def sizeof_fmt(num):
    unit = "B"
    for u in ['kB','MB','GB','TB']:
        if abs(num) >= 1000.0:
            num /= 1000.0
            unit = u
    return "%3.1f %s" % (num, unit)
