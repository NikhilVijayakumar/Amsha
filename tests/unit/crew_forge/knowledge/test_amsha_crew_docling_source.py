import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock docling modules before importing the class under test
class MockConversionError(Exception):
    pass

mock_docling = MagicMock()
mock_docling_core = MagicMock()
sys.modules['docling'] = mock_docling
sys.modules['docling.datamodel'] = MagicMock()
sys.modules['docling.datamodel.base_models'] = MagicMock()
sys.modules['docling.document_converter'] = MagicMock()
sys.modules['docling.exceptions'] = MagicMock()
sys.modules['docling.exceptions'].ConversionError = MockConversionError
sys.modules['docling_core'] = mock_docling_core
sys.modules['docling_core.transforms'] = MagicMock()
sys.modules['docling_core.transforms.chunker'] = MagicMock()
sys.modules['docling_core.transforms.chunker.hierarchical_chunker'] = MagicMock()
sys.modules['docling_core.types'] = MagicMock()
sys.modules['docling_core.types.doc'] = MagicMock()
sys.modules['docling_core.types.doc.document'] = MagicMock()

from amsha.crew_forge.knowledge.amsha_crew_docling_source import AmshaCrewDoclingSource

class TestAmshaCrewDoclingSource(unittest.TestCase):
    def setUp(self):
        self.file_paths = ["test.pdf", "https://example.com/doc.html"]
        # Create a dummy file for local path tests
        self.local_file = Path("test.pdf")
        self.local_file.touch()

    def tearDown(self):
        if self.local_file.exists():
            self.local_file.unlink()

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_initialization_success(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            source = AmshaCrewDoclingSource(file_paths=self.file_paths)
            self.assertEqual(source.file_paths, self.file_paths)
            self.assertTrue(len(source.safe_file_paths) > 0)

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', False)
    def test_initialization_no_docling(self):
        with self.assertRaises(ImportError) as cm:
            AmshaCrewDoclingSource(file_paths=self.file_paths)
        self.assertIn("docling package is required", str(cm.exception))

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_deprecated_file_path(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'), \
             patch.object(AmshaCrewDoclingSource, '_load_content', return_value=[]):
            # Pass an empty list to file_paths to satisfy Pydantic
            source = AmshaCrewDoclingSource(file_path=self.file_paths, file_paths=[])
            self.assertEqual(source.file_paths, self.file_paths)

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_content_local_file(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            self.assertEqual(len(source.safe_file_paths), 1)
            self.assertIsInstance(source.safe_file_paths[0], Path)

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_content_file_not_found(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            with self.assertRaises(FileNotFoundError):
                AmshaCrewDoclingSource(file_paths=["non_existent.pdf"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_content_valid_url(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            source = AmshaCrewDoclingSource(file_paths=["https://example.com/doc.html"])
            self.assertEqual(len(source.safe_file_paths), 1)
            self.assertEqual(source.safe_file_paths[0], "https://example.com/doc.html")

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_content_invalid_url(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            with self.assertRaises(ValueError):
                AmshaCrewDoclingSource(file_paths=["https://invalid"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_load_content_success(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter') as mock_converter:
            mock_instance = mock_converter.return_value
            mock_result = MagicMock()
            mock_result.document = "MockDoc"
            mock_instance.convert_all.return_value = [mock_result]
            
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            self.assertEqual(source.content, ["MockDoc"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_load_content_conversion_error(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter') as mock_converter:
            mock_instance = mock_converter.return_value
            mock_instance.convert_all.side_effect = MockConversionError("Conversion failed")
            
            with self.assertRaises(MockConversionError):
                AmshaCrewDoclingSource(file_paths=["test.pdf"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_load_content_general_exception(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter') as mock_converter:
            mock_instance = mock_converter.return_value
            mock_instance.convert_all.side_effect = Exception("General error")
            
            with self.assertRaises(Exception):
                AmshaCrewDoclingSource(file_paths=["test.pdf"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_add_success(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter') as mock_converter, \
             patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.HierarchicalChunker') as mock_chunker:
            mock_instance = mock_converter.return_value
            mock_result = MagicMock()
            mock_doc = MagicMock()
            mock_result.document = mock_doc
            mock_instance.convert_all.return_value = [mock_result]
            
            mock_chunk = MagicMock()
            mock_chunk.text = "Chunk text"
            mock_chunker.return_value.chunk.return_value = [mock_chunk]
            
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            # Mock _save_documents to avoid actual file saving if it's implemented in Base class
            with patch.object(AmshaCrewDoclingSource, '_save_documents'):
                source.add()
                self.assertEqual(source.chunks, ["Chunk text"])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_add_empty_content(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            source.content = None
            source.add()
            self.assertEqual(source.chunks, [])

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_content_path_object(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            path_obj = Path("test.pdf")
            source = AmshaCrewDoclingSource(file_paths=[path_obj])
            self.assertEqual(len(source.safe_file_paths), 1)
            self.assertEqual(source.safe_file_paths[0], path_obj)

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_validate_url_exception(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'):
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            # Mock urlparse to raise an exception
            with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.urlparse', side_effect=Exception("Parse error")):
                result = source._validate_url("http://example.com")
                self.assertFalse(result)

    @patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DOCLING_AVAILABLE', True)
    def test_chunk_doc(self):
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.DocumentConverter'), \
             patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.HierarchicalChunker') as mock_chunker:
            source = AmshaCrewDoclingSource(file_paths=["test.pdf"])
            mock_doc = MagicMock()
            mock_chunk = MagicMock()
            mock_chunk.text = "Chunk text"
            mock_chunker.return_value.chunk.return_value = [mock_chunk]
            
            chunks = list(source._chunk_doc(mock_doc))
            self.assertEqual(chunks, ["Chunk text"])

if __name__ == '__main__':
    unittest.main()
