"""Output formatters package."""

from .base import BaseFormatter
from .json_fmt import JSONFormatter
from .markdown_fmt import MarkdownFormatter
from .csv_fmt import CSVFormatter
from .rag_fmt import RAGFormatter

# Registry of all available formatters
FORMATTER_REGISTRY = {
    "json": JSONFormatter,
    "markdown": MarkdownFormatter,
    "csv": CSVFormatter,
    "rag": RAGFormatter,
}


def get_formatter(name: str) -> "BaseFormatter":
    """Get a formatter instance by name.

    Args:
        name: The formatter name (e.g., 'json', 'markdown').

    Returns:
        An instance of the requested formatter.

    Raises:
        ValueError: If the formatter name is not recognized.
    """
    if name not in FORMATTER_REGISTRY:
        available = ", ".join(sorted(FORMATTER_REGISTRY.keys()))
        raise ValueError(f"Unknown formatter '{name}'. Available formatters: {available}")
    return FORMATTER_REGISTRY[name]()


__all__ = [
    "BaseFormatter",
    "JSONFormatter",
    "MarkdownFormatter",
    "CSVFormatter",
    "RAGFormatter",
    "FORMATTER_REGISTRY",
    "get_formatter",
]
