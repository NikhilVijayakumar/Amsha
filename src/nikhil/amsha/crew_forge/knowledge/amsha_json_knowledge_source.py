from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


class AmshaJsonKnowledgeSource(JSONKnowledgeSource):
    """CrewAI's native JSON knowledge source with Amsha-style local path handling.

    The base ``JSONKnowledgeSource`` prefixes any *string* ``file_paths`` entry
    with its ``knowledge/`` directory and has no URL handling. This wrapper keeps
    the same behavior as :class:`AmshaCrewDoclingSource` instead — a string path
    is treated as a local filesystem path (absolute, or relative to the working
    directory), must exist, and remote URLs are rejected with a clear message
    (the native JSON source is local-file only).

    Example::

        from amsha.crew_forge.knowledge.amsha_json_knowledge_source import AmshaJsonKnowledgeSource

        knowledge_source = AmshaJsonKnowledgeSource(file_paths=["data/products.json"])
    """

    def _process_file_paths(self) -> List[Path]:
        if getattr(self, "file_path", None) is not None:
            self.file_paths = self.file_path

        if self.file_paths is None:
            raise ValueError("Your source must be provided with a file_paths: []")

        path_list: List[Union[str, Path]] = (
            [self.file_paths]
            if isinstance(self.file_paths, (str, Path))
            else list(self.file_paths)
            if isinstance(self.file_paths, (list, tuple))
            else []
        )

        if not path_list:
            raise ValueError("file_path/file_paths must be a Path, str, or a list of these types")

        processed: List[Path] = []
        for path in path_list:
            if isinstance(path, str) and urlparse(path).scheme in ("http", "https"):
                raise ValueError(
                    f"Remote URL not supported for JSON knowledge: {path}. "
                    "Download the file first and pass a local path."
                )
            local = Path(path)
            if not local.exists():
                raise FileNotFoundError(f"File not found: {local}")
            if not local.is_file():
                raise ValueError(f"Path is not a file: {local}")
            processed.append(local)
        return processed