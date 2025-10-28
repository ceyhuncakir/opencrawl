"""Text generation using vLLM models.

This module provides a clean interface for generating text using vLLM models
with extensive sampling parameter control.
"""

from typing import Union, List
import json


from .base import BaseVLLM
from .structures import GenerationConfig, GenerationOutput, ModelConfig


class Model:
    """Text generator using model for high-performance inference.

    This class provides a clean interface for generating text with models.
    It handles both single and batch generation with flexible configuration.

    Attributes:
        model_config: Configuration for model initialization.
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
        messages: Union[List[dict[str, str]], List[List[dict[str, str]]]]
    ) -> List[GenerationOutput]:
        """Generate text from chat conversations using chat templates.

        This method uses vLLM's chat API which automatically formats messages
        using the model's default chat template or a custom template if provided.
        
        Supports both single and batch generation - pass a list of conversations
        for efficient batch processing.

        Args:
            messages: Either a single conversation or a list of conversations.
                Each conversation is a list of message dicts with 'role' and 'content'.
                Example: [{"role": "user", "content": "Hello"}]
                For batch: [[{"role": "user", "content": "Hello"}], [{"role": "user", "content": "Hi"}]]

        Returns:
            List of GenerationOutput objects for each conversation.
            Always returns a list, even for single inputs.
        """
        config = self.default_gen_config

        is_single = len(messages) > 0 and isinstance(messages[0], dict)
        batch_messages = [messages] if is_single else messages

        chat_kwargs = {
            "sampling_params": config.to_sampling_params(),
            "use_tqdm": config.use_tqdm,
        }

        # Generate with vLLM chat API (batch generation)
        outputs = self.base_model.model.chat(batch_messages, **chat_kwargs)

        results = []

        for output in outputs:

            completion = output.outputs[0]

            if config.structured_outputs:
                parsed_data = json.loads(completion.text)
                validated_model = config.structured_outputs.model_validate(parsed_data)
                results.append(validated_model)
            else:
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
