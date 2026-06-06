"""Base class for all data source collectors.

Provides the interface and common functionality that all
data source implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..client import HTTPClient
from ..config import Config
from ..models import SourceItem, SourceType


class BaseSource(ABC):
    """Abstract base class for data source collectors.

    All data source implementations must inherit from this class
    and implement the fetch and search methods.

    Attributes:
        name: Human-readable name of the data source.
        source_type: The SourceType enum value for this source.
        base_url: The base URL for the data source.
        description: Brief description of the data source.
        client: HTTP client instance for making requests.
    """

    name: str = "base"
    source_type: SourceType = SourceType.GITHUB
    base_url: str = ""
    description: str = ""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the data source.

        Args:
            config: Optional configuration instance.
        """
        self.config = config or Config()
        self.client = HTTPClient(self.config)

    @abstractmethod
    def fetch(self, limit: int = 20) -> List[SourceItem]:
        """Fetch trending/popular items from the data source.

        Args:
            limit: Maximum number of items to fetch.

        Returns:
            List of SourceItem objects.
        """
        pass

    @abstractmethod
    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search for items matching a keyword.

        Args:
            keyword: The search keyword.
            limit: Maximum number of results to return.

        Returns:
            List of matching SourceItem objects.
        """
        pass

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.client.close()

    def __enter__(self) -> "BaseSource":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: any, exc_val: any, exc_tb: any) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the source."""
        return f"<{self.__class__.__name__}(name='{self.name}', url='{self.base_url}')>"
