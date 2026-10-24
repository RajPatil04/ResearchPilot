"""Unit tests for GemmaClient using mock SDK responses."""

import unittest
from unittest.mock import MagicMock, patch
from src.gemma_client import GemmaClient, GemmaClientError


class TestGemmaClientMock(unittest.TestCase):

    def setUp(self):
        self.mock_api_key = "AIzaSyFakeTestKey1234567890abcdefABC"

    @patch("src.gemma_client.genai.Client")
    def test_client_init_and_masked_key(self, mock_genai_client):
        client = GemmaClient(api_key=self.mock_api_key, model="gemma-4-26b-a4b-it")
        self.assertEqual(client.model, "gemma-4-26b-a4b-it")
        masked = client.masked_key
        self.assertNotIn("1234567890", masked)
        self.assertTrue(masked.startswith("AIza"))
        self.assertTrue(masked.endswith("fABC"))

    def test_empty_api_key_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(GemmaClientError) as ctx:
                GemmaClient(api_key="")
            self.assertIn("No API key provided", str(ctx.exception))

    @patch("src.gemma_client.genai.Client")
    def test_test_connection_success(self, mock_genai_client):
        mock_instance = MagicMock()
        mock_genai_client.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "Gemma 4 model is ready."
        mock_instance.models.generate_content.return_value = mock_response

        client = GemmaClient(api_key=self.mock_api_key)
        success, msg = client.test_connection()
        self.assertTrue(success)
        self.assertIn("Successfully connected", msg)

    @patch("src.gemma_client.genai.Client")
    def test_generate_text_success(self, mock_genai_client):
        mock_instance = MagicMock()
        mock_genai_client.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "This is a structured summary of the Transformer paper."
        mock_instance.models.generate_content.return_value = mock_response

        client = GemmaClient(api_key=self.mock_api_key)
        result = client.generate_text("Summarize the paper")
        self.assertEqual(result, "This is a structured summary of the Transformer paper.")
        mock_instance.models.generate_content.assert_called_once()

    @patch("src.gemma_client.genai.Client")
    def test_generate_with_image_success(self, mock_genai_client):
        mock_instance = MagicMock()
        mock_genai_client.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "The chart displays training loss converging after epoch 10."
        mock_instance.models.generate_content.return_value = mock_response

        client = GemmaClient(api_key=self.mock_api_key)
        dummy_png = b"\x89PNG\r\n\x1a\nfakeimagebytes"
        result = client.generate_with_image(
            prompt="Analyze the loss curves",
            image_bytes=dummy_png
        )
        self.assertIn("training loss converging", result)

    @patch("src.gemma_client.genai.Client")
    def test_key_sanitization_in_errors(self, mock_genai_client):
        mock_instance = MagicMock()
        mock_genai_client.return_value = mock_instance
        # Simulate an exception containing the raw secret key
        mock_instance.models.generate_content.side_effect = Exception(
            f"Quota exceeded for request with key {self.mock_api_key}"
        )

        client = GemmaClient(api_key=self.mock_api_key)
        with self.assertRaises(GemmaClientError) as ctx:
            client.generate_text("Hello")

        # The error message must NEVER leak the secret key
        error_msg = str(ctx.exception)
        self.assertNotIn(self.mock_api_key, error_msg)
        self.assertIn("[REDACTED_API_KEY]", error_msg)


if __name__ == "__main__":
    unittest.main()
