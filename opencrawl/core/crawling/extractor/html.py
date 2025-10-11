"""Full HTML extraction strategy."""

from .base import BaseExtractor
from .structures import ExtractedContent, ExtractionType, RawResponse


class HTMLExtractor(BaseExtractor):
    """Extracts full HTML content with minimal processing.
    
    This extractor returns the complete HTML with optional cleanup
    of scripts, styles, and comments based on configuration.
    """
    
    def extract(self, response: RawResponse) -> ExtractedContent:
        """Extract full HTML from response.
        
        Args:
            response: The raw response to extract from
            
        Returns:
            Extracted HTML content
        """
        try:
            if response.status < 200 or response.status >= 300:
                return ExtractedContent(
                    content="",
                    extraction_type=ExtractionType.HTML,
                    error=f"HTTP {response.status}",
                )
            
            tree = self._parse_html(response.text)
            cleaned_tree = self._clean_tree(tree, response.url)
            
            metadata = self._extract_metadata(tree)
            links = self._extract_links(tree, response.url)
            images = self._extract_images(tree, response.url)
            
            return ExtractedContent(
                content=cleaned_tree.html,
                metadata=metadata,
                links=links,
                images=images,
                extraction_type=ExtractionType.HTML,
            )
            
        except Exception as e:
            return ExtractedContent(
                content="",
                extraction_type=ExtractionType.HTML,
                error=f"Extraction error: {str(e)}",
            )
