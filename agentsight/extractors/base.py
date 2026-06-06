"""Base class for content extractors.

Provides the interface for extracting structured content
from web pages and other data sources.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..client import HTTPClient
from ..config import Config
from ..models import ExtractedContent


class BaseExtractor(ABC):
    """Abstract base class for content extractors.

    All extractor implementations must inherit from this class
    and implement the extract method.

    Attributes:
        client: HTTP client instance for making requests.
        config: Configuration instance.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the extractor.

        Args:
            config: Optional configuration instance.
        """
        self.config = config or Config()
        self.client = HTTPClient(self.config)

    @abstractmethod
    def extract(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from a URL.

        Args:
            url: The URL to extract content from.

        Returns:
            ExtractedContent object if successful, None otherwise.
        """
        pass

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.client.close()

    def __enter__(self) -> "BaseExtractor":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: any, exc_val: any, exc_tb: any) -> None:
        """Context manager exit."""
        self.close()
