<div align="center">
  <img src="images/banner.svg" alt="OpenCrawl Banner" width="100%">
</div>

<div align="center" style="margin-top: 20px;">

[![GitHub stars](https://img.shields.io/github/stars/ceyhuncakir/opencrawl?style=social)](https://github.com/ceyhuncakir/opencrawl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ceyhuncakir/opencrawl?style=social)](https://github.com/ceyhuncakir/opencrawl/network/members)

</div>

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/opencrawl?color=brightgreen&label=pypi%20package)](https://pypi.org/project/opencrawl/)
[![Python versions](https://img.shields.io/pypi/pyversions/opencrawl)](https://pypi.org/project/opencrawl/)
[![Downloads](https://img.shields.io/pypi/dm/opencrawl?color=blue&label=downloads/month)](https://pypi.org/project/opencrawl/)
[![Sponsors](https://img.shields.io/github/sponsors/ceyhuncakir?color=pink&logo=github-sponsors)](https://github.com/sponsors/ceyhuncakir)

</div>

# Opencrawl
This project was created to crawl data in a meaningfull way using open source LLMs. I've been thinking of that most crawlers either use propriatary models from openai or anthropic but rarely have i seen crawlers that are using solely open-source models. So for that reason this project came to to the creation. Its still in the very early stages, but througout the time i will keep maintainting it and adding more features to make crawling more comphrensive with open-source LLMs.

## Installation
With pip
```
pip install opencrawl
```

With uv
```
uv add opencrawl
```

## Examples
### Basic Crawling
Simple web crawling with markdown extraction:

```python
import asyncio
from opencrawl import AsyncCrawler, CrawlerConfig, CrawlRequest, ExtractionType

async def crawl_example():
    # Configure the crawler
    config = CrawlerConfig(
        max_concurrent_requests=5,
        extraction_strategy=ExtractionType.MARKDOWN,
    )
    
    # Create crawler and fetch content
    crawler = AsyncCrawler(config)
    await crawler.setup()
    
    response = await crawler.fetch(
        CrawlRequest(url="https://example.com")
    )
    
    print(response.extracted.content)
    await crawler.cleanup()

asyncio.run(crawl_example())
```

### Crawling with LLM Analysis
Combine web crawling with open-source LLM analysis:

```python
import asyncio
from opencrawl import Spider, ModelConfig, CrawlerConfig, CrawlRequest, ExtractionType

async def llm_crawl_example():
    # Initialize spider with crawler and model
    spider = Spider(
        crawl_config=CrawlerConfig(
            max_concurrent_requests=5,
            extraction_strategy=ExtractionType.MARKDOWN,
        ),
        model_config=ModelConfig(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            tensor_parallel_size=1,
        ),
        output_path="output.json"
    )
    
    # Define task and crawl
    task = "Summarize the main content of this webpage."
    results = await spider.crawl(
        requests=[
            CrawlRequest(url="https://example.com"),
            CrawlRequest(url="https://example.org"),
        ],
        task=task,
    )
    
    for result in results:
        print(f"{result.url}: {result.content}")

asyncio.run(llm_crawl_example())
```

### Structured Output Extraction
Extract structured data using Pydantic models:

```python
import asyncio
from pydantic import BaseModel
from opencrawl import Spider, ModelConfig, GenerationConfig, CrawlerConfig, CrawlRequest

class ArticleData(BaseModel):
    title: str
    summary: str
    main_topics: list[str]

async def structured_extraction():
    spider = Spider(
        crawl_config=CrawlerConfig(),
        model_config=ModelConfig(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            gen_config=GenerationConfig(
                temperature=0.7,
                max_tokens=512,
                structured_outputs=ArticleData,
            ),
        ),
    )
    
    results = await spider.crawl(
        requests=[CrawlRequest(url="https://example.com/article")],
        task="Extract the article title, summary, and main topics.",
    )
    
    print(results[0].content)

asyncio.run(structured_extraction())
```

## Contributions
This project is in its very early stages, but any contributions towards the project is highgly appreciatied. Just open a PR and i will have an look at it, and if its fits the projects vision, i will gladly merge it in.

## License
This project is licensed wit the Apache 2.0 license. Please have a look at the license if your not sure what the kind of rules it requires.