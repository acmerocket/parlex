from extractor import extract_file, to_json
import unittest

RESOURCES = "test/resources/"

class TestExtractor(unittest.TestCase):
    def test_weblink(self):
        extracted = extract_file(RESOURCES + "37395ea23a4444698454bec6e02f6edd")
        self.assertGreater(len(extracted), 0)
        print(to_json(extracted))