# -*- coding: utf-8 -*-
"""A script to demonstrate how to use the MarktstammdatenregisterAPI class."""

import os

from dotenv import load_dotenv

from app.api import MaStR
from app.enums import Einheiten

if __name__ == "__main__":
    # Load credentials from .env into environment
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    MARKTAKTEUR_NUMMER = os.getenv("MARKTAKTEUR_NUMMER")

    # Initialize the API object.
    api = MaStR()

    # Authorize the API object.
    api.set_api_key(API_KEY)
    api.set_marktakteur_nummer(MARKTAKTEUR_NUMMER)

    # Get the information for specific unit.
    response = api.get_unit(unit_type=Einheiten.SOLAR, unit_number="SEE943462317456")

    # Print the response.
    print(response)
