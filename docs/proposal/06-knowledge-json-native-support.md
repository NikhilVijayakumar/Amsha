# Proposal 06 — Native JSON Knowledge Source Support

| | |
|---|---|
| **Priority** | Phase 4, easy win |
| **Risk** | Low |
| **Effort** | Small |
| **Depends on** | [02](02-crewai-version-migration.md) |

## The specific gap the user flagged

Amsha's knowledge support is entirely routed through `AmshaCrewDoclingSource` (`crew_forge/knowledge/amsha_crew_docling_source.py`), which wraps `docling.document_converter.DocumentConverter` with `allowed_formats=[MD, ASCIIDOC, PDF, DOCX, HTML, IMAGE, XLSX, PPTX]`. **JSON is not in that list, and docling doesn't have a JSON conversion path** — so Amsha genuinely cannot ingest JSON as a knowledge source today. This matches what was reported.

## What CrewAI 1.x actually offers

CrewAI ships **JSON as a native, built-in knowledge source type** alongside `StringKnowledgeSource`, `.txt`, PDF, CSV, XLSX — no docling required for it. This isn't a docling limitation Amsha needs to work around; it's a format CrewAI already handles natively and Amsha simply never exposed a path to it because `AmshaCrewDoclingSource` is currently the *only* knowledge source class Amsha's builder API knows about.

## Proposal

1. Add a thin passthrough in `CrewBuilderService.add_agent()`/`.build()` — both already accept a `knowledge_sources` parameter and just assign it (`agent.knowledge_sources = knowledge_sources` / `crew.knowledge_sources = knowledge_sources`). **No change needed there** — a caller can already pass CrewAI's native JSON knowledge source instance today; the gap is that nothing in Amsha's domain layer or docs tells users this is possible, and there's no Amsha-side construction helper for it the way there is for `AmshaCrewDoclingSource`.
2. Add a small `AmshaJsonKnowledgeSource` convenience wrapper (or simply document direct use of CrewAI's native JSON source class) in `crew_forge/knowledge/`, following the same file-path-validation pattern `AmshaCrewDoclingSource.validate_content()` already establishes, so JSON sources get the same local-path/URL handling consistency as docling sources.
3. Update `docs/feature/crew_forge/About.md`'s "Advanced Knowledge Management" section — it currently says "Multi-Format Support... (Currently tested with Markdown)" with no mention of JSON/CSV/XLSX being reachable via CrewAI natively.

## What NOT to do

- Don't extend `AmshaCrewDoclingSource` itself to handle JSON — docling isn't the right tool for structured JSON knowledge, and forcing it through a document-conversion pipeline designed for unstructured/semi-structured documents would be the wrong abstraction. Use CrewAI's native JSON source directly.
