#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from safebox import backends, common

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(levelname)s %(threadName)s %(asctime)s %(message)s"


def main(argv=sys.argv):
    """ Main function as used in CLI mode. """
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

    parser = argparse.ArgumentParser(
        description='Object-storage friendly deduplication backup')
    parser.add_argument('--hmac-key', default="", help='HMAC Key')
    parser.add_argument(
        '--tag', default="default", help='Tag to use for this backup')

    subparsers = parser.add_subparsers(dest="subparsers")

    parser_backup = subparsers.add_parser(
        'backup', help='Create new backup')
    parser_backup.add_argument(
        'src', action="store", type=str, help='Source path')
    parser_backup.add_argument(
        'path', action="store", type=str, help='Destination path')

    parser_restore = subparsers.add_parser(
        'restore', help='Restore from backup')
    parser_restore.add_argument(
        'path', action="store", type=str, help='Source path')
    parser_restore.add_argument(
        'dst', action="store", type=str, help='Destination path')
    parser_restore.add_argument(
        'backup_id', action="store", type=str, help='Backup ID')

    parser_restore = subparsers.add_parser(
        'gc', help='Garbage collect')
    parser_restore.add_argument(
        'path', action="store", type=str, help='Backup path')

    parser_list = subparsers.add_parser(
        'list', help='List backups')
    parser_list.add_argument(
        'path', action="store", type=str, help='Backup path')
    parser_list.add_argument(
        '--backup-id', action="store", type=str, help='Backup ID')

    args = parser.parse_args(argv[1:])

    path = os.path.expanduser(args.path)
    backend = backends.LocalStorage(path)

    if args.subparsers == "backup":
        common.backup(backend, args.src, args.tag)
    if args.subparsers == "restore":
        common.restore(backend, args.dst, args.backup_id)
    if args.subparsers == "gc":
        common.gc(backend)
    if args.subparsers == "list":
        common.list_backups(backend, args.path, args.backup_id)
