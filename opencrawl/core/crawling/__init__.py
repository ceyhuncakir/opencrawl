"""Crawling module for OpenCrawl.

This module provides high-performance async web crawling functionality
using aiohttp and uvloop.
"""

from .base import BaseCrawler
from .structures import CrawlerConfig, CrawlRequest, CrawlResponse
from .crawler import AsyncCrawler

__all__ = [
    "AsyncCrawler",
    "BaseCrawler",
    "CrawlerConfig",
    "CrawlRequest",
    "CrawlResponse",
]
