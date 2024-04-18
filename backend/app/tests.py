from dotenv import find_dotenv, load_dotenv
import os
import unittest
from flask import current_app
from app import create_app
load_dotenv(find_dotenv(".test"))

class TestTiller(unittest.TestCase):
    config = os.environ.get("CONFIG") or "testing"
    
    def setUp(self) -> None:
        super().setUp()
        self.app = create_app(TestTiller.config)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self) -> None:
        super().tearDown()
        self.app_context.pop()
        self.app = None
        self.app_context = None
        
    def test_app_exists(self):
        self.assertFalse(current_app is None)
        
    def test_if_palindrome(self):
        name = "madam"
        response = self.client.get(f"/palindrome/{name}")
        self.assertEqual(response.text, name)