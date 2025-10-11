"""OpenCrawl - High-performance web crawler and text generator.

This package provides:
- AsyncCrawler: High-performance async web crawling with aiohttp
- VLLMGenerator: Text generation using vLLM models

Examples:
    Using as a library::

        from opencrawl import AsyncCrawler, CrawlerConfig, CrawlRequest

        # Create crawler
        config = CrawlerConfig(max_concurrent_requests=20)
        async with AsyncCrawler(config) as crawler:
            request = CrawlRequest(url="https://example.com")
            response = await crawler.fetch(request)
            print(response.text)

    Using the CLI::

        $ opencrawl crawl https://example.com --output result.json
        $ opencrawl generate "Hello world" --model llama-2-7b
"""

from opencrawl.core.crawling import (
    AsyncCrawler,
    CrawlerConfig,
    CrawlRequest,
    CrawlResponse,
    ExtractionConfig,
    ExtractionType,
    ExtractedContent,
)
from opencrawl.core.model import (
    Model,
    ModelConfig,
    GenerationConfig,
    GenerationOutput,
    ChatMessage,
    Conversation,
)
from opencrawl.spider import Spider
from opencrawl.core import SpiderOutput

__version__ = "0.1.0"

__all__ = [
    # Crawling
    "AsyncCrawler",
    "CrawlerConfig",
    "CrawlRequest",
    "CrawlResponse",
    # Extraction
    "ExtractionConfig",
    "ExtractionType",
    "ExtractedContent",
    # Model
    "Model",
    "ModelConfig",
    "GenerationConfig",
    "GenerationOutput",
    "ChatMessage",
    "Conversation",
    # Spider
    "Spider",
    "SpiderOutput",
]

