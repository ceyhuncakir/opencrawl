from typing import Any
from pydantic import BaseModel

class SpiderOutput(BaseModel):
    url: str
    content: Any  # Can be str (GenerationOutput.text) or any Pydantic BaseModel (structured outputs)