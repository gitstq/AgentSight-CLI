"""JSON output formatter.

Formats SourceItem data as JSON for programmatic consumption.
"""

import json
from typing import List

from ..models import SourceItem
from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Formats output as JSON.

    Produces a JSON array of objects, each representing a SourceItem
    with all its fields and metadata.

    Attributes:
        name: Display name.
        extension: File extension.
    """

    name = "JSON"
    extension = ".json"

    def format_items(self, items: List[SourceItem]) -> str:
        """Format items as a JSON array.

        Args:
            items: List of SourceItem objects.

        Returns:
            JSON formatted string.
        """
        data = [item.to_dict() for item in items]
        return json.dumps(data, ensure_ascii=False, indent=2)
