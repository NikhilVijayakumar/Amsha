import chardet
import os

class FileUtils:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert_to_utf8(self):
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read()

            detected_info = chardet.ect(raw_data)
            current_encoding = detected_info['encoding']
            confidence = detected_info['confidence']

            if not current_encoding or confidence < 0.8:
                print(f"Warning: Could not reliably detect encoding for '{self.file_path}'. Confidence: {confidence:.2f}")
                print("Attempting to decode with a common fallback encoding (latin-1).")
                current_encoding = 'latin-1'

            print(f"Detected encoding: {current_encoding} with confidence {confidence:.2f}")

            content = raw_data.decode(current_encoding)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"File '{self.file_path}' has been successfully converted to UTF-8.")

        except Exception as e:
            print(f"An error occurred during conversion: {e}")


