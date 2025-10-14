from typing import List, Optional

import json
import os
from pathlib import Path

from opencrawl import (
    Model,
    CrawlerConfig,
    ModelConfig,
    AsyncCrawler,
    CrawlResponse,
    CrawlRequest,
)
from opencrawl.core import SpiderOutput


class Spider:
    def __init__(
        self,
        crawl_config: CrawlerConfig = None,
        model_config: ModelConfig = None,
        output_path: Optional[str] = None,
    ) -> None:
        self._crawl_config = crawl_config
        self._model_config = model_config
        self._output_path = output_path

        if model_config:
            self._generator = Model(model_config)

        if crawl_config:
            self._crawler = AsyncCrawler(crawl_config)

    def _build_conversation(self, responses: List[CrawlResponse], task: Optional[str] = None) -> list[dict]:
        
        conversations = []
        
        for response in responses:
            conversation = []

            content = response.extracted.content if response.extracted else response.text
            
            # Add system prompt if task is provided
            if task:
                conversation.append({
                    "role": "system",
                    "content": task
                })
            
            # Add HTML content as user message
            conversation.append({
                "role": "user",
                "content": f"URL: {response.url}\n\nContent:\n{content}"
            })
            
            conversations.append(conversation)

        return conversations

    def _save_to_json(self, spider_outputs: List[SpiderOutput]) -> None:
        """Save spider outputs to JSON file.
        
        Args:
            spider_outputs: List of SpiderOutput objects to save.
        """
        if not self._output_path:
            return
        
        # Create parent directories if they don't exist
        output_path = Path(self._output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert Pydantic models to dictionaries
        outputs_dict = [output.model_dump() for output in spider_outputs]
        
        # Write to JSON file
        with open(self._output_path, "w", encoding="utf-8") as f:
            json.dump(outputs_dict, f, indent=2, ensure_ascii=False)

    async def crawl(
        self,
        requests: List[CrawlRequest],
        task: Optional[str] = None,
    ) -> List[SpiderOutput]:
        """Crawl URLs and process content with LLM.

        Args:
            requests: List of URLs to crawl.
            task: Task definition for the LLM (system prompt).

        Returns:
            List of SpiderOutput objects with URL, content, analysis, and token count.
        """
        # Crawl the websites
        await self._crawler.setup()
        crawl_data = await self._crawler.fetch_all(requests=requests)
        await self._crawler.cleanup()

        # Build conversations for each crawled page
        conversations = self._build_conversation(crawl_data, task)

        # Process with LLM
        outputs = self._generator.chat(conversations)

        spider_outputs = [
            SpiderOutput(
                url=response.url,
                content=outputs[i]
            )
            for i, response in enumerate(crawl_data)
        ]

        # Save to JSON if output path is specified
        self._save_to_json(spider_outputs)

        return spider_outputs