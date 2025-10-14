from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Type

from vllm import SamplingParams
from vllm.sampling_params import StructuredOutputsParams
from pydantic import BaseModel

@dataclass
class ModelConfig:
    """Configuration for model initialization and serving.

    Attributes:
        model: The name or path of a HuggingFace Transformers model.
        tensor_parallel_size: Number of GPUs to use for distributed execution.
        trust_remote_code: Trust remote code when downloading model and tokenizer.
        dtype: Data type for model weights and activations ("auto", "float16", "bfloat16", "float32").
        download_dir: Directory to download and load the weights.
        gpu_memory_utilization: Fraction of GPU memory to use (0.0 to 1.0).
        max_model_len: Maximum sequence length supported by the model.
        max_num_batched_tokens: Maximum number of tokens to be processed in a single iteration.
        enforce_eager: Whether to enforce eager execution (disable CUDA graphs).
        swap_space: CPU swap space size (GiB) per GPU.
        seed: Random seed for reproducibility.
        **kwargs: Additional parameters for model initialization.
    """

    model: str
    tensor_parallel_size: int = 1
    trust_remote_code: bool = False
    dtype: str = "auto"
    download_dir: Optional[str] = None
    gpu_memory_utilization: float = 0.9
    max_model_len: Optional[int] = None
    max_num_batched_tokens: Optional[int] = None
    enforce_eager: bool = False
    swap_space: int = 4
    seed: int = 0
    gen_config: Optional[GenerationConfig] = None
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationConfig:
    """Configuration for text generation.

    Attributes:
        temperature: Float that controls the randomness of sampling (0.0 to 2.0).
        top_p: Float for nucleus sampling - cumulative probability cutoff.
        top_k: Integer for top-k sampling - number of top tokens to consider (-1 for all).
        max_tokens: Maximum number of tokens to generate per output sequence.
        n: Number of output sequences to return for each prompt.
        best_of: Number of output sequences generated, returns best n (n <= best_of).
        presence_penalty: Penalizes new tokens based on presence in text so far (-2.0 to 2.0).
        frequency_penalty: Penalizes new tokens based on frequency in text so far (-2.0 to 2.0).
        repetition_penalty: Penalizes repetition of tokens (1.0 means no penalty).
        stop: List of strings that stop generation when encountered.
        ignore_eos: Whether to ignore EOS token and continue generating.
        logprobs: Number of log probabilities to return per output token.
        min_tokens: Minimum number of tokens to generate before stopping.
        skip_special_tokens: Whether to skip special tokens in the output.
        spaces_between_special_tokens: Whether to add spaces between special tokens.
        chat_template: Optional Jinja2 chat template for formatting chat messages.
        use_tqdm: Whether to use tqdm progress bar during generation.
        **kwargs: Additional parameters for SamplingParams.
    """

    temperature: float = 1.0
    top_p: float = 1.0
    top_k: int = -1
    max_tokens: int = 512
    n: int = 1
    best_of: Optional[int] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    repetition_penalty: float = 1.0
    stop: Optional[list[str]] = None
    ignore_eos: bool = False
    logprobs: Optional[int] = None
    min_tokens: int = 0
    skip_special_tokens: bool = True
    spaces_between_special_tokens: bool = True
    chat_template: Optional[str] = None
    use_tqdm: bool = False
    structured_outputs: Optional[Type[BaseModel]] = None
    kwargs: dict[str, Any] = field(default_factory=dict)

    def to_sampling_params(self) -> SamplingParams:
        """Convert to SamplingParams object.

        Returns:
            SamplingParams instance with configured parameters.
        """
        return SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            structured_outputs=StructuredOutputsParams(self.structured_outputs.model_json_schema()),
            max_tokens=self.max_tokens,
            n=self.n,
            best_of=self.best_of,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            repetition_penalty=self.repetition_penalty,
            stop=self.stop,
            ignore_eos=self.ignore_eos,
            logprobs=self.logprobs,
            min_tokens=self.min_tokens,
            skip_special_tokens=self.skip_special_tokens,
            spaces_between_special_tokens=self.spaces_between_special_tokens,
            **self.kwargs,
        )


@dataclass
class GenerationOutput:
    """Output from text generation.

    Attributes:
        text: The generated text.
        finish_reason: Reason for generation completion ('length', 'stop', etc.).
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the completion.
        total_tokens: Total number of tokens (prompt + completion).
        logprobs: Log probabilities if requested.
    """

    text: str
    finish_reason: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    logprobs: Optional[Any] = None

