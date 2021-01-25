#!/usr/bin/env python3

# Scrape metadata from a compressed archive. 
# Currently, just some tools to example the dataset and find taggable data.

# by philion@acmerocket.com

import sys
import logging
from typing import Text
import zipfile
import pprint
import os

from selectolax.parser import HTMLParser

## meta tags to ignore
META_IGNORE = {"viewport", "og:type", "og:site_name", "twitter:card", "twitter:title", 
        "twitter:description", "twitter:site", "twitter:image", "description",
        "theme-color"}

#ALL_TAGS = {}

def og_metadata(dom):
    attrs = {}

    for tag in dom.tags("meta"):
        if "property" in tag.attributes:
            name = tag.attributes["property"]
            attrs[name] = tag.attributes["content"]

    return attrs

def sample_archive(archive_name, count):

    zf = zipfile.ZipFile(archive_name)

    i = 0
    for info in zf.infolist():
        try:    
            data = zf.read(info.filename)
            process_file(data)
            i += 1
        except KeyError:
            logging.error("Did not find %s in zip file" % info.filename)

    print("processed %s records", i)


# scrape_tags - low-level data scraping indented for verification and coverage. 
# Desired metadata is captured "structurally" with CSS selectors, while this captures 
# all data to verify is anything is missing.
def scrape_tags(dom):
    attrs = {}
    for node in dom.css("*"):
        value = nodevalue(node)
        if value is not None:
            name = nodename(node)
            #print(name, " -> ", value)

            # check for duplicate key
            if name not in attrs:
                attrs[name] = [value]
            else:
                attrs[name].append(value)
    return attrs


# nodevalue - determine is there is a worthwile value in the node (text or attribute) and return it, or None.  
def nodevalue(node):
    text = node.text(deep=False, strip=True)
    if text is not None and len(text) > 0:
        return text
    else:
        # check a bunch of attributes
        for attr in ["content", "href", "src"]:
            if attr in node.attributes:
                return node.attributes[attr]
    
    # some data splunking
    if (len(node.attributes) > 0):
        logging.debug("No value found for:", node.attributes)
    return None

# nodename - derive a name for the node, based on metadata or structure in DOM.
def nodename(node):
    # check a bunch of attributes
    for attr in ["id", "name", "property"]:
        if attr in node.attributes:
            return node.attributes[attr]
    
    # no known name, construct from class?
    name = ""
    if "class" in node.attributes:
        name += node.attributes.get("class")
    if "class" in node.parent.attributes:
        name = node.parent.attributes.get("class") + name
    return name


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

COMMENT_MAPPING = {
    "body": ".card--body",
    "name": ".author--name",
    "username": ".author--username",
    "replies": ".ca--item--wrapper img[alt='Replies'] + .ca--item--count",
    "echoes": ".ca--item--wrapper img[alt='Post Echoes'] + .ca--item--count",
    "upvotes": ".ca--item--wrapper img[alt='Post Upvotes'] + .ca--item--count"

    #"badge": ".ch--avatar--badge--wrapper",
    #"avatar": ".ch--avatar--wrapper",
    #"profile": ".pf--jccard-meta--row"
}
# Reurns an array of 
def extract_comments(dom):
    data = {}
    comments = []

    for comment_node in dom.css("div.reply--card--wrapper"):
        comment = {}
        for key, select in COMMENT_MAPPING.items():
            for node in comment_node.css(select):
                value = node.text(strip=True)
                #print("--", key, value)
                comment[key] = value

        comments.append(comment)

    return comments

def process_file(data):
    # build a dom
    dom = HTMLParser(data)

    comments = extract_comments(dom)

    # Process all the tags in the file to
    #og_tags = og_metadata(dom) 
    #other_metadata = extract_meta_attrs(dom)
    
    tags = scrape_tags(dom)

    pp = pprint.PrettyPrinter(indent=4, width=160)
    pp.pprint(comments)
    #pp.pprint(other_metadata)



def extract_all(archive_name):
    zf = zipfile.ZipFile(archive_name)

    i = 0

    for info in zf.infolist():
        try:    
            data = zf.read(info.filename)
            process_file(data)
            i = i+1
        except KeyError:
            logging.error("Did not find %s in zip file" % info.filename)

    print("Extracted %s records", i)

def main():
    if len(sys.argv) == 0:
        process_file(open("pdb/untitled 4.html", "r").read()) ## simple test, move to test
    else:
        for filename in sys.argv:
            if filename.endswith(".zip"):
                extract_all(filename)
            elif os.path.isdir(filename):
                # process everything in the dir
                for file in os.listdir(filename):
                    process_file(open(file, "r").read())
            else:
                process_file(open(filename, "r").read())


if __name__ == '__main__':
    sys.exit(main())
