#!/usr/bin/env python
import json
from dotenv import load_dotenv
from argparse import ArgumentParser

from src.neris_api_client import NerisApiClient


if __name__ == "__main__":
    parser = ArgumentParser(description="Lists NERIS API integrations for an entity")
    parser.add_argument("-n", "--neris-id", help="NERIS ID of the entity for which to list integrations")
    args = parser.parse_args()

    # Credentials must be defined in .env
    load_dotenv()
    client = NerisApiClient()

    res = client.list_integrations(neris_id=args.neris_id)

    print(json.dumps(res.json(), indent=2))
