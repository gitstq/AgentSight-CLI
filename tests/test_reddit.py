"""Tests for Reddit source collector."""

import unittest
from unittest.mock import MagicMock

from agentsight.models import SourceType
from agentsight.sources.reddit import RedditSource


class TestRedditSource(unittest.TestCase):
    """Test cases for RedditSource."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = RedditSource()

    def tearDown(self):
        """Clean up after tests."""
        self.source.close()

    def test_source_properties(self):
        """Test that source has correct properties."""
        self.assertEqual(self.source.name, "Reddit")
        self.assertEqual(self.source.source_type, SourceType.REDDIT)
        self.assertEqual(self.source.base_url, "https://old.reddit.com")

    def test_fetch_returns_list(self):
        """Test that fetch returns a list."""
        self.source.client.get = MagicMock(return_value=None)
        items = self.source.fetch(limit=5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_fetch_with_subreddit(self):
        """Test fetching from a specific subreddit."""
        self.source.client.get = MagicMock(return_value=None)
        items = self.source.fetch(limit=5, subreddit="python")
        self.assertIsInstance(items, list)
        # Verify the correct URL was called
        call_args = self.source.client.get.call_args
        self.assertIn("r/python", call_args[0][0])

    def test_search_returns_list(self):
        """Test that search returns a list."""
        self.source.client.get = MagicMock(return_value=None)
        items = self.source.search("python", limit=5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_parse_post_none(self):
        """Test that parsing None returns None."""
        result = self.source._parse_post(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
