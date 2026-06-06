"""Local cache management for AgentSight-CLI.

Provides file-based caching to avoid redundant HTTP requests
and improve response times for repeated queries.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Config


class CacheManager:
    """Manages local file-based cache for HTTP responses.

    Cache files are stored as JSON with metadata including
    creation timestamp and TTL information.

    Attributes:
        cache_dir: Directory where cache files are stored.
        ttl: Time-to-live for cache entries in seconds.
        enabled: Whether caching is enabled.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the cache manager.

        Args:
            config: Configuration instance. Uses defaults if not provided.
        """
        self._config = config or Config()
        self.cache_dir = Path(self._config.cache_dir)
        self.ttl = self._config.cache_ttl
        self.enabled = self._config.cache_enabled

        # Ensure cache directory exists
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key from URL and parameters.

        Args:
            url: The request URL.
            params: Optional query parameters.

        Returns:
            A hash string used as the cache filename.
        """
        raw = url
        if params:
            # Sort params to ensure consistent keys
            sorted_params = json.dumps(params, sort_keys=True)
            raw = f"{url}?{sorted_params}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _cache_path(self, key: str) -> Path:
        """Get the full file path for a cache key.

        Args:
            key: The cache key.

        Returns:
            Path to the cache file.
        """
        return self.cache_dir / f"{key}.json"

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached response data.

        Args:
            url: The request URL.
            params: Optional query parameters.

        Returns:
            Cached data dict if found and not expired, None otherwise.
        """
        if not self.enabled:
            return None

        key = self._make_key(url, params)
        path = self._cache_path(key)

        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                cache_entry = json.load(f)

            # Check if cache has expired
            cached_at = cache_entry.get("cached_at", 0)
            if time.time() - cached_at > self.ttl:
                # Cache expired, remove the file
                path.unlink(missing_ok=True)
                return None

            return cache_entry.get("data")
        except (json.JSONDecodeError, IOError, KeyError):
            # Corrupted cache file, remove it
            path.unlink(missing_ok=True)
            return None

    def set(self, url: str, data: Any, params: Optional[Dict[str, Any]] = None) -> None:
        """Store data in cache.

        Args:
            url: The request URL.
            data: The data to cache.
            params: Optional query parameters.
        """
        if not self.enabled:
            return

        key = self._make_key(url, params)
        path = self._cache_path(key)

        cache_entry = {
            "cached_at": time.time(),
            "ttl": self.ttl,
            "url": url,
            "data": data,
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cache_entry, f, ensure_ascii=False)
        except IOError:
            # Fail silently if cache write fails
            pass

    def invalidate(self, url: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Invalidate a specific cache entry.

        Args:
            url: The request URL.
            params: Optional query parameters.

        Returns:
            True if the entry was removed, False otherwise.
        """
        key = self._make_key(url, params)
        path = self._cache_path(key)

        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            The number of cache entries that were removed.
        """
        count = 0
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    count += 1
                except IOError:
                    pass
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics.
        """
        total_size = 0
        entry_count = 0
        oldest_entry = float("inf")
        newest_entry = 0

        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    stat = cache_file.stat()
                    total_size += stat.st_size
                    entry_count += 1
                    mtime = stat.st_mtime
                    if mtime < oldest_entry:
                        oldest_entry = mtime
                    if mtime > newest_entry:
                        newest_entry = mtime
                except IOError:
                    pass

        return {
            "enabled": self.enabled,
            "entry_count": entry_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_entry": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(oldest_entry)) if oldest_entry != float("inf") else "N/A",
            "newest_entry": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(newest_entry)) if entry_count > 0 else "N/A",
            "ttl_seconds": self.ttl,
            "cache_dir": str(self.cache_dir),
        }
