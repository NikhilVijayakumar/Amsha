"""
Unit tests for Utf8Utils utility class.
"""
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from amsha.utils.utf8_utils import Utf8Utils


class TestUtf8Utils(unittest.TestCase):
    """Test cases for Utf8Utils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.txt')
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_convert_to_utf8_already_utf8(self):
        """Test conversion when file is already UTF-8."""
        # Create a UTF-8 file
        test_content = "Hello World! 你好世界"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        converter = Utf8Utils(self.test_file)
        converter.convert_to_utf8()
        
        # Verify file is still UTF-8 and content is preserved
        with open(self.test_file, 'r', encoding='utf-8') as f:
            result = f.read()
        
        self.assertEqual(result, test_content)
    
    def test_convert_to_utf8_from_latin1(self):
        """Test conversion from Latin-1 to UTF-8."""
        # Create a Latin-1 encoded file
        test_content = "Café résumé"
        with open(self.test_file, 'wb') as f:
            f.write(test_content.encode('latin-1'))
        
        converter = Utf8Utils(self.test_file)
        converter.convert_to_utf8()
        
        # Verify file is now UTF-8
        with open(self.test_file, 'r', encoding='utf-8') as f:
            result = f.read()
        
        self.assertEqual(result, test_content)
    
    def test_convert_to_utf8_low_confidence_fallback(self):
        """Test fallback to latin-1 when confidence is low."""
        # Create a file with mixed encodings that will have low confidence
        test_bytes = b'Some text with \xe9 special chars'
        
        with open(self.test_file, 'wb') as f:
            f.write(test_bytes)
        
        # Mock chardet to return low confidence
        with patch('amsha.utils.utf8_utils.chardet.detect') as mock_detect:
            mock_detect.return_value = {
                'encoding': 'unknown',
                'confidence': 0.5
            }
            
            converter = Utf8Utils(self.test_file)
            converter.convert_to_utf8()
        
        # File should still exist and be readable
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r', encoding='utf-8') as f:
            result = f.read()
        self.assertIsInstance(result, str)
    
    def test_convert_to_utf8_with_errors_replace(self):
        """Test conversion with problematic characters using replace strategy."""
        # Create bytes that will cause decode errors
        problematic_bytes = b'Hello \xff\xfe World'
        
        with open(self.test_file, 'wb') as f:
            f.write(problematic_bytes)
        
        converter = Utf8Utils(self.test_file)
        
        # This should not raise an exception
        try:
            converter.convert_to_utf8()
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_convert_to_utf8_file_not_found(self):
        """Test handling of non-existent file."""
        non_existent_file = os.path.join(self.test_dir, 'does_not_exist.txt')
        
        converter = Utf8Utils(non_existent_file)
        
        # Should not raise exception, just prints error
        try:
            converter.convert_to_utf8()
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    @patch('builtins.print')
    def test_convert_to_utf8_prints_encoding_info(self, mock_print):
        """Test that encoding detection info is printed."""
        test_content = "Simple ASCII text"
        with open(self.test_file, 'wb') as f:
            f.write(test_content.encode('utf-8'))
        
        converter = Utf8Utils(self.test_file)
        converter.convert_to_utf8()
        
        # Check that print was called with encoding information
        self.assertTrue(mock_print.called)
        call_args_str = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn('encoding', call_args_str.lower())
    
    @patch('builtins.print')
    def test_convert_to_utf8_success_message(self, mock_print):
        """Test that success message is printed."""
        test_content = "Test content"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        converter = Utf8Utils(self.test_file)
        converter.convert_to_utf8()
        
        # Check for success message
        call_args_str = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn('successfully', call_args_str.lower())
    
    def test_convert_to_utf8_preserves_content(self):
        """Test that conversion preserves file content."""
        test_content = "Line 1\nLine 2\nLine 3 with special: é à ñ"
        
        # Write with UTF-8
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        converter = Utf8Utils(self.test_file)
        converter.convert_to_utf8()
        
        # Read back and verify
        with open(self.test_file, 'r', encoding='utf-8') as f:
            result = f.read()
        
        self.assertEqual(result, test_content)
    
    def test_convert_to_utf8_initialization(self):
        """Test proper initialization of Utf8Utils."""
        converter = Utf8Utils(self.test_file)
        
        self.assertEqual(converter.file_path, self.test_file)


if __name__ == '__main__':
    unittest.main()
