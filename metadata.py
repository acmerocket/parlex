#!/usr/bin/env python3

# Scrape metadata from a compressed archive. 
# Currently, just some tools to example the dataset and find taggable data.

# by philion@acmerocket.com

import sys
import logging
import zipfile
import pprint

from selectolax.parser import HTMLParser

## meta tags to ignore
META_IGNORE = {"viewport", "og:type", "og:site_name", "twitter:card", "twitter:title", 
        "twitter:description", "twitter:site", "twitter:image", "description",
        "theme-color"}

ALL_TAGS = {}

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


def scrape_tags(data):
    attrs = {}

    dom = HTMLParser(data)
    for node in dom.css("meta"):
        name = nodename(node)
        value = nodevalue(node)

        if name is not None and value is not None and len(value) > 0:
            print(name, " ==> ", value)
            #attrs[name] = value
        else:
            print("???", node.attributes, node.text(strip=True))

    return attrs
        
def nodevalue(node):
    text = value = node.text(deep=False, strip=True)
    content = None
    if "content" in node.attributes:
        content = node.attributes["content"]
    if "href" in node.attributes and content is None:
        content = node.attributes["href"]
    if len(text) > 0 and content is not None:
        #print("WARNING - mismatch content and text", content, text)
        return text
    elif content is not None:
        return content
    else:
        return text

def nodename(node):
    if "id" in node.attributes:
        return node.attributes["id"]
    if "name" in node.attributes:
        return node.attributes["name"]
    elif "property" in node.attributes:
        return node.attributes["property"]
    else:
        return node.attributes.get("class", None)
        #if node.parent is None:
        #    return node.attributes.get("class", "")
        #else:
        #    return nodename(node.parent) + "." + node.attributes.get("class", "")

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

def process_file(data):
    # Process all the tags in the file to
    tags = scrape_tags(data)

    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(tags)

    #ALL_TAGS.update(tags)

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
            else:
                process_file(open(filename, "r").read())


if __name__ == '__main__':
    sys.exit(main())
