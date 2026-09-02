"""
Unit tests for AmshaJsonKnowledgeSource.
"""
import json
import tempfile
import unittest
from pathlib import Path

from amsha.crew_forge.knowledge.amsha_json_knowledge_source import AmshaJsonKnowledgeSource


class TestAmshaJsonKnowledgeSource(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmpdir.name)
        self.json_file = self.tmpdir / "data.json"
        self.json_file.write_text(json.dumps({"name": "acme", "products": ["a", "b"]}), encoding="utf-8")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_loads_local_json(self):
        source = AmshaJsonKnowledgeSource(file_paths=[str(self.json_file)])
        self.assertEqual(source.safe_file_paths, [self.json_file])
        self.assertIn("name: acme", str(source.content[self.json_file]))

    def test_accepts_path_objects(self):
        source = AmshaJsonKnowledgeSource(file_paths=[self.json_file])
        self.assertEqual(source.safe_file_paths, [self.json_file])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            AmshaJsonKnowledgeSource(file_paths=[str(self.tmpdir / "nope.json")])

    def test_url_raises(self):
        with self.assertRaises(ValueError):
            AmshaJsonKnowledgeSource(file_paths=["https://example.com/data.json"])

    def test_deprecated_file_path_still_works(self):
        source = AmshaJsonKnowledgeSource(file_path=self.json_file, file_paths=[])
        self.assertEqual(source.safe_file_paths, [self.json_file])

    def test_no_paths_raises(self):
        with self.assertRaises(ValueError):
            AmshaJsonKnowledgeSource()


if __name__ == '__main__':
    unittest.main()