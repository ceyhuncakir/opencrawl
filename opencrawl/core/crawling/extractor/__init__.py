"""Content extraction strategies for web crawling.

This module provides different strategies for extracting content from web pages:
- HTMLExtractor: Full HTML with optional cleanup
- ContentExtractor: Clean text content only
- MarkdownExtractor: Convert to Markdown format
"""

from .base import BaseExtractor
from .content import ContentExtractor
from .html import HTMLExtractor
from .markdown import MarkdownExtractor
from .structures import (
    ExtractionConfig,
    ExtractionType,
    ExtractedContent,
    RawResponse,
)

__all__ = [
    "BaseExtractor",
    "HTMLExtractor",
    "ContentExtractor",
    "MarkdownExtractor",
    "ExtractionConfig",
    "ExtractionType",
    "ExtractedContent",
    "RawResponse",
]
