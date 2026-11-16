import unittest
from unittest.mock import patch
from web_reader import fetch_article

class WebReaderTest(unittest.TestCase):
    def test_non_web_urls(self):
        for url in ['file:///etc/passwd','javascript:alert(1)','http://user:pass@example.com','https://example.com:8765']:
            with self.assertRaises(ValueError):fetch_article(url)

    def test_private_resolution(self):
        with patch('web_reader.socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',80))]):
            with self.assertRaises(ValueError):fetch_article('http://example.com')
