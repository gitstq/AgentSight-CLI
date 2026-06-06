"""Tests for cache manager."""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from agentsight.cache import CacheManager
from agentsight.config import Config


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager."""

    def setUp(self):
        """Set up a temporary cache directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        config = Config()
        config.set("cache_dir", self.temp_dir)
        config.set("cache_ttl", 2)  # Short TTL for testing
        self.cache = CacheManager(config)

    def tearDown(self):
        """Clean up temporary cache directory."""
        # Clear cache and remove temp dir
        self.cache.clear()
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    def test_cache_enabled(self):
        """Test that cache is enabled by default."""
        self.assertTrue(self.cache.enabled)

    def test_set_and_get(self):
        """Test basic set and get operations."""
        self.cache.set("https://example.com", {"text": "hello"})
        result = self.cache.get("https://example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "hello")

    def test_get_miss(self):
        """Test that get returns None for missing keys."""
        result = self.cache.get("https://nonexistent.com")
        self.assertIsNone(result)

    def test_set_with_params(self):
        """Test caching with URL parameters."""
        self.cache.set("https://example.com/api", {"data": 1}, params={"page": 1})
        result = self.cache.get("https://example.com/api", params={"page": 1})
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], 1)

    def test_different_params_different_keys(self):
        """Test that different params produce different cache keys."""
        self.cache.set("https://example.com/api", {"page": 1}, params={"p": 1})
        self.cache.set("https://example.com/api", {"page": 2}, params={"p": 2})
        result1 = self.cache.get("https://example.com/api", params={"p": 1})
        result2 = self.cache.get("https://example.com/api", params={"p": 2})
        self.assertEqual(result1["page"], 1)
        self.assertEqual(result2["page"], 2)

    def test_cache_expiry(self):
        """Test that cache entries expire after TTL."""
        self.cache.set("https://example.com/expiring", {"text": "temp"})
        result = self.cache.get("https://example.com/expiring")
        self.assertIsNotNone(result)

        # Wait for expiry
        time.sleep(3)
        result = self.cache.get("https://example.com/expiring")
        self.assertIsNone(result)

    def test_invalidate(self):
        """Test cache invalidation."""
        self.cache.set("https://example.com/invalid", {"text": "data"})
        result = self.cache.get("https://example.com/invalid")
        self.assertIsNotNone(result)

        invalidated = self.cache.invalidate("https://example.com/invalid")
        self.assertTrue(invalidated)

        result = self.cache.get("https://example.com/invalid")
        self.assertIsNone(result)

    def test_invalidate_miss(self):
        """Test invalidating a non-existent key."""
        invalidated = self.cache.invalidate("https://nonexistent.com")
        self.assertFalse(invalidated)

    def test_clear(self):
        """Test clearing all cache entries."""
        self.cache.set("https://example.com/1", {"text": "a"})
        self.cache.set("https://example.com/2", {"text": "b"})
        self.cache.set("https://example.com/3", {"text": "c"})

        count = self.cache.clear()
        self.assertEqual(count, 3)

        self.assertIsNone(self.cache.get("https://example.com/1"))
        self.assertIsNone(self.cache.get("https://example.com/2"))
        self.assertIsNone(self.cache.get("https://example.com/3"))

    def test_clear_empty(self):
        """Test clearing an empty cache."""
        count = self.cache.clear()
        self.assertEqual(count, 0)

    def test_get_stats(self):
        """Test cache statistics."""
        self.cache.set("https://example.com/stats", {"text": "data"})
        stats = self.cache.get_stats()

        self.assertTrue(stats["enabled"])
        self.assertEqual(stats["entry_count"], 1)
        self.assertGreater(stats["total_size_bytes"], 0)
        self.assertIn("cache_dir", stats)

    def test_disabled_cache(self):
        """Test that disabled cache doesn't store data."""
        config = Config()
        config.set("cache_dir", self.temp_dir)
        config.set("cache_enabled", False)
        disabled_cache = CacheManager(config)

        disabled_cache.set("https://example.com/disabled", {"text": "nope"})
        result = disabled_cache.get("https://example.com/disabled")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
