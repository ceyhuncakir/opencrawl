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

# TODO
- [ ] Write tests
- [ ] create more extraction strategies
- [ ] add more proxy strategies
- [ ] Captcha bypasses
- [ ] better model support from VLLM

# Features

## Crawler Features

<details>
<summary><b>High-Performance Web Crawling</b></summary>

- **Async Architecture**: Built on `aiohttp` and `uvloop` for maximum performance
- **Concurrent Requests**: Configurable concurrency limits with semaphore-based control
- **Smart Retry Logic**: Automatic retries with exponential backoff for failed requests
- **Connection Management**: Efficient connection pooling and timeout control

</details>

<details>
<summary><b>Proxy Support</b></summary>

- **Proxy Rotation**: Automatic proxy rotation from a pool of proxies
- **Proxy Validation**: Built-in proxy health checking against test endpoints
- **Multiple Input Methods**: Load proxies from file or comma-separated string
- **Proxy Filtering**: Automatic removal of invalid proxies

</details>

<details>
<summary><b>Flexible Configuration</b></summary>

- **Custom Headers & Cookies**: Set default and per-request headers/cookies
- **SSL Control**: Enable/disable SSL verification as needed
- **Redirect Handling**: Configurable redirect following with max redirect limits
- **User Agent**: Customizable user agent strings
- **Request Timeouts**: Fine-grained timeout control for each request

</details>

<details>
<summary><b>Content Extraction</b></summary>

- **Multiple Extraction Types**:
  - **HTML**: Raw HTML extraction with cleaning options
  - **Content**: Clean text content extraction
  - **Markdown**: Convert HTML to markdown format
- **Smart Cleaning**: Configurable removal of scripts, styles, navigation, headers, footers
- **Metadata Extraction**: Automatic extraction of page metadata (title, description, keywords)
- **Link & Image Preservation**: Optional extraction of links and image URLs
- **Minimum Text Filtering**: Filter out elements below a minimum text length

</details>

## Model Features

<details>
<summary><b>VLLM-Powered Inference</b></summary>

- **Flexible & Easy**: Built on VLLM for easy model integration
- **Multi-GPU Support**: Automatic device mapping across multiple GPUs
- **Cross-Platform**: Works on Linux, macOS (MPS), and CPU
- **Batch Generation**: Efficient batch processing for multiple requests

</details>

<details>
<summary><b>Model Configuration</b></summary>

- **Flexible Model Loading**: Support for any HuggingFace model
- **Data Type Options**: Choose between auto, float16, bfloat16, and float32
- **Custom Download**: Specify custom cache directories for models
- **Device Mapping**: Automatic or manual device mapping for multi-GPU setups
- **Trust Remote Code**: Option to trust remote code for specialized models

</details>

<details>
<summary><b>Advanced Generation Control</b></summary>

- **Temperature & Sampling**: Fine-tune creativity with temperature, top_p, and top_k
- **Token Control**: Set min/max tokens, stop sequences, and EOS handling
- **Penalties**: Apply repetition and length penalties for better generation quality
- **Multiple Outputs**: Generate multiple sequences and control output diversity
- **Stopping Criteria**: Custom stopping criteria with stop strings support

</details>

<details>
<summary><b>Chat & Structured Outputs</b></summary>

- **Chat Templates**: Built-in support for chat-style interactions
- **Structured Outputs**: Extract structured data using Pydantic models
- **JSON Validation**: Automatic parsing and validation of structured responses
- **Batch Chat**: Efficient batch processing of multiple conversations

</details>

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
            dtype="float16",
            device_map="auto",
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
            dtype="float16",
            gen_config=GenerationConfig(
                temperature=0.7,
                max_new_tokens=512,
                do_sample=True,
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

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. The developers of OpenCrawl are not responsible for any damages, legal issues, or consequences arising from the use or misuse of this tool. Users are solely responsible for ensuring their use complies with applicable laws, terms of service, and ethical guidelines.

## License
This project is licensed wit the Apache 2.0 license. Please have a look at the license if your not sure what the kind of rules it requires.