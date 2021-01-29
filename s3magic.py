#!/usr/bin/env python3

# Generate a set of detailed file data in an S3 bucket and dump as JSON
# Used to walk the contents of s3://ddosecrets-parler-* to get file metadata.
# Why? Because you can't tell anything from filesize.
# (see `man file`, https://pypi.org/project/filemagic/)

# by philion@acmerocket.com

import sys
import logging
import boto3

def visit_bucket(bucket_name):
    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')

    # Output the bucket names
    print('Existing buckets:')
    for bucket in s3.list_buckets(RequestPayer=True):
        print(f'  {bucket["Name"]}')

def main():
    visit_bucket("ddosecrets-parler")


if __name__ == '__main__':
    sys.exit(main())
