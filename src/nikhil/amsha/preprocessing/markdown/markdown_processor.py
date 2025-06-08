import os
import markdown
from bs4 import BeautifulSoup, Tag,NavigableString
import re

class MarkdownProcessor:

    VALID_MD_EXTENSIONS = {'.md', '.markdown', '.mdown'}
    HTML_PARSER = 'lxml'

    def __init__(self, markdown_extensions=None, markdown_extension_configs=None):

        if markdown_extensions is None:
            self.markdown_extensions = ['extra', 'nl2br']  # nl2br for preserving newlines
        else:
            self.markdown_extensions = markdown_extensions

        self.markdown_extension_configs = markdown_extension_configs if markdown_extension_configs is not None else {}

        print(f"MarkdownProcessor initialized with Markdown extensions: {self.markdown_extensions}")

    def _markdown_to_html(self, markdown_text: str) -> str:
        return markdown.markdown(
            markdown_text,
            extensions=self.markdown_extensions,
            extension_configs=self.markdown_extension_configs
        )

    @staticmethod
    def _is_valid_markdown_extension(file_path: str) -> bool:
        _, ext = os.path.splitext(file_path)
        return ext.lower() in MarkdownProcessor.VALID_MD_EXTENSIONS

    @staticmethod
    def read_markdown_from_file(file_path: str, encoding: str = 'utf-8') -> str:
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("`file_path` must be a non-empty string.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        if not os.path.isfile(file_path):
            raise IOError(f"The path '{file_path}' is not a file.")

        if not MarkdownProcessor._is_valid_markdown_extension(file_path):
            raise ValueError(
                f"The file '{file_path}' has an **unrecognized file extension for Markdown**. "
                "Please provide a file with one of the supported Markdown extensions: "
                f"{', '.join(MarkdownProcessor.VALID_MD_EXTENSIONS)}."
            )

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                f"Failed to decode file '{file_path}' with encoding '{encoding}'. "
                "Try a different encoding (e.g., 'latin-1' or 'cp1252'). Error: {e}"
            ) from e
        except IOError as e:
            raise IOError(f"An error occurred while reading the file '{file_path}': {e}") from e

    def get_structured_elements(self, markdown_text: str) -> list:
        html_content = self._markdown_to_html(markdown_text)
        soup = BeautifulSoup(html_content, MarkdownProcessor.HTML_PARSER)

        structured_data = []
        for element in soup.body.children:
            if isinstance(element, Tag):
                if element.name.startswith('h') and len(element.name) == 2 and element.name[1].isdigit():
                    structured_data.append({
                        'type': 'heading',
                        'level': int(element.name[1]),
                        'text': element.get_text(strip=True)
                    })
                elif element.name == 'p':
                    structured_data.append({
                        'type': 'paragraph',
                        'content': element.get_text(strip=True)
                    })
                elif element.name == 'pre':  # For code blocks
                    code_tag = element.find('code')
                    if code_tag:
                        lang = ''
                        if 'class' in code_tag.attrs:
                            for cls in code_tag.attrs['class']:
                                if cls.startswith('language-'):
                                    lang = cls.split('-')[1]
                                    break
                        structured_data.append({
                            'type': 'code_block',
                            'lang': lang,
                            'content': code_tag.get_text(strip=False)  # Preserve internal whitespace in code
                        })
                elif element.name in ['ul', 'ol']:
                    list_items = []
                    for li in element.find_all('li'):
                        list_items.append(li.get_text(strip=True))
                    structured_data.append({
                        'type': element.name,  # 'ul' or 'ol'
                        'items': list_items
                    })
                elif element.name == 'blockquote':
                    structured_data.append({
                        'type': 'blockquote',
                        'content': element.get_text(strip=True)
                    })
            elif isinstance(element, NavigableString) and element.strip():
                structured_data.append({
                    'type': 'text',
                    'content': str(element).strip()
                })
        return structured_data

    def get_chunks_by_heading(self, markdown_text: str, include_header_in_chunk: bool = True) -> dict:
        html_content = self._markdown_to_html(markdown_text)
        soup = BeautifulSoup(html_content, MarkdownProcessor.HTML_PARSER)

        chunks = {}
        current_heading_text = "HEADER_LESS_CONTENT"
        current_chunk_elements = []

        for element in soup.body.children:
            if isinstance(element, Tag) and element.name.startswith('h') and len(element.name) == 2 and element.name[
                1].isdigit():
                if current_chunk_elements:
                    chunks[current_heading_text] = ''.join(str(e) for e in current_chunk_elements).strip()

                current_heading_text = element.get_text(strip=True)
                current_chunk_elements = []

                if include_header_in_chunk:
                    current_chunk_elements.append(element)
            else:
                current_chunk_elements.append(element)

        # Add the last chunk's content
        if current_chunk_elements:
            chunks[current_heading_text] = ''.join(str(e) for e in current_chunk_elements).strip()

        # Filter out empty chunks
        return {k: v for k, v in chunks.items() if v}

    def markdown_to_plaintext(self, markdown_text: str) -> str:
        html_content = self._markdown_to_html(markdown_text)
        return MarkdownProcessor.get_plaintext(html_content)

    @staticmethod
    def get_plaintext(html_content: str) -> str:
        if not html_content.strip():
            return ""

        soup = BeautifulSoup(html_content, MarkdownProcessor.HTML_PARSER)

        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\n+', '\n\n', text)  # Collapse multiple newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
        return text.strip()