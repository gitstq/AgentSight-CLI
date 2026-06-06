"""CSV output formatter.

Formats SourceItem data as CSV for spreadsheet consumption.
"""

import csv
import io
from typing import List

from ..models import SourceItem
from .base import BaseFormatter


class CSVFormatter(BaseFormatter):
    """Formats output as CSV.

    Produces CSV data with headers suitable for import into
    spreadsheet applications like Excel, Google Sheets, etc.

    Attributes:
        name: Display name.
        extension: File extension.
    """

    name = "CSV"
    extension = ".csv"

    # Column headers for the CSV output
    HEADERS = [
        "title", "url", "content", "author", "source",
        "score", "comments", "created_at",
    ]

    def format_items(self, items: List[SourceItem]) -> str:
        """Format items as CSV.

        Args:
            items: List of SourceItem objects.

        Returns:
            CSV formatted string.
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header
        writer.writerow(self.HEADERS)

        # Write data rows
        for item in items:
            row = [
                item.title,
                item.url,
                item.content[:500] if item.content else "",
                item.author,
                item.source.value,
                item.score,
                item.comments,
                item.created_at,
            ]
            writer.writerow(row)

        return output.getvalue()
