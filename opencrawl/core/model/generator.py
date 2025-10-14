"""Text generation using vLLM models.

This module provides a clean interface for generating text using vLLM models
with extensive sampling parameter control.
"""

from typing import Any, Union
import json

from transformers import AutoProcessor

from .base import BaseVLLM
from .structures import GenerationConfig, GenerationOutput, ModelConfig

# Type alias for chat messages
ChatMessage = dict[str, str]
Conversation = list[ChatMessage]


class Model:
    """Text generator using model for high-performance inference.

    This class provides a clean interface for generating text with models.
    It handles both single and batch generation with flexible configuration.

    Example:
        >>> model_config = ModelConfig(
        ...     model="meta-llama/Llama-2-7b-hf",
        ...     tensor_parallel_size=1
        ... )
        >>> generator = Model(model_config)
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
        model_config: ModelConfig,
    ) -> None:
        """Initialize the generator with model configuration.

        Args:
            model_config: Configuration for model initialization.
            default_gen_config: Default generation configuration (optional).
        """
        self.base_model = BaseVLLM(model_config)
        self.default_gen_config = model_config.gen_config or GenerationConfig()

    def chat(
        self,
        messages: Union[Conversation, list[Conversation]]
    ) -> list[GenerationOutput]:
        """Generate text from chat conversations using chat templates.

        This method uses vLLM's chat API which automatically formats messages
        using the model's default chat template or a custom template if provided.

        Args:
            messages: Either a single conversation or a list of conversations.
                Each conversation is a list of message dicts with 'role' and 'content'.
                Example: [{"role": "user", "content": "Hello"}]
            **kwargs: Additional generation parameters to override config.

        Returns:
            List of GenerationOutput objects for each conversation.

        Example:
            >>> conversation = [
            ...     {"role": "system", "content": "You are a helpful assistant"},
            ...     {"role": "user", "content": "Hello"}
            ... ]
            >>> outputs = model.chat(conversation)
            >>> print(outputs[0].text)
        """
        config = self.default_gen_config

        # Prepare kwargs for llm.chat()
        chat_kwargs = {
            "sampling_params": config.to_sampling_params(),
            "use_tqdm": config.use_tqdm,
        }

        # Generate with vLLM chat API
        outputs = self.base_model.model.chat(messages, **chat_kwargs)

        # Parse outputs
        results = []

        for output in outputs:
            # Get the first (or best) completion
            completion = output.outputs[0]

            if config.structured_outputs:
                # Parse JSON and validate against the Pydantic model
                parsed_data = json.loads(completion.text)
                validated_model = config.structured_outputs.model_validate(parsed_data)
                results.append(validated_model)
            else:
                # Return standard GenerationOutput
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

    def __repr__(self) -> str:
        """String representation of the generator."""
        return f"Model(model={self.base_model.config.model})"
