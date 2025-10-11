"""Data structures for extraction strategies."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExtractionType(Enum):
    """Types of content extraction strategies."""
    
    HTML = "html"
    CONTENT = "content"
    MARKDOWN = "markdown"
    STRUCTURED = "structured"


@dataclass
class RawResponse:
    """Raw response data for extraction.
    
    Simple structure to avoid circular imports with CrawlResponse.
    
    Attributes:
        url: The response URL
        text: HTML content as text
        status: HTTP status code
    """
    
    url: str
    text: str
    status: int = 200


@dataclass
class ExtractionConfig:
    """Configuration for content extraction.
    
    Attributes:
        remove_scripts: Remove script tags and their content
        remove_styles: Remove style tags and their content
        remove_comments: Remove HTML comments
        remove_nav: Remove navigation elements
        remove_footer: Remove footer elements
        remove_header: Remove header elements
        preserve_links: Keep link URLs in extracted content
        preserve_images: Keep image URLs in extracted content
        min_text_length: Minimum text length to consider (filter out short elements)
        extract_metadata: Extract page metadata (title, description, etc.)
    """
    
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_comments: bool = True
    remove_nav: bool = False
    remove_footer: bool = False
    remove_header: bool = False
    preserve_links: bool = True
    preserve_images: bool = True
    min_text_length: int = 10
    extract_metadata: bool = True


@dataclass
class ExtractedContent:
    """Represents extracted content from a web page.
    
    Attributes:
        content: The main extracted content
        metadata: Page metadata (title, description, keywords, etc.)
        links: List of extracted links
        images: List of extracted image URLs
        extraction_type: Type of extraction performed
        error: Error message if extraction failed
    """
    
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    links: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    extraction_type: ExtractionType = ExtractionType.CONTENT
    error: str | None = None
    
    @property
    def is_success(self) -> bool:
        """Check if extraction was successful."""
        return self.error is None and bool(self.content)
