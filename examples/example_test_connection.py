# -*- coding: utf-8 -*-
"""A script to demonstrate how to check the connection to the MarktstammdatenregisterAPI."""

import os

from dotenv import load_dotenv

from app.api import MaStR

if __name__ == "__main__":
    # Load credentials from .env into environment
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    # Initialize the API object.
    api = MaStR()

    # Test the connection to the API.
    print(api.test_connection())

    # Authorize the API object.
    api.set_api_key(API_KEY)

    # Test if API Token is valid.
    print(api.test_authorization())
