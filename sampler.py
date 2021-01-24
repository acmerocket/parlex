#!/usr/bin/env python3

# Pull a sample of files from the larger dataset, for testing and verification
# Currently, designed to pull the largest 100 docs and dump to files

# by philion@acmerocket.com

import sys
import logging
import zipfile


def sample_archive(archive_name, count):
    sizes = []
    print("loading data")
    with zipfile.ZipFile(archive_name) as zf:
        i = 0
        infolist = zf.infolist()
        print("sorting file sizes")
        infolist.sort(key=lambda z: z.file_size, reverse=True)
        print("writing", count, "sample files")
        for info in infolist:
            i+=1
            if i >= count:
                break
            zf.extract(info.filename, "data/samples")

def main():
    sample_archive(sys.argv[1], 10)


if __name__ == '__main__':
    sys.exit(main())
