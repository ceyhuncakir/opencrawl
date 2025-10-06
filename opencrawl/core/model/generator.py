"""Text generation using vLLM models.

This module provides a clean interface for generating text using vLLM models
with extensive sampling parameter control.
"""

from typing import Any, Optional

from .base import BaseVLLM
from .structures import GenerationConfig, GenerationOutput, VLLMConfig


class VLLMGenerator:
    """Text generator using vLLM for high-performance inference.

    This class provides a clean interface for generating text with vLLM models.
    It handles both single and batch generation with flexible configuration.

    Example:
        >>> model_config = VLLMConfig(
        ...     model="meta-llama/Llama-2-7b-hf",
        ...     tensor_parallel_size=1
        ... )
        >>> generator = VLLMGenerator(model_config)
        >>>
        >>> gen_config = GenerationConfig(
        ...     temperature=0.7,
        ...     max_tokens=100,
        ...     top_p=0.9
        ... )
        >>>
        >>> output = generator.generate("Hello, world!", gen_config)
        >>> print(output.text)
    """

    def __init__(
        self,
        model_config: VLLMConfig,
        default_gen_config: Optional[GenerationConfig] = None,
    ):
        """Initialize the generator with model configuration.

        Args:
            model_config: Configuration for vLLM model initialization.
            default_gen_config: Default generation configuration (optional).
        """
        self.base_model = BaseVLLM(model_config)
        self.default_gen_config = default_gen_config or GenerationConfig()

    def generate(
        self,
        prompt: str,
        gen_config: Optional[GenerationConfig] = None,
        **kwargs: Any,
    ) -> GenerationOutput:
        """Generate text from a single prompt.

        Args:
            prompt: The input text prompt.
            gen_config: Generation configuration (uses default if None).
            **kwargs: Additional generation parameters to override config.

        Returns:
            GenerationOutput with the generated text and metadata.
        """
        outputs = self.batch_generate([prompt], gen_config, **kwargs)
        return outputs[0]

    def batch_generate(
        self,
        prompts: list[str],
        gen_config: Optional[GenerationConfig] = None,
        **kwargs: Any,
    ) -> list[GenerationOutput]:
        """Generate text from multiple prompts in batch.

        Args:
            prompts: List of input text prompts.
            gen_config: Generation configuration (uses default if None).
            **kwargs: Additional generation parameters to override config.

        Returns:
            List of GenerationOutput objects for each prompt.
        """
        config = gen_config or self.default_gen_config

        # Override config with kwargs if provided
        if kwargs:
            config_dict = {
                k: v
                for k, v in config.__dict__.items()
                if not k.startswith("_") and k != "kwargs"
            }
            config_dict.update(kwargs)
            config = GenerationConfig(**config_dict)

        sampling_params = config.to_sampling_params()

        # Generate with vLLM
        outputs = self.base_model.model.generate(prompts, sampling_params)

        # Parse outputs
        results = []
        for output in outputs:
            # Get the first (or best) completion
            completion = output.outputs[0]

            result = GenerationOutput(
                text=completion.text,
                finish_reason=completion.finish_reason,
                prompt_tokens=len(output.prompt_token_ids),
                completion_tokens=len(completion.token_ids),
                total_tokens=len(output.prompt_token_ids) + len(completion.token_ids),
                logprobs=completion.logprobs if config.logprobs else None,
            )
            results.append(result)

        return results

    def stream_generate(
        self,
        prompt: str,
        gen_config: Optional[GenerationConfig] = None,
        **kwargs: Any,
    ):
        """Generate text with streaming output (placeholder for future implementation).

        Note: vLLM does not natively support streaming through the offline API.
        Consider using vLLM's OpenAI-compatible server for streaming.

        Args:
            prompt: The input text prompt.
            gen_config: Generation configuration (uses default if None).
            **kwargs: Additional generation parameters to override config.

        Raises:
            NotImplementedError: Streaming is not yet implemented.
        """
        raise NotImplementedError(
            "Streaming is not supported with vLLM offline inference API. "
            "Use vLLM's OpenAI-compatible server for streaming support."
        )

    def update_default_config(self, gen_config: GenerationConfig) -> None:
        """Update the default generation configuration.

        Args:
            gen_config: New default generation configuration.
        """
        self.default_gen_config = gen_config

    def reload_model(self, model_config: VLLMConfig) -> None:
        """Reload the underlying model with new configuration.

        Args:
            model_config: New model configuration.
        """
        self.base_model.reload_model(model_config)

    def __repr__(self) -> str:
        """String representation of the generator."""
        return f"VLLMGenerator(model={self.base_model.config.model})"
