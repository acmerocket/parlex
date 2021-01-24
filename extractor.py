#!/usr/bin/env python3

# Extract JSON data from a Parler archive, to import into DBs otherwise index.
# by philion@acmerocket.com

import sys
import logging
import zipfile

from selectolax.parser import HTMLParser

## meta tags to ignore
META_IGNORE = {"viewport", "og:type", "og:site_name", "twitter:card", "twitter:title", 
        "twitter:description", "twitter:site", "twitter:image", "description",
        "theme-color"}


class ParlerMessage:
  def __init__(self, mid, uid, title, desc, user, text):
    self.title = title
    self.description = desc
    self.messageid = mid
    self.userid = uid
    self.username = user
    self.text = text
    

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


def process_file(data):
    attrs = parse_message(data)
    print(attrs)

    
ATTR_MAP = {
    "title": "meta[property='og:title']",
    "description": "meta[name='description']",
    "messageid": "meta[property='og:url']",
    "userid": "meta[property='og:image']",
    "username": ".author--username",
    "text": "div.card--body > p",
    "impressions": ".impressions--count",
    "link": ".mc-article--link > a",
    "comments": ".pa--item--wrapper img[alt='Post Comments'] + .pa--item--count",
    "echoes": ".pa--item--wrapper img[alt='Post Echoes'] + .pa--item--count",
    "upvotes": ".pa--item--wrapper img[alt='Post Upvotes'] + .pa--item--count"
}

def parse_message(data):
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

    return attrs
        

## OLD version
def parse_content(data):
    dom = HTMLParser(data)

    title = dom.css_first("meta[property='og:title']").attributes["content"]
    desc = dom.css_first("meta[name='description']").attributes["content"]
    mid = dom.css_first("meta[property='og:url']").attributes["content"] 
    uid = dom.css_first("meta[property='og:image']").attributes["content"] 

    user = dom.css_first(".author--username").text()
    text = dom.css_first("div.card--body > p").text(strip=True)

    message = ParlerMessage(mid, uid, title, desc, user, text)
    print(message.__dict__)


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

def main():
    extract_all(sys.argv[1])

    ## TODO: Move to tests
    #process_file(open("pdb/untitled 4.html", "r").read())



if __name__ == '__main__':
    sys.exit(main())
