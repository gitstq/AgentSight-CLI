"""Tests for output formatters."""

import unittest

from agentsight.models import SourceItem, SourceType
from agentsight.formatters.json_fmt import JSONFormatter
from agentsight.formatters.markdown_fmt import MarkdownFormatter
from agentsight.formatters.csv_fmt import CSVFormatter
from agentsight.formatters.rag_fmt import RAGFormatter


def _make_test_items() -> list:
    """Create test SourceItem objects."""
    return [
        SourceItem(
            title="Test Repository",
            url="https://github.com/test/repo",
            content="A test repository for testing purposes.",
            author="testuser",
            source=SourceType.GITHUB,
            score=1500,
            comments=200,
            created_at="2024-01-15T10:30:00Z",
            extra={"language": "Python", "stars_today": 50},
        ),
        SourceItem(
            title="Another Project",
            url="https://github.com/another/project",
            content="Another interesting project.",
            author="anotheruser",
            source=SourceType.GITHUB,
            score=500,
            comments=50,
            created_at="2024-01-14T08:00:00Z",
            extra={"language": "Go", "stars_today": 10},
        ),
    ]


class TestJSONFormatter(unittest.TestCase):
    """Test cases for JSONFormatter."""

    def setUp(self):
        self.formatter = JSONFormatter()
        self.items = _make_test_items()

    def test_name(self):
        self.assertEqual(self.formatter.name, "JSON")

    def test_extension(self):
        self.assertEqual(self.formatter.extension, ".json")

    def test_format_items(self):
        result = self.formatter.format_items(self.items)
        self.assertIn("Test Repository", result)
        self.assertIn("https://github.com/test/repo", result)
        self.assertIn("testuser", result)

    def test_format_empty(self):
        result = self.formatter.format_items([])
        self.assertEqual(result, "[]")

    def test_format_single(self):
        result = self.formatter.format_single(self.items[0])
        self.assertIn("Test Repository", result)


class TestMarkdownFormatter(unittest.TestCase):
    """Test cases for MarkdownFormatter."""

    def setUp(self):
        self.formatter = MarkdownFormatter()
        self.items = _make_test_items()

    def test_name(self):
        self.assertEqual(self.formatter.name, "Markdown")

    def test_extension(self):
        self.assertEqual(self.formatter.extension, ".md")

    def test_format_items(self):
        result = self.formatter.format_items(self.items)
        self.assertIn("# Github", result)
        self.assertIn("Test Repository", result)
        self.assertIn("|", result)  # Table rows

    def test_format_empty(self):
        result = self.formatter.format_items([])
        self.assertIn("No Results", result)

    def test_contains_details(self):
        result = self.formatter.format_items(self.items)
        self.assertIn("## Details", result)


class TestCSVFormatter(unittest.TestCase):
    """Test cases for CSVFormatter."""

    def setUp(self):
        self.formatter = CSVFormatter()
        self.items = _make_test_items()

    def test_name(self):
        self.assertEqual(self.formatter.name, "CSV")

    def test_extension(self):
        self.assertEqual(self.formatter.extension, ".csv")

    def test_format_items(self):
        result = self.formatter.format_items(self.items)
        lines = result.strip().split("\n")
        # Header + 2 data rows
        self.assertEqual(len(lines), 3)
        self.assertIn("title", lines[0])
        self.assertIn("Test Repository", result)

    def test_format_empty(self):
        result = self.formatter.format_items([])
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 1)  # Only header


class TestRAGFormatter(unittest.TestCase):
    """Test cases for RAGFormatter."""

    def setUp(self):
        self.formatter = RAGFormatter()
        self.items = _make_test_items()

    def test_name(self):
        self.assertEqual(self.formatter.name, "RAG")

    def test_extension(self):
        self.assertEqual(self.formatter.extension, ".jsonl")

    def test_format_items(self):
        result = self.formatter.format_items(self.items)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 2)

        # Each line should be valid JSON
        import json
        for line in lines:
            data = json.loads(line)
            self.assertIn("id", data)
            self.assertIn("text", data)
            self.assertIn("metadata", data)

    def test_format_context(self):
        result = self.formatter.format_context(self.items, max_tokens=1000)
        self.assertIn("Collected Data", result)
        self.assertIn("Test Repository", result)

    def test_format_empty(self):
        result = self.formatter.format_items([])
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
