"""Content-only extraction strategy."""

from .base import BaseExtractor
from .structures import ExtractedContent, ExtractionType, RawResponse


class ContentExtractor(BaseExtractor):
    """Extracts clean text content from HTML.
    
    This extractor removes all HTML tags and returns only the text content,
    with optional filtering of navigation, headers, footers, etc.
    """
    
    def extract(self, response: RawResponse) -> ExtractedContent:
        """Extract clean text content from response.
        
        Args:
            response: The raw response to extract from
            
        Returns:
            Extracted text content
        """
        try:
            if response.status < 200 or response.status >= 300:
                return ExtractedContent(
                    content="",
                    extraction_type=ExtractionType.CONTENT,
                    error=f"HTTP {response.status}",
                )
            
            tree = self._parse_html(response.text)
            cleaned_tree = self._clean_tree(tree, response.url)
            
            # Extract metadata
            metadata = self._extract_metadata(tree)
            links = self._extract_links(tree, response.url)
            images = self._extract_images(tree, response.url)
            
            # Find main content area (prioritize main, article, or body)
            main_content = (
                cleaned_tree.css_first("main")
                or cleaned_tree.css_first("article")
                or cleaned_tree.css_first("body")
                or cleaned_tree.body
            )
            
            # Extract text from content elements
            selectors = "p, h1, h2, h3, h4, h5, h6, li, div, span, td, th"
            text_elements = main_content.css(selectors) if main_content else []
            
            # Filter and clean text using list comprehension
            text_parts = [
                text
                for element in text_elements
                if (text := element.text(strip=True)) and len(text) >= self.config.min_text_length
            ]
            
            # Join with double newlines for better readability
            content = "\n\n".join(text_parts)
            
            return ExtractedContent(
                content=content,
                metadata=metadata,
                links=links,
                images=images,
                extraction_type=ExtractionType.CONTENT,
            )
            
        except Exception as e:
            return ExtractedContent(
                content="",
                extraction_type=ExtractionType.CONTENT,
                error=f"Extraction error: {str(e)}",
            )
