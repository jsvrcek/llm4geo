from unittest.mock import MagicMock

from django.test import TestCase, override_settings


class TestChatExportsView(TestCase):

    mocked_response = [{"example_key": "example_value"}]
    mocked_model = MagicMock()
    mocked_model().with_structured_output().invoke.return_value = mocked_response

    @override_settings(LLM_MODEL=mocked_model)
    def test_post(self):
        self.assertEquals(
            self.client.post({"text_input": "some_input"}), self.mocked_response
        )
