"""Crawling module for OpenCrawl.

This module provides high-performance async web crawling functionality
using aiohttp and uvloop, along with various content extraction strategies.
"""

from .base import BaseCrawler
from .proxies import Proxies
from .structures import CrawlerConfig, CrawlRequest, CrawlResponse
from .crawler import AsyncCrawler
from .extractor import (
    BaseExtractor,
    ContentExtractor,
    HTMLExtractor,
    MarkdownExtractor,
    ExtractionConfig,
    ExtractionType,
    ExtractedContent,
)

__all__ = [
    "AsyncCrawler",
    "BaseCrawler",
    "CrawlerConfig",
    "CrawlRequest",
    "CrawlResponse",
    "Proxies",
    "BaseExtractor",
    "ContentExtractor",
    "HTMLExtractor",
    "MarkdownExtractor",
    "ExtractionConfig",
    "ExtractionType",
    "ExtractedContent",
]
