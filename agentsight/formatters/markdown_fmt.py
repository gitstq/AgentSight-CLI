"""Markdown output formatter.

Formats SourceItem data as Markdown for human-readable output
and documentation purposes.
"""

from typing import List

from ..models import SourceItem
from .base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Formats output as Markdown.

    Produces a Markdown document with a table of items
    including titles, links, scores, and other metadata.

    Attributes:
        name: Display name.
        extension: File extension.
    """

    name = "Markdown"
    extension = ".md"

    def format_items(self, items: List[SourceItem]) -> str:
        """Format items as a Markdown document.

        Args:
            items: List of SourceItem objects.

        Returns:
            Markdown formatted string.
        """
        if not items:
            return "# No Results\n\nNo items found."

        lines = []

        # Header
        source_name = items[0].source.value.capitalize()
        lines.append(f"# {source_name} Results")
        lines.append(f"")
        lines.append(f"Total items: **{len(items)}**")
        lines.append("")

        # Table header
        lines.append("| # | Title | Author | Score | Comments | Link |")
        lines.append("|---|-------|--------|-------|----------|------|")

        # Table rows
        for i, item in enumerate(items, 1):
            title = self._escape_markdown(item.title[:80])
            author = self._escape_markdown(item.author[:30]) if item.author else "-"
            score = self._format_number(item.score)
            comments = self._format_number(item.comments)
            link = f"[Link]({item.url})"

            lines.append(f"| {i} | {title} | {author} | {score} | {comments} | {link} |")

        lines.append("")

        # Detailed items
        lines.append("---")
        lines.append("")
        lines.append("## Details")
        lines.append("")

        for i, item in enumerate(items, 1):
            lines.append(f"### {i}. {self._escape_markdown(item.title)}")
            lines.append("")

            if item.content:
                lines.append(f"> {self._escape_markdown(item.content[:200])}")
                lines.append("")

            lines.append(f"- **Author**: {self._escape_markdown(item.author) or 'N/A'}")
            lines.append(f"- **URL**: {item.url}")
            lines.append(f"- **Score**: {self._format_number(item.score)}")
            lines.append(f"- **Comments**: {self._format_number(item.comments)}")

            if item.created_at:
                lines.append(f"- **Date**: {item.created_at}")

            # Extra metadata
            if item.extra:
                for key, value in item.extra.items():
                    if value and str(value).strip():
                        lines.append(f"- **{key}**: {value}")

            lines.append("")

        return "\n".join(lines)

    def _escape_markdown(self, text: str) -> str:
        """Escape special Markdown characters in text.

        Args:
            text: Raw text string.

        Returns:
            Escaped text string.
        """
        if not text:
            return ""
        # Escape pipe character in table cells
        text = text.replace("|", "\\|")
        # Escape newlines
        text = text.replace("\n", " ")
        return text.strip()

    def _format_number(self, number: int) -> str:
        """Format a number with comma separators.

        Args:
            number: Integer to format.

        Returns:
            Formatted number string.
        """
        if number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}K"
        return str(number)
