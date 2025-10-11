"""High-performance async web crawler using aiohttp and uvloop."""

import asyncio
import logging
from typing import Optional

import aiohttp
import uvloop

from .proxies import Proxies
from .base import BaseCrawler
from .structures import CrawlerConfig, CrawlRequest, CrawlResponse
from .extractor import (
    BaseExtractor,
    ContentExtractor,
    HTMLExtractor,
    MarkdownExtractor,
    ExtractionType,
    RawResponse,
)

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
        self._proxies = Proxies(self.config.proxies)
        self._extractors = self._init_extractors()

    async def setup(self) -> None:
        """Set up the crawler session and resources."""
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

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
    
    def _init_extractors(self) -> dict[ExtractionType, BaseExtractor]:
        """Initialize extractors based on configuration.
        
        Returns:
            Dictionary mapping extraction types to extractor instances
        """
        extraction_config = self.config.extraction_config
        
        return {
            ExtractionType.HTML: HTMLExtractor(extraction_config),
            ExtractionType.CONTENT: ContentExtractor(extraction_config),
            ExtractionType.MARKDOWN: MarkdownExtractor(extraction_config),
        }
    
    def _get_extractor(self, extraction_type: Optional[ExtractionType]) -> Optional[BaseExtractor]:
        """Get the appropriate extractor for the given type.
        
        Args:
            extraction_type: Type of extraction to perform
            
        Returns:
            Extractor instance or None if no extraction requested
        """
        if not extraction_type:
            return None
        
        return self._extractors.get(extraction_type)

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
                proxy = self._proxies.rotate_proxy()

                # Make the request
                async with self._semaphore:
                    async with self._session.request(
                        method=request.method,
                        url=request.url,
                        headers=headers,
                        data=request.data,
                        params=request.params,
                        cookies=cookies,
                        proxy=proxy.url,
                        allow_redirects=self.config.follow_redirects,
                        max_redirects=self.config.max_redirects,
                    ) as response:
                    
                        content = await response.read()
                        text = await response.text(errors="replace")

                        crawl_response = CrawlResponse(
                            url=str(response.url),
                            status=response.status,
                            headers=dict(response.headers),
                            content=content,
                            text=text,
                            encoding=response.charset,
                            metadata=request.metadata,
                        )
                        
                        # Apply extraction if configured
                        extraction_type = request.extraction_strategy or self.config.extraction_strategy
                        if extraction_type:
                            extractor = self._get_extractor(extraction_type)
                            if extractor:
                                raw_response = RawResponse(
                                    url=crawl_response.url,
                                    text=crawl_response.text,
                                    status=crawl_response.status,
                                )

                                crawl_response.extracted = extractor.extract(raw_response)
                        
                        return crawl_response

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

    async def fetch_all(self, requests: list[CrawlRequest]) -> list[CrawlResponse]:
        """Fetch multiple URLs and return all responses.

        Args:
            requests: List of crawl requests to execute

        Returns:
            List of all crawl responses
        """
        tasks = [asyncio.create_task(self.fetch(request)) for request in requests]
        return await asyncio.gather(*tasks)
