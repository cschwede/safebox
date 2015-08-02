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
from datetime import datetime
from string import ascii_letters, digits
import hashlib
import json
import logging
import os
import random
import time

from stat import S_ISREG

from rabin import rabin
from safebox import utils


def backup(backend, src, tag="default"):
    # Try to load old metadata from latest backup
    old_backups = backend.list(prefix="b-*")
    old_meta_data = {}
    if old_backups:
        backup_id = utils.newest_backup_id(old_backups)
        om = backend.get(backup_id)
        try:
            old_meta_data = json.loads(om)
        except ValueError:
            pass

    start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = os.path.expanduser(src)
    files = utils.find_modified_files(path)
    chunk_size = chunk_count = changed_bytes = 0
    for filename, meta in files.items():
        # Assume file is unchanged if neither mtime nor size is changed
        old = old_meta_data.get(unicode(filename, 'utf-8'))
        if old and old['m'] == meta['m'] and old['s'] == meta['s']:
            old_checksum = old.get('c')
            if old_checksum:
                meta['c'] = old_checksum
            logging.info("Skipped unchanged %s" % filename)
            continue

        fullname = os.path.join(path, filename)
        if not S_ISREG(meta['p']):  # not a file
            continue

        my_sha256 = hashlib.sha256()

        chunk_checksums = []
        try:
            chunks = rabin(fullname)
        except IOError:
            logging.warning("%s not found, skipping" % fullname)
            continue
        with open(fullname) as infile:
            for chunksize in chunks:
                data = infile.read(chunksize)
                my_sha256.update(data)
                chunk_checksum = utils.sha256_string(data)
                name = "c-%s" % chunk_checksum
                chunk_checksums.append(chunk_checksum)
                stored = backend.put(name, data)
                changed_bytes += len(data)
                if stored:
                    chunk_size += len(data)
                    chunk_count += 1

        checksum = my_sha256.hexdigest()
        name = "o-%s" % checksum
        backend.put(name, ';'.join(chunk_checksums))

        meta['c'] = name
        logging.info(fullname)

    # write backup summary
    meta_data = json.dumps(files)
    suffix = ''.join(random.choice(ascii_letters + digits) for _ in range(8))
    backup_id = "b-%s-%s-%s" % (tag, start_time, suffix)
    backend.put(backup_id, meta_data)
    logging.info("Finished backup %s. %s bytes changed" % (
                 backup_id, changed_bytes))
    logging.info("Stored %s new objects with a total size of %s bytes" % (
                 chunk_count, chunk_size))
    return backup_id


def restore(backend, dst, backup_id):
    dst = os.path.expanduser(dst)
    meta_data = backend.get(backup_id)
    meta_data = json.loads(meta_data)
    # sort to update directory mtime after files
    for filename in sorted(meta_data, reverse=True):
        entry = meta_data[filename]
        dst_filename = os.path.join(dst, filename)

        directory = os.path.dirname(dst_filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if S_ISREG(entry['p']):
            with open(dst_filename, "wb") as outfile:
                checksum = entry['c']
                list_of_chunks = backend.get(checksum)
                for chunk in list_of_chunks.split(';'):
                    data = backend.get("c-" + chunk)
                    outfile.write(data)

        # Set mtime, owner, group, permissisons
        os.utime(dst_filename, (time.time(), entry['m']))
        os.chmod(dst_filename, entry['p'])
        os.chown(dst_filename, entry['u'], entry['g'])
        logging.info("Restored: %s" % dst_filename)


def gc(backend):
    backups = backend.list("b-*")
    needed_chunks = []
    needed_objs = []
    for backup in backups:
        meta_data = backend.get(backup)
        meta_data = json.loads(meta_data)
        for _, entry in meta_data.items():
            content = entry.get('c', '')
            if content.startswith('c'):
                needed_chunks.append(content)
            if content.startswith('o'):
                needed_objs.append(content)
                list_of_chunks = backend.get(content)
                for chunk in list_of_chunks.split(';'):
                    needed_chunks.append("c-" + chunk)
    removed = []

    all_chunks = backend.list("c-*")
    for chunk in all_chunks:
        chunk_name = os.path.basename(chunk)
        if chunk_name not in needed_chunks:
            backend.delete(chunk_name)
            removed.append(chunk)
            logging.info("Removed chunk %s" % chunk)

    all_objs = backend.list("o-*")
    for obj in all_objs:
        obj_name = os.path.basename(obj)
        if obj_name not in needed_objs:
            backend.delete(obj_name)
            removed.append(obj)
            logging.info("Removed obj %s" % obj)
    return removed


def list_backups(backend, path, backup_id=None):
    backups = backend.list(prefix="b-*")
    for backup in backups:
        backup_name = os.path.basename(backup)
        if backup_id is None:
            print backup_name
        else:
            if backup_name == backup_id:
                om = backend.get(backup_id)
                try:
                    old_meta_data = json.loads(om)
                except ValueError:
                    pass
                for name in sorted(old_meta_data):
                    meta = old_meta_data.get(name)
                    datestring = time.strftime(
                        "%d %b %Y %H:%M:%S", time.localtime(meta.get('m')))
                    size = utils.sizeof_fmt(meta.get('s'))
                    print u"%20s %10s %s" % (datestring, size, name)
