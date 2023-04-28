"""Test the dict_to_conn_str function."""
from __future__ import annotations

import unittest

from client.db.utils import dict_to_conn_str


class TestDictToConnStr(unittest.TestCase):
    """Test the dict_to_conn_str function."""

    config_dict = {
        "postgresql": {
            "host": "example.com",
            "port": 8001,
            "database": "test",
            "user": "Alice",
            "password": "%Ef699Fwz8z*",
        }
    }
    expected_conn_str = "host=example.com dbname=test user=Alice password=%Ef699Fwz8z*"

    def test_dict_to_conn_str(self: TestDictToConnStr) -> None:
        """Test function that converts a dict to a connection string."""
        generated_conn_str = dict_to_conn_str(self.config_dict)
        assert generated_conn_str == self.expected_conn_str
