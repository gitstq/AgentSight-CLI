"""Tests for Hacker News source collector."""

import unittest
from unittest.mock import MagicMock

from agentsight.models import SourceType
from agentsight.sources.hackernews import HackerNewsSource


class TestHackerNewsSource(unittest.TestCase):
    """Test cases for HackerNewsSource."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = HackerNewsSource()

    def tearDown(self):
        """Clean up after tests."""
        self.source.close()

    def test_source_properties(self):
        """Test that source has correct properties."""
        self.assertEqual(self.source.name, "Hacker News")
        self.assertEqual(self.source.source_type, SourceType.HACKERNEWS)
        self.assertIn("firebaseio.com", self.source.base_url)

    def test_fetch_returns_list(self):
        """Test that fetch returns a list."""
        self.source.client.get_json = MagicMock(return_value=None)
        items = self.source.fetch(limit=5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_fetch_with_story_type(self):
        """Test fetching different story types."""
        self.source.client.get_json = MagicMock(return_value=None)
        items = self.source.fetch(limit=5, story_type="new")
        self.assertIsInstance(items, list)

    def test_search_returns_list(self):
        """Test that search returns a list."""
        self.source.client.get_json = MagicMock(return_value=None)
        items = self.source.search("python", limit=5)
        self.assertIsInstance(items, list)

    def test_fetch_story_none_data(self):
        """Test fetching a story with no data returns None."""
        self.source.client.get_json = MagicMock(return_value=None)
        result = self.source._fetch_story(12345)
        self.assertIsNone(result)

    def test_fetch_story_deleted(self):
        """Test that deleted stories return None."""
        self.source.client.get_json = MagicMock(return_value={
            "deleted": True,
            "title": "Test",
        })
        result = self.source._fetch_story(12345)
        self.assertIsNone(result)

    def test_fetch_story_dead(self):
        """Test that dead stories return None."""
        self.source.client.get_json = MagicMock(return_value={
            "dead": True,
            "title": "Test",
        })
        result = self.source._fetch_story(12345)
        self.assertIsNone(result)

    def test_story_types(self):
        """Test that all story types are defined."""
        expected_types = {"top", "new", "best", "ask", "show", "job"}
        self.assertEqual(set(self.source.STORY_TYPES.keys()), expected_types)


if __name__ == "__main__":
    unittest.main()
