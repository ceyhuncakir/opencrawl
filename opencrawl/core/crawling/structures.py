"""Configuration data classes for the crawler."""

from dataclasses import dataclass, field
from typing import Any, Optional

from .extractor.structures import ExtractionConfig, ExtractionType, ExtractedContent


@dataclass
class CrawlerConfig:
    """Configuration for the web crawler.

    Attributes:
        max_concurrent_requests: Maximum number of concurrent requests
        request_timeout: Timeout for each request in seconds
        max_retries: Maximum number of retries for failed requests
        retry_delay: Delay between retries in seconds
        headers: Default headers to send with requests
        follow_redirects: Whether to follow redirects
        verify_ssl: Whether to verify SSL certificates
        max_redirects: Maximum number of redirects to follow
        user_agent: User agent string to use
        proxy: Proxy URL to use for requests
        cookies: Default cookies to send with requests
        verbose: Whether to enable verbose logging
        extraction_strategy: Content extraction strategy (html, content, markdown, or None)
        extraction_config: Configuration for content extraction
    """
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    headers: dict[str, str] = field(default_factory=dict)
    follow_redirects: bool = True
    verify_ssl: bool = True
    max_redirects: int = 10
    user_agent: str = "OpenCrawl/0.1.0"
    proxies: str = field(default_factory=str)
    cookies: dict[str, str] = field(default_factory=dict)
    verbose: bool = False
    extraction_strategy: Optional[ExtractionType] = None
    extraction_config: Optional[ExtractionConfig] = None

    def __post_init__(self):
        """Set default user agent if not provided in headers."""
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = self.user_agent
        
        # Set default extraction config if strategy is set but config is not
        if self.extraction_strategy and not self.extraction_config:
            self.extraction_config = ExtractionConfig()


@dataclass
class CrawlRequest:
    """Represents a single crawl request.

    Attributes:
        url: URL to crawl
        method: HTTP method to use
        headers: Request-specific headers
        data: Request body data
        params: URL query parameters
        cookies: Request-specific cookies
        metadata: Additional metadata for the request
        extraction_strategy: Override extraction strategy for this request
    """

    url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    data: dict[str, Any] | str | bytes | None = None
    params: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_strategy: Optional[ExtractionType] = None


@dataclass
class CrawlResponse:
    """Represents a crawl response.

    Attributes:
        url: The final URL (after redirects)
        status: HTTP status code
        headers: Response headers
        content: Response content as bytes
        text: Response content as text
        encoding: Response encoding
        metadata: Metadata from the request
        error: Error message if the request failed
        extracted: Extracted content (if extraction was enabled)
    """

    url: str
    status: int
    headers: dict[str, str]
    content: bytes
    text: str
    encoding: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    extracted: Optional[ExtractedContent] = None

    @property
    def is_success(self) -> bool:
        """Check if the response was successful."""
        return 200 <= self.status < 300 and self.error is None


@dataclass
class Proxy:
    """Represents a proxy.

    Attributes:
        url: Proxy URL
        username: Proxy username
        password: Proxy password
    """

    url: str