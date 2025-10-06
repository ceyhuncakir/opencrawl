"""High-performance async web crawler using aiohttp and uvloop."""

import asyncio
import logging
from typing import AsyncGenerator

import aiohttp
import uvloop

from .base import BaseCrawler
from .structures import CrawlerConfig, CrawlRequest, CrawlResponse

logger = logging.getLogger(__name__)


class AsyncCrawler(BaseCrawler):
    """High-performance async web crawler using aiohttp.

    Features:
        - Async/await with aiohttp for optimal performance
        - Configurable concurrency limits
        - Automatic retries with exponential backoff
        - Proxy support
        - Custom headers and cookies
        - SSL verification control

    Example:
        >>> config = CrawlerConfig(max_concurrent_requests=20)
        >>> async with AsyncCrawler(config) as crawler:
        ...     request = CrawlRequest(url="https://example.com")
        ...     response = await crawler.fetch(request)
        ...     print(response.text)
    """

    def __init__(self, config: CrawlerConfig | None = None):
        """Initialize the crawler.

        Args:
            config: Crawler configuration. If None, uses default config.
        """
        super().__init__(config)
        self._rate_limiter = None

        # Set up uvloop if configured
        if self.config.use_uvloop:
            try:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                logger.info("Using uvloop for enhanced performance")
            except ImportError:
                logger.warning("uvloop not available, using default event loop")

    async def setup(self) -> None:
        """Set up the crawler session and resources."""
        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)

        # Create connector with SSL settings
        connector = aiohttp.TCPConnector(
            limit=self.config.max_concurrent_requests,
            verify_ssl=self.config.verify_ssl,
        )

        # Create client session
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.config.headers,
            cookies=self.config.cookies,
        )

        # Set up semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

    async def cleanup(self) -> None:
        """Clean up the crawler session and resources."""
        if self._session:
            await self._session.close()
            self._session = None

        self._semaphore = None

    async def fetch(self, request: CrawlRequest) -> CrawlResponse:
        """Fetch a single URL with retries.

        Args:
            request: The crawl request to execute

        Returns:
            The crawl response
        """
        if not self._session:
            raise RuntimeError(
                "Crawler not set up. Use async context manager or call setup()"
            )

        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                # Merge request headers with config headers
                headers = {**self.config.headers, **request.headers}
                cookies = {**self.config.cookies, **request.cookies}

                # Prepare proxy
                proxy = self.config.proxy

                # Make the request
                async with self._semaphore:
                    async with self._session.request(
                        method=request.method,
                        url=request.url,
                        headers=headers,
                        data=request.data,
                        params=request.params,
                        cookies=cookies,
                        proxy=proxy,
                        allow_redirects=self.config.follow_redirects,
                        max_redirects=self.config.max_redirects,
                    ) as response:
                        content = await response.read()
                        text = await response.text(errors="replace")

                        return CrawlResponse(
                            url=str(response.url),
                            status=response.status,
                            headers=dict(response.headers),
                            content=content,
                            text=text,
                            encoding=response.charset,
                            metadata=request.metadata,
                        )

            except asyncio.TimeoutError as e:
                last_error = f"Timeout error: {e}"
                logger.warning(
                    f"Timeout for {request.url} (attempt {attempt + 1}/{self.config.max_retries})"
                )

            except aiohttp.ClientError as e:
                last_error = f"Client error: {e}"
                logger.warning(
                    f"Client error for {request.url} (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            except Exception as e:
                last_error = f"Unexpected error: {e}"
                logger.error(
                    f"Unexpected error for {request.url} (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            # Wait before retrying (exponential backoff)
            if attempt < self.config.max_retries - 1:
                wait_time = self.config.retry_delay * (2**attempt)
                await asyncio.sleep(wait_time)

        # All retries failed, return error response
        return CrawlResponse(
            url=request.url,
            status=0,
            headers={},
            content=b"",
            text="",
            metadata=request.metadata,
            error=last_error,
        )

    async def fetch_many(
        self, requests: list[CrawlRequest]
    ) -> AsyncGenerator[CrawlResponse, None]:
        """Fetch multiple URLs concurrently.

        Args:
            requests: List of crawl requests to execute

        Yields:
            Crawl responses as they complete
        """
        if not self._session:
            raise RuntimeError(
                "Crawler not set up. Use async context manager or call setup()"
            )

        # Create tasks for all requests
        tasks = [asyncio.create_task(self.fetch(request)) for request in requests]

        # Yield responses as they complete
        for coro in asyncio.as_completed(tasks):
            response = await coro
            yield response

    async def fetch_all(self, requests: list[CrawlRequest]) -> list[CrawlResponse]:
        """Fetch multiple URLs and return all responses.

        Args:
            requests: List of crawl requests to execute

        Returns:
            List of all crawl responses
        """

        task = [asyncio.create_task(self.fetch(request)) for request in requests]

        return [response.result() for response in task]
