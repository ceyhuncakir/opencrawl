"""Base model configuration and initialization for vLLM.

This module provides the base class for serving and managing vLLM models.
"""

from typing import Optional
from vllm import LLM as VLLMModel

from .structures import ModelConfig


class BaseVLLM:
    """Base class for vLLM model serving and management.

    This class handles the initialization and lifecycle management of vLLM models.
    It provides a clean interface for serving models dynamically.

    Example:
        >>> config = VLLMConfig(
        ...     model="meta-llama/Llama-2-7b-hf",
        ...     tensor_parallel_size=1,
        ...     dtype="float16"
        ... )
        >>> base_model = BaseVLLM(config)
        >>> # Model is now ready for generation
    """

    def __init__(self, config: ModelConfig):
        """Initialize the vLLM model with given configuration.

        Args:
            config: VLLMConfig instance with model parameters.

        Raises:
            ImportError: If vLLM is not installed.
            ValueError: If configuration is invalid.
        """
        self.config = config
        self._model: Optional[VLLMModel] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the vLLM model instance.

        Raises:
            ImportError: If vLLM package is not available.
        """
        try:
            # Build initialization parameters
            init_params = {
                "model": self.config.model,
                "tensor_parallel_size": self.config.tensor_parallel_size,
                "trust_remote_code": self.config.trust_remote_code,
                "dtype": self.config.dtype,
                "gpu_memory_utilization": self.config.gpu_memory_utilization,
                "enforce_eager": self.config.enforce_eager,
                "swap_space": self.config.swap_space,
                "seed": self.config.seed,
            }
            
            # Add optional parameters if specified
            if self.config.download_dir is not None:
                init_params["download_dir"] = self.config.download_dir
            if self.config.max_model_len is not None:
                init_params["max_model_len"] = self.config.max_model_len
            if self.config.max_num_batched_tokens is not None:
                init_params["max_num_batched_tokens"] = self.config.max_num_batched_tokens
            
            # Add any additional kwargs
            init_params.update(self.config.kwargs)
            
            self._model = VLLMModel(**init_params)
        except ImportError as e:
            raise ImportError(
                "Could not import vllm python package. "
                "Please install it with `pip install vllm`."
            ) from e

    @property
    def model(self) -> VLLMModel:
        """Get the underlying vLLM model instance.

        Returns:
            The initialized vLLM model.

        Raises:
            RuntimeError: If model is not initialized.
        """
        if self._model is None:
            raise RuntimeError("Model is not initialized")
        return self._model

    def is_ready(self) -> bool:
        """Check if the model is ready for inference.

        Returns:
            True if model is initialized and ready.
        """
        return self._model is not None

    def reload_model(self, new_config: Optional[ModelConfig] = None) -> None:
        """Reload the model with optional new configuration.

        Args:
            new_config: Optional new configuration. If None, uses current config.
        """
        if new_config is not None:
            self.config = new_config

        self._model = None
        self._initialize_model()

    def __repr__(self) -> str:
        """String representation of the model instance."""
        return (
            f"BaseVLLM(model={self.config.model}, "
            f"tensor_parallel_size={self.config.tensor_parallel_size}, "
            f"dtype={self.config.dtype})"
        )
