# -*- coding: utf-8 -*-
import unittest

from client.db.utils import dict_to_conn_str


class TestDictToConnStr(unittest.TestCase):

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

    def test_dict_to_conn_str(self) -> None:
        generated_conn_str = dict_to_conn_str(self.config_dict)
        self.assertEqual(generated_conn_str, self.expected_conn_str)


if __name__ == "__main__":
    unittest.main()
