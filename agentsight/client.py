"""HTTP client with rate limiting, retry logic, and caching support.

Provides a robust HTTP client wrapper around requests library
with built-in rate limiting, automatic retries, and cache integration.
"""

import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .cache import CacheManager
from .config import Config


class RateLimiter:
    """Simple rate limiter using a token bucket approach.

    Ensures a minimum delay between requests to avoid overwhelming servers.

    Attributes:
        min_delay: Minimum seconds between requests.
        _last_request_time: Timestamp of the last request.
    """

    def __init__(self, min_delay: float = 1.0):
        """Initialize the rate limiter.

        Args:
            min_delay: Minimum delay between requests in seconds.
        """
        self.min_delay = min_delay
        self._last_request_time: float = 0

    def wait(self) -> None:
        """Wait if necessary to respect the rate limit."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            time.sleep(sleep_time)
        self._last_request_time = time.time()


class HTTPClient:
    """HTTP client with rate limiting, retries, and caching.

    Wraps the requests library with additional features:
    - Automatic retry on failure with exponential backoff
    - Rate limiting to avoid server bans
    - Response caching to avoid redundant requests
    - Configurable timeouts and headers

    Attributes:
        config: Configuration instance.
        cache: Cache manager instance.
        rate_limiter: Rate limiter instance.
        session: Underlying requests Session.
    """

    def __init__(self, config: Optional[Config] = None, cache: Optional[CacheManager] = None):
        """Initialize the HTTP client.

        Args:
            config: Configuration instance. Uses defaults if not provided.
            cache: Cache manager instance. Creates new one if not provided.
        """
        self.config = config or Config()
        self.cache = cache or CacheManager(self.config)
        self.rate_limiter = RateLimiter(self.config.rate_limit_delay)

        # Create a session with retry strategy
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests Session with retry adapter.

        Returns:
            Configured requests Session.
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/json,application/xhtml+xml,*/*",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
        })

        return session

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Perform a GET request with rate limiting, retry, and caching.

        Args:
            url: The URL to request.
            params: Optional query parameters.
            headers: Optional additional headers.
            use_cache: Whether to use caching for this request.
            timeout: Optional request timeout override.

        Returns:
            Response text if successful, None otherwise.
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(url, params)
            if cached is not None:
                return cached.get("text")

        # Apply rate limiting
        self.rate_limiter.wait()

        # Prepare request kwargs
        request_kwargs: Dict[str, Any] = {
            "timeout": timeout or self.config.request_timeout,
        }
        if params:
            request_kwargs["params"] = params
        if headers:
            request_kwargs["headers"] = headers

        # Proxy configuration
        proxies = None
        if self.config.proxy:
            proxies = {
                "http": self.config.proxy,
                "https": self.config.proxy,
            }
            request_kwargs["proxies"] = proxies

        # SSL verification
        request_kwargs["verify"] = self.config.verify_ssl

        try:
            response = self.session.get(url, **request_kwargs)
            response.raise_for_status()

            # Determine encoding from response
            response.encoding = response.apparent_encoding or "utf-8"
            text = response.text

            # Store in cache
            if use_cache:
                self.cache.set(url, {"text": text}, params)

            return text

        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.HTTPError:
            return None
        except requests.exceptions.RequestException:
            return None

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        timeout: Optional[int] = None,
    ) -> Optional[Any]:
        """Perform a GET request and parse JSON response.

        Args:
            url: The URL to request.
            params: Optional query parameters.
            headers: Optional additional headers.
            use_cache: Whether to use caching for this request.
            timeout: Optional request timeout override.

        Returns:
            Parsed JSON data if successful, None otherwise.
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(url, params)
            if cached is not None and "json" in cached:
                return cached["json"]

        # Apply rate limiting
        self.rate_limiter.wait()

        # Prepare request kwargs
        request_kwargs: Dict[str, Any] = {
            "timeout": timeout or self.config.request_timeout,
        }
        if params:
            request_kwargs["params"] = params
        if headers:
            request_kwargs["headers"] = headers

        # Proxy configuration
        proxies = None
        if self.config.proxy:
            proxies = {
                "http": self.config.proxy,
                "https": self.config.proxy,
            }
            request_kwargs["proxies"] = proxies

        request_kwargs["verify"] = self.config.verify_ssl

        try:
            response = self.session.get(url, **request_kwargs)
            response.raise_for_status()
            data = response.json()

            # Store in cache
            if use_cache:
                self.cache.set(url, {"json": data}, params)

            return data

        except (requests.exceptions.RequestException, ValueError):
            return None

    def close(self) -> None:
        """Close the underlying session and release resources."""
        self.session.close()

    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
