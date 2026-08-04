import os
import unittest
from unittest.mock import patch

from neris_api_client.config import Config, GrantType


class ConfigTests(unittest.TestCase):
    def test_explicit_password_config_does_not_require_grant_type_environment_variable(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Config(
                grant_type=GrantType.PASSWORD,
                username="user@example.test",
                password="secret",
            )

        self.assertEqual(config.grant_type, GrantType.PASSWORD)
        self.assertEqual(config.username, "user@example.test")
        self.assertEqual(config.password, "secret")

    def test_explicit_user_agent_is_preserved_when_environment_is_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Config(user_agent="integration-test/1.0")

        self.assertEqual(config.user_agent, "integration-test/1.0")


if __name__ == "__main__":
    unittest.main()
