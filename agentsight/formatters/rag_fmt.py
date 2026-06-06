"""RAG adapter formatter.

Formats SourceItem data for direct use in RAG (Retrieval-Augmented Generation)
pipelines and LLM context windows.
"""

import json
from datetime import datetime, timezone
from typing import List

from ..models import SourceItem
from .base import BaseFormatter


class RAGFormatter(BaseFormatter):
    """Formats output for RAG pipeline consumption.

    Produces structured text optimized for embedding and retrieval,
    with clear document boundaries and metadata annotations.

    Attributes:
        name: Display name.
        extension: File extension.
    """

    name = "RAG"
    extension = ".jsonl"

    def format_items(self, items: List[SourceItem]) -> str:
        """Format items as JSONL for RAG pipeline.

        Each item is formatted as a JSON Lines record with
        a dedicated 'text' field for embedding and a 'metadata'
        field for filtering/context.

        Args:
            items: List of SourceItem objects.

        Returns:
            JSONL formatted string (one JSON object per line).
        """
        lines = []
        timestamp = datetime.now(timezone.utc).isoformat()

        for item in items:
            # Build the text field for embedding
            text_parts = [item.title]

            if item.content:
                text_parts.append(item.content)

            # Add extra context from metadata
            if item.extra:
                extra_texts = []
                for key, value in item.extra.items():
                    if isinstance(value, str) and len(value) > 5:
                        extra_texts.append(f"{key}: {value}")
                    elif isinstance(value, (int, float)) and value > 0:
                        extra_texts.append(f"{key}: {value}")
                if extra_texts:
                    text_parts.append(" | ".join(extra_texts))

            text = "\n".join(text_parts)

            # Build the RAG document
            doc = {
                "id": f"{item.source.value}_{hash(item.url)}",
                "text": text,
                "title": item.title,
                "url": item.url,
                "source": item.source.value,
                "author": item.author,
                "score": item.score,
                "comments": item.comments,
                "created_at": item.created_at,
                "collected_at": timestamp,
                "metadata": {
                    "source_type": item.source.value,
                    "author": item.author,
                    "score": item.score,
                    "comments": item.comments,
                    **item.extra,
                },
            }

            lines.append(json.dumps(doc, ensure_ascii=False))

        return "\n".join(lines)

    def format_context(self, items: List[SourceItem], max_tokens: int = 4000) -> str:
        """Format items as LLM context text.

        Produces a clean text representation suitable for
        direct inclusion in an LLM prompt.

        Args:
            items: List of SourceItem objects.
            max_tokens: Approximate maximum token count.

        Returns:
            Formatted context string for LLM consumption.
        """
        parts = []
        current_length = 0

        parts.append(f"## Collected Data ({len(items)} items from various sources)\n")

        for i, item in enumerate(items, 1):
            # Estimate token count (rough: 1 token ~ 4 chars)
            entry = self._format_context_entry(i, item)
            entry_length = len(entry)

            if current_length + entry_length > max_tokens * 4:
                parts.append(f"\n[... {len(items) - i + 1} more items truncated ...]")
                break

            parts.append(entry)
            current_length += entry_length

        return "\n".join(parts)

    def _format_context_entry(self, index: int, item: SourceItem) -> str:
        """Format a single item as a context entry.

        Args:
            index: Item index number.
            item: SourceItem to format.

        Returns:
            Formatted context entry string.
        """
        lines = [
            f"### [{index}] {item.title}",
            f"Source: {item.source.value} | Author: {item.author or 'N/A'} | Score: {item.score}",
            f"URL: {item.url}",
        ]

        if item.content:
            lines.append(f"")
            lines.append(item.content[:500])

        if item.extra:
            extra_parts = []
            for key, value in item.extra.items():
                if value and str(value).strip():
                    extra_parts.append(f"{key}: {value}")
            if extra_parts:
                lines.append(f"")
                lines.append(f"Metadata: {', '.join(extra_parts)}")

        lines.append("")
        return "\n".join(lines)
