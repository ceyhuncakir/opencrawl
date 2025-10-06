"""Base classes for web crawling."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from .structures import CrawlerConfig, CrawlRequest, CrawlResponse


class BaseCrawler(ABC):
    """Abstract base class for web crawlers.

    Provides a common interface for different crawler implementations.
    """

    def __init__(self, config: CrawlerConfig | None = None):
        """Initialize the crawler with configuration.

        Args:
            config: Crawler configuration. If None, uses default config.
        """
        self.config = config or CrawlerConfig()
        self._session = None
        self._semaphore = None

    @abstractmethod
    async def setup(self) -> None:
        """Set up the crawler (e.g., create session, initialize resources)."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources (e.g., close session)."""
        pass

    @abstractmethod
    async def fetch(self, request: CrawlRequest) -> CrawlResponse:
        """Fetch a single URL.

        Args:
            request: The crawl request to execute

        Returns:
            The crawl response
        """
        pass

    @abstractmethod
    async def fetch_many(
        self, requests: list[CrawlRequest]
    ) -> AsyncGenerator[CrawlResponse, None]:
        """Fetch multiple URLs concurrently.

        Args:
            requests: List of crawl requests to execute

        Yields:
            Crawl responses as they complete
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return False
