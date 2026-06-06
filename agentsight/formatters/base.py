"""Base class for output formatters.

Provides the interface for formatting SourceItem data
into various output formats.
"""

from abc import ABC, abstractmethod
from typing import List

from ..models import SourceItem


class BaseFormatter(ABC):
    """Abstract base class for output formatters.

    All formatter implementations must inherit from this class
    and implement the format_items method.

    Attributes:
        name: Display name of the formatter.
        extension: Default file extension for this format.
    """

    name: str = "base"
    extension: str = ".txt"

    @abstractmethod
    def format_items(self, items: List[SourceItem]) -> str:
        """Format a list of SourceItems into a string.

        Args:
            items: List of SourceItem objects to format.

        Returns:
            Formatted string output.
        """
        pass

    def format_single(self, item: SourceItem) -> str:
        """Format a single SourceItem.

        Args:
            item: A single SourceItem to format.

        Returns:
            Formatted string output.
        """
        return self.format_items([item])
