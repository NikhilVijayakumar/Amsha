import os

from markdown_it import MarkdownIt


class MarkdownProcessor:

    def __init__(self, md_config=None):
        if md_config is None:
            # Default configuration: enable common Markdown rules
            self.md = MarkdownIt().enable([
                'heading', 'paragraph', 'list', 'code', 'fence', 'image', 'link', 'text',
                'strong', 'em', 's_inline', 'backticks', 'linkify', 'autolink', 'hr',
                'blockquote', 'table', 'dl', 'abbr', 'footnote', 'sup', 'sub', 'mark',
                'container', 'deflist', 'cmark'  # More comprehensive CommonMark support
            ])
        else:
            self.md = MarkdownIt(md_config)

    def parse_to_tokens(self, markdown_text):
        return self.md.parse(markdown_text)

    def get_structured_elements(self, markdown_text):
        tokens = self.parse_to_tokens(markdown_text)
        parsed_data = []
        current_heading_data = None
        current_paragraph_content = []

        for i, token in enumerate(tokens):
            if token.type == 'heading_open':
                heading_level = int(token.tag[1])
                # Find the actual heading text from the next inline token
                heading_text = ""
                if i + 1 < len(tokens) and tokens[i + 1].type == 'inline':
                    heading_text = tokens[i + 1].content
                current_heading_data = {'type': 'heading', 'level': heading_level, 'text': heading_text}
                parsed_data.append(current_heading_data)
            elif token.type == 'paragraph_open':
                current_paragraph_content = []
            elif token.type == 'inline' and current_paragraph_content is not None:
                # Capture content for current paragraph or list item
                if tokens[i - 1].type == 'paragraph_open' or \
                        (i > 1 and tokens[i - 2].type == 'paragraph_open' and tokens[i - 1].type == 'inline') or \
                        tokens[i - 1].type == 'list_item_open' or \
                        (i > 1 and tokens[i - 2].type == 'list_item_open' and tokens[i - 1].type == 'inline'):
                    current_paragraph_content.append(token.content)
            elif token.type == 'paragraph_close':
                if current_paragraph_content:
                    parsed_data.append({'type': 'paragraph', 'content': ' '.join(current_paragraph_content).strip()})
                current_paragraph_content = None  # Reset
            elif token.type == 'fence':  # Code blocks
                parsed_data.append({'type': 'code_block', 'lang': token.info.strip(), 'content': token.content})
            # Add basic handling for list items (can be expanded for nested lists)
            elif token.type == 'list_item_open':
                # This needs more sophisticated parsing to capture full list content,
                # but we'll include it for basic recognition.
                pass  # The content is usually in an inline token immediately following.

        return parsed_data


    def to_plaintext(self, markdown_text):
        tokens = self.parse_to_tokens(markdown_text)
        plaintext_parts = []
        for token in tokens:
            if token.type == 'text' and token.content:
                plaintext_parts.append(token.content)
            elif token.type == 'inline' and token.children:
                # Iterate children of inline tokens to get text
                for child in token.children:
                    if child.type == 'text' and child.content:
                        plaintext_parts.append(child.content)
            elif token.type in ['paragraph_open', 'heading_open', 'list_item_open', 'fence', 'blockquote_open']:
                # Add a space or newline to separate blocks
                plaintext_parts.append(' ')
            elif token.type == 'softbreak':
                plaintext_parts.append(' ')  # Replace softbreak with space
            elif token.type == 'hardbreak':
                plaintext_parts.append('\n')  # Replace hardbreak with newline
            elif token.type == 'fence' and token.content:
                plaintext_parts.append(token.content)  # Preserve code block content

        # Join and clean up multiple spaces/newlines
        clean_text = ' '.join(plaintext_parts)
        clean_text = ' '.join(clean_text.split())  # Remove extra spaces
        return clean_text.strip()

    def _get_heading_text_from_tokens(self, tokens, h_open_token_idx):
        for j in range(h_open_token_idx + 1, len(tokens)):
            if tokens[j].type == 'inline':
                return tokens[j].content
            elif tokens[j].type == 'heading_close':
                # Stop if we hit the close tag without finding inline text
                break
        return ""  # Should not happen with well-formed Markdown and 'inline' rule enabled

    def get_chunks_by_heading(self, markdown_text, include_header_in_chunk=True):
        tokens = self.parse_to_tokens(markdown_text)

        chunks = {}
        current_heading_text = "HEADER_LESS_CONTENT"  # For content before the first heading
        current_chunk_tokens = []

        for i, token in enumerate(tokens):
            if token.type == 'heading_open':
                # Save the content of the previous chunk
                if current_chunk_tokens:
                    current_chunk_md = self.md.renderer.render(current_chunk_tokens, self.md.options, {})
                    chunks[current_heading_text] = current_chunk_md.strip()

                # Start new chunk
                current_heading_text = self._get_heading_text_from_tokens(tokens, i)
                current_chunk_tokens = []

                # If we want to include the header in the chunk, add the 'heading_open' and 'inline' tokens
                if include_header_in_chunk:
                    current_chunk_tokens.append(token)  # heading_open
                    if i + 1 < len(tokens) and tokens[i + 1].type == 'inline':
                        current_chunk_tokens.append(tokens[i + 1])  # inline (text)
                    if i + 2 < len(tokens) and tokens[i + 2].type == 'heading_close':
                        current_chunk_tokens.append(tokens[i + 2])  # heading_close
                    # Add a newline for separation (mimics common Markdown rendering)
                    current_chunk_tokens.append(type('Token', (object,), {'type': 'softbreak', 'level': 0})())

            else:
                current_chunk_tokens.append(token)

        # Add the last chunk's content
        if current_chunk_tokens:
            last_chunk_md = self.md.renderer.render(current_chunk_tokens, self.md.options, {})
            chunks[current_heading_text] = last_chunk_md.strip()

        # Filter out empty chunks that might arise from empty sections
        return {k: v for k, v in chunks.items() if v}

    @staticmethod
    def _is_valid_markdown_extension(file_path: str) -> bool:
        valid_extensions = {'.md', '.markdown', '.mdown'}
        _, ext = os.path.splitext(file_path)
        return ext.lower() in valid_extensions

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
                "Please provide a file with one of the supported Markdown extensions: .md, .markdown, or .mdown."
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
