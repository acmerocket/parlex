
import unittest

from pathlib import Path

from parlex.extractor import extract_file

# import logging

# logging
# LOG_FORMAT = "%(asctime)s %(name)s: %(message)s"
# logging.basicConfig(level=logging.INFO, format = LOG_FORMAT)

RESOURCES = "tests/resources/"

class TestExtractor(unittest.TestCase):
    def test_weblink(self):
        file = Path(RESOURCES + "4beec3bf2543403b8c32abcacbc59530.html").absolute()
        extracted = extract_file(file)
        self.assertGreater(len(extracted), 0)
        self.assertIn("weblink", extracted[0])
        self.assertTrue(extracted[0]["weblink"].startswith("https://rumble.com/"))
        # logging.info(to_json(extracted))
