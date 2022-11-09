import unittest

from client.db.utils import dict_to_conn_str


class TestDictToConnStr(unittest.TestCase):

    config_dict: dict = {
        "postgresql": {
            "host": "example.com",
            "port": 8001,
            "database": "test",
            "user": "Alice",
            "password": "%Ef699Fwz8z*",
        }
    }
    expected_conn_str: str = (
        "host=example.com dbname=test user=Alice password=%Ef699Fwz8z*"
    )

    def test_dict_to_conn_str(self) -> None:
        """Test function that converts a dict to a connection string."""

        generated_conn_str: str = dict_to_conn_str(self.config_dict)
        self.assertEqual(generated_conn_str, self.expected_conn_str)
