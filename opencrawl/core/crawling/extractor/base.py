"""Base extractor class for content extraction."""

from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from .structures import ExtractionConfig, ExtractedContent, RawResponse


class BaseExtractor(ABC):
    """Abstract base class for content extractors.
    
    Provides common functionality for different extraction strategies.
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize the extractor.
        
        Args:
            config: Extraction configuration. If None, uses default config.
        """
        self.config = config or ExtractionConfig()
    
    @abstractmethod
    def extract(self, response: RawResponse) -> ExtractedContent:
        """Extract content from a raw response.
        
        Args:
            response: The raw response to extract from
            
        Returns:
            Extracted content
        """
        pass
    
    def _parse_html(self, html: str) -> HTMLParser:
        """Parse HTML content using Selectolax.
        
        Args:
            html: HTML content to parse
            
        Returns:
            Parsed HTMLParser object
        """
        return HTMLParser(html)
    
    def _clean_tree(self, tree: HTMLParser, base_url: str = "") -> HTMLParser:
        """Clean HTML tree by removing unwanted elements.
        
        Args:
            tree: HTMLParser object to clean
            base_url: Base URL for resolving relative links
            
        Returns:
            Cleaned HTMLParser object
        """
        # Remove scripts
        if self.config.remove_scripts:
            [node.decompose() for node in tree.css("script")]
        
        # Remove styles
        if self.config.remove_styles:
            [node.decompose() for node in tree.css("style")]
        
        # Remove comments
        if self.config.remove_comments:
            for node in tree.root.traverse():
                if node.tag == "-comment":
                    node.decompose()
        
        # Remove navigation
        if self.config.remove_nav:
            [node.decompose() for node in tree.css("nav, [role='navigation']")]
        
        # Remove footer
        if self.config.remove_footer:
            [node.decompose() for node in tree.css("footer")]
        
        # Remove header
        if self.config.remove_header:
            [node.decompose() for node in tree.css("header")]
        
        return tree
    
    def _extract_metadata(self, tree: HTMLParser) -> dict[str, str]:
        """Extract metadata from HTML.
        
        Args:
            tree: HTMLParser object
            
        Returns:
            Dictionary of metadata
        """
        if not self.config.extract_metadata:
            return {}
        
        metadata = {}
        
        # Extract title
        title_tag = tree.css_first("title")
        if title_tag:
            metadata["title"] = title_tag.text(strip=True)
        
        # Extract meta tags
        meta_selectors = {
            "description": "meta[name='description']",
            "keywords": "meta[name='keywords']",
            "author": "meta[name='author']",
            "og:title": "meta[property='og:title']",
            "og:description": "meta[property='og:description']",
            "og:image": "meta[property='og:image']",
        }
        
        for key, selector in meta_selectors.items():
            tag = tree.css_first(selector)
            if tag and (content := tag.attributes.get("content")):
                metadata[key] = content
        
        return metadata
    
    def _extract_links(self, tree: HTMLParser, base_url: str = "") -> list[str]:
        """Extract all links from HTML.
        
        Args:
            tree: HTMLParser object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        if not self.config.preserve_links:
            return []
        
        links = [
            urljoin(base_url, href)
            for a in tree.css("a[href]")
            if (href := a.attributes.get("href"))
        ]
        
        return list(set(links))  # Remove duplicates
    
    def _extract_images(self, tree: HTMLParser, base_url: str = "") -> list[str]:
        """Extract all image URLs from HTML.
        
        Args:
            tree: HTMLParser object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute image URLs
        """
        if not self.config.preserve_images:
            return []
        
        images = [
            urljoin(base_url, src)
            for img in tree.css("img[src]")
            if (src := img.attributes.get("src"))
        ]
        
        return list(set(images))  # Remove duplicates
