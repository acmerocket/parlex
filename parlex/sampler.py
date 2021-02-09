#!/usr/bin/env python3

# Pull a sample of files from the larger dataset, for testing and verification
# Currently, designed to pull the largest 100 docs and dump to files

# by philion@acmerocket.com

import sys
import logging
import zipfile
import tarfile
import datetime
from pathlib import Path


def sample_zip_archive(archive_name, count):
    sizes = []
    print("loading data")
    with zipfile.ZipFile(archive_name) as zf:
        i = 0
        infolist = zf.infolist()
        print("sorting file sizes")
        infolist.sort(key=lambda z: z.file_size, reverse=True)
        print("writing", count, "sample files")
        for info in infolist:
            i += 1
            if i >= count:
                break
            zf.extract(info.filename, "test/resources")


def sample_tgz(archive_name, count):
    with tarfile.open(archive_name) as tar:
        i = 0
        infolist = tar.getmembers()
        print("sorting file sizes")
        infolist.sort(key=lambda z: z.size, reverse=True)
        print("writing", count, "sample files")
        for info in infolist:
            # checking for '/post', there's probably a better way...
            if "/post/" in info.name:
                tar.extract(info.name, path="test/resources")
                i += 1

            if i >= count:
                break
        tar.close()
    print("Extracted records:", i)


def main():
    sample_size = 100
    for filename in sys.argv[1:]:
        if filename.endswith(".zip"):
            sample_zip_archive(filename, sample_size)
        elif filename.endswith((".tar.gz", ".tgz")):
            sample_tgz(filename, sample_size)
        else:
            print("huh?", filename)
            exit(1)


if __name__ == "__main__":
    sys.exit(main())
