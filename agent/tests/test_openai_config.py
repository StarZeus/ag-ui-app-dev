import os
import unittest
from unittest.mock import patch

from src.openai_config import build_chat_openai_kwargs


class OpenAIConfigTest(unittest.TestCase):
    def test_reads_openai_configuration_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://llm.example.test/v1",
                "OPENAI_MODEL": "custom-model",
            },
            clear=True,
        ):
            self.assertEqual(
                build_chat_openai_kwargs(),
                {
                    "model": "custom-model",
                    "api_key": "test-key",
                    "base_url": "https://llm.example.test/v1",
                },
            )

    def test_uses_defaults_and_openai_api_base_fallback(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_API_BASE": "https://fallback.example.test/v1"},
            clear=True,
        ):
            self.assertEqual(
                build_chat_openai_kwargs(),
                {
                    "model": "gpt-5.4-mini",
                    "base_url": "https://fallback.example.test/v1",
                },
            )


if __name__ == "__main__":
    unittest.main()
