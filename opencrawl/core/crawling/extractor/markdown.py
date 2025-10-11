"""Markdown extraction strategy."""

from .base import BaseExtractor
from .structures import ExtractedContent, ExtractionType, RawResponse


class MarkdownExtractor(BaseExtractor):
    """Extracts content and converts it to Markdown format.
    
    This extractor converts HTML to clean Markdown, preserving
    structure like headings, lists, links, and emphasis.
    """
    
    def extract(self, response: RawResponse) -> ExtractedContent:
        """Extract content and convert to Markdown.
        
        Args:
            response: The raw response to extract from
            
        Returns:
            Extracted content in Markdown format
        """
        try:
            if response.status < 200 or response.status >= 300:
                return ExtractedContent(
                    content="",
                    extraction_type=ExtractionType.MARKDOWN,
                    error=f"HTTP {response.status}",
                )
            
            tree = self._parse_html(response.text)
            cleaned_tree = self._clean_tree(tree, response.url)
            
            # Extract metadata
            metadata = self._extract_metadata(tree)
            links = self._extract_links(tree, response.url)
            images = self._extract_images(tree, response.url)
            
            # Find main content area
            main_content = (
                cleaned_tree.css_first("main")
                or cleaned_tree.css_first("article")
                or cleaned_tree.css_first("body")
                or cleaned_tree.body
            )
            
            # Convert to markdown
            markdown_content = self._convert_to_markdown(main_content, response.url) if main_content else ""
            
            return ExtractedContent(
                content=markdown_content,
                metadata=metadata,
                links=links,
                images=images,
                extraction_type=ExtractionType.MARKDOWN,
            )
            
        except Exception as e:
            return ExtractedContent(
                content="",
                extraction_type=ExtractionType.MARKDOWN,
                error=f"Extraction error: {str(e)}",
            )
    
    def _convert_to_markdown(self, node, base_url: str = "") -> str:
        """Convert HTML node to Markdown.
        
        Args:
            node: Selectolax node to convert
            base_url: Base URL for resolving relative links
            
        Returns:
            Markdown formatted string
        """
        from urllib.parse import urljoin
        
        markdown_parts = []
        
        # Headings - using list comprehension
        for level in range(1, 7):
            headings = [
                f"{'#' * level} {h.text(strip=True)}\n"
                for h in node.css(f"h{level}")
                if (text := h.text(strip=True)) and len(text) >= self.config.min_text_length
            ]
            markdown_parts.extend(headings)
        
        # Paragraphs
        paragraphs = [
            f"{p.text(strip=True)}\n"
            for p in node.css("p")
            if (text := p.text(strip=True)) and len(text) >= self.config.min_text_length
        ]
        markdown_parts.extend(paragraphs)
        
        # Links (if preserve_links is enabled)
        if self.config.preserve_links:
            links = [
                f"[{a.text(strip=True)}]({urljoin(base_url, href)})"
                for a in node.css("a[href]")
                if (href := a.attributes.get("href")) and (text := a.text(strip=True)) and len(text) >= self.config.min_text_length
            ]
            markdown_parts.extend(links)
        
        # Images (if preserve_images is enabled)
        if self.config.preserve_images:
            images = [
                f"![{img.attributes.get('alt', '')}]({urljoin(base_url, src)})\n"
                for img in node.css("img[src]")
                if (src := img.attributes.get("src"))
            ]
            markdown_parts.extend(images)
        
        # Ordered list items
        ol_items = [
            f"1. {li.text(strip=True)}\n"
            for li in node.css("ol > li")
            if (text := li.text(strip=True)) and len(text) >= self.config.min_text_length
        ]
        markdown_parts.extend(ol_items)
        
        # Unordered list items
        ul_items = [
            f"- {li.text(strip=True)}\n"
            for li in node.css("ul > li")
            if (text := li.text(strip=True)) and len(text) >= self.config.min_text_length
        ]
        markdown_parts.extend(ul_items)
        
        # Code blocks
        code_blocks = [
            f"```\n{code.text(strip=True)}\n```\n"
            for code in node.css("pre > code")
            if (text := code.text(strip=True))
        ]
        markdown_parts.extend(code_blocks)
        
        # Inline code
        inline_code = [
            f"`{code.text(strip=True)}`"
            for code in node.css("code")
            if code.parent and code.parent.tag != "pre" and (text := code.text(strip=True))
        ]
        markdown_parts.extend(inline_code)
        
        # Blockquotes
        blockquotes = [
            "\n".join([f"> {line}" for line in bq.text(strip=True).split("\n") if line.strip()]) + "\n"
            for bq in node.css("blockquote")
            if (text := bq.text(strip=True)) and len(text) >= self.config.min_text_length
        ]
        markdown_parts.extend(blockquotes)
        
        # Bold
        bold = [
            f"**{b.text(strip=True)}**"
            for b in node.css("strong, b")
            if (text := b.text(strip=True))
        ]
        markdown_parts.extend(bold)
        
        # Italic
        italic = [
            f"*{i.text(strip=True)}*"
            for i in node.css("em, i")
            if (text := i.text(strip=True))
        ]
        markdown_parts.extend(italic)
        
        # Join and clean up
        markdown = "\n".join(markdown_parts)
        
        # Remove excessive newlines
        while "\n\n\n" in markdown:
            markdown = markdown.replace("\n\n\n", "\n\n")
        
        return markdown.strip()
