#!/usr/bin/env python3

# Extract JSON data from a Parler archive, to import into DBs otherwise index.
# by philion@acmerocket.com

from metadata import extract_comments
import sys
import logging
import zipfile
import tarfile
import dateparser
import datetime
import os
import json

import pandas as pd

from selectolax.parser import HTMLParser
from pathlib import Path

# logging
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

## meta tags to ignore
META_IGNORE = {"viewport", "og:type", "og:site_name", "twitter:card", "twitter:title", 
        "twitter:description", "twitter:site", "twitter:image", "description",
        "theme-color"}    
    
ATTR_MAP = {
    "title": "meta[property='og:title']",
    "description": "meta[name='description']",
    "messageid": "meta[property='og:url']",
    "profilepic": "meta[property='og:image']",
    "username": ".post .author--username",
    "body": ".post .card--body > p",
    "impressions": ".impressions--count",
    "articlelink": ".mc-article--link",
    "weblink": ".mc-website--link",
    "timestr": ".post--timestamp",
    "commentcount": ".pa--item--wrapper img[alt='Post Comments'] + .pa--item--count",
    "echoes": ".pa--item--wrapper img[alt='Post Echoes'] + .pa--item--count",
    "upvotes": ".pa--item--wrapper img[alt='Post Upvotes'] + .pa--item--count"
}

# scrape all interesting data from the message. doesn't transform or interpret anything
def scrape_message(data):
    attrs = {}
    dom = HTMLParser(data)

    # pull known values
    for key, select in ATTR_MAP.items():
        val = ""
        for node in dom.css(select):
            #print(node.attributes, node.text(strip=True))
            if node.text() != "":
                val = node.text(strip=True)
            elif node.attributes.get("content") != "":
                val = node.attributes.get("content")
            else:
                logging.warning("### text: %s, attrs: %s", node.text(strip=True), node.attributes)
        if val != "" and key in attrs:
            logging.warning("### dup key: %s = %s, %s", key, attrs[key], val)
        elif val == "":
            logging.debug("missed key: %s, %s", key, select)
        else:
            attrs[key] = val
    
    # get metadata, make sure is covered (not dup)
    metatags = extract_meta_attrs(dom)
    vals = attrs.values()
    for tag, value in metatags.items():
        if value not in vals:
            attrs[tag] = value
        else:
            logging.debug("skipping dup value: %s - %s", tag, value)

    # get the comments
    comments = extract_comments(dom)
    #if len(comments) > 0:
        #print("###", comments)
        #attrs["comments"] = comments
        #if "commentcount" in attrs:
        #    expected_count = int(attrs["commentcount"])
        #    if len(comments) != expected_count:
        #        logging.warning("Mismatched comment counts: count=%s, length=%s", expected_count, len(comments))

    return attrs, comments
        
def extract_meta_attrs(dom):
    attrs = {}

    for tag in dom.tags("meta"):
        name = ""
        if "name" in tag.attributes:
            name = tag.attributes["name"]
        elif "property" in tag.attributes:
            name = tag.attributes["property"]

        if name != "" and name not in META_IGNORE:
            attrs[name] = tag.attributes["content"]

    return attrs



# borrowed from https://github.com/jlev/parler-etl/blob/master/transform-post-html-to-jsonl.py
# timestr represents something like "5 days ago", and is used to calulate against the download/extract time
# origin_time from the archive or file system 

time_strs = {}
def parse_relative_time(timestr, origin_time):
    if timestr is None:
        return None

    dt_parsed = dateparser.parse(timestr, languages=['en'])

    try:
        if "ago" in timestr:
            time_strs[timestr] = timestr # tracking all the time strings in the sample
            offset = datetime.datetime.now() - dt_parsed
            dt_approx = origin_time - offset
        else:
            dt_approx = dt_parsed
        return dt_approx
    except Exception as e:
        logging.error(f"Failed to parse datetime with timestamp: {timestr}, offset: {origin_time}: {e}")
        return None
    except KeyboardInterrupt:
        raise

# parse a buffer into useable metadata
def process_html(data, id, filedate):
    # parse into main message and sub-comments
    # fixme - scrape to record, not dict
    msg, comments = scrape_message(data)
    msg["id"] = id

    # process timestamp
    if "timestr" in msg:
        timestamp = parse_relative_time(msg["timestr"], filedate)
        if timestamp:
            msg["timestamp"] = timestamp.strftime("%c") # fixme to reliable struct

    #print(msg) # FIXME as json.

    # process comments
    for i, comment in enumerate(comments):
        comment["id"] = id + "_" + str(i)
        comment["refer"] = id
        if "timestr" in msg:
            timestamp = parse_relative_time(msg["timestr"], filedate)
            if timestamp:
                comment["timestamp"] = timestamp.strftime("%c") # fixme to reliable struct
        #print(comment)
    
    comments.insert(0, msg)
    return comments

def extract_zip(archive_name):
    zf = zipfile.ZipFile(archive_name)

    i = 0

    for info in zf.infolist():
        try:    
            data = zf.read(info.filename)
            process_html(data)
            i = i+1
        except KeyError:
            logging.error("Did not find %s in zip file" % info.filename)

    print("Extracted %s records", i)


file_types = {}
def extract_tgz(archive_name):

    with tarfile.open(archive_name) as tar:
        i = 0
        allmsg = []
        for info in tar:
            # checking for '/post', there's probably a better way...
            if info.isfile() and info.size > 0 and info.name.find("/post/") >= 0:
                name = info.name
                for strippable in ["?", "&", ";"]:
                    idx = name.find(strippable)
                    if idx >= 0:
                        name = name[:idx]
                        break

                ext = Path(name).suffix
                if len(ext) == 0:
                    file_types["none"] = 1 + file_types.get("none", 0)
                else:
                    file_types[ext] = 1 + file_types.get(ext, 0)

                if ext in [".html",".htm"]:
                    id = Path(info.name).stem
                    data = tar.extractfile(info.name).read()
                    # construct a download timestamp for the file
                    timestamp = datetime.datetime.utcfromtimestamp(info.mtime)
                    #print(id, timestamp)
                    messages = process_html(data, id, timestamp)
                    allmsg += messages
                    i+=1

            if i >= 1000: break
        print(to_json(allmsg))
        print("File types:", file_types)
        print("Times:", time_strs)
        tar.close()
    print("Extracted records:", len(allmsg))

def extract_file(filename):
    file = open(filename, "r")
    id = Path(filename).stem
    timestamp = datetime.datetime.utcfromtimestamp(os.stat(filename).st_mtime)
    messages = process_html(file.read(), id, timestamp)
    file.close()
    return messages

# output csv
def to_csv(messages):
    return pd.DataFrame(messages).to_csv()

def to_json(messages):
    return json.dumps(messages, indent=4)


def main():
    for filename in sys.argv[1:]:
        if filename.endswith(".zip"):
            extract_zip(filename)
        elif filename.endswith((".tar.gz", ".tgz")):
            extract_tgz(filename)
        else:
            messages = extract_file(filename)
            print(to_json(messages))

if __name__ == '__main__':
    sys.exit(main())
