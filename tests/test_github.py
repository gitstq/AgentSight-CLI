"""Tests for GitHub Trending source collector."""

import unittest
from unittest.mock import MagicMock, patch

from agentsight.models import SourceItem, SourceType
from agentsight.sources.github import GitHubSource


class TestGitHubSource(unittest.TestCase):
    """Test cases for GitHubSource."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = GitHubSource()

    def tearDown(self):
        """Clean up after tests."""
        self.source.close()

    def test_source_properties(self):
        """Test that source has correct properties."""
        self.assertEqual(self.source.name, "GitHub Trending")
        self.assertEqual(self.source.source_type, SourceType.GITHUB)
        self.assertEqual(self.source.base_url, "https://github.com/trending")

    def test_parse_number_plain(self):
        """Test parsing plain number strings."""
        self.assertEqual(self.source._parse_number("12345"), 12345)
        self.assertEqual(self.source._parse_number("1,234"), 1234)

    def test_parse_number_k_suffix(self):
        """Test parsing number strings with 'k' suffix."""
        self.assertEqual(self.source._parse_number("1.5k"), 1500)
        self.assertEqual(self.source._parse_number("10k"), 10000)
        self.assertEqual(self.source._parse_number("0.5k"), 500)

    def test_parse_number_m_suffix(self):
        """Test parsing number strings with 'm' suffix."""
        self.assertEqual(self.source._parse_number("1.2m"), 1200000)
        self.assertEqual(self.source._parse_number("5m"), 5000000)

    def test_parse_number_empty(self):
        """Test parsing empty or invalid strings."""
        self.assertEqual(self.source._parse_number(""), 0)
        self.assertEqual(self.source._parse_number("abc"), 0)

    def test_fetch_returns_list(self):
        """Test that fetch returns a list."""
        # Mock the HTTP client to return None (no network)
        self.source.client.get = MagicMock(return_value=None)
        items = self.source.fetch(limit=5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_search_returns_list(self):
        """Test that search returns a list."""
        self.source.client.get = MagicMock(return_value=None)
        items = self.source.search("python", limit=5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_parse_article_none(self):
        """Test that parsing None returns None."""
        result = self.source._parse_article(None)
        self.assertIsNone(result)

    def test_source_repr(self):
        """Test source string representation."""
        repr_str = repr(self.source)
        self.assertIn("GitHubSource", repr_str)
        self.assertIn("GitHub Trending", repr_str)


if __name__ == "__main__":
    unittest.main()
