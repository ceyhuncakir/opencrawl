"""Core data structures for OpenCrawl."""

from dataclasses import dataclass


@dataclass
class SpiderOutput:
    """Output from a Spider crawl operation.
    
    Attributes:
        url: The crawled URL
        content: The extracted or raw content
        analysis: LLM analysis of the content
        tokens: Total tokens used in analysis
    """
    
    url: str
    content: str
