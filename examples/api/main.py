#!/usr/bin/env python
import json
from dotenv import load_dotenv
from argparse import ArgumentParser

from src.neris_api_client import NerisApiClient


if __name__ == "__main__":
    parser = ArgumentParser(description="Creates a NERIS API integration")
    parser.add_argument("-n", "--neris-id", help="NERIS ID of the entity to which to attach the integration")
    parser.add_argument("-t", "--title", help="Title of the new integration")
    args = parser.parse_args()

    # Credentials must be defined in .env
    load_dotenv()
    client = NerisApiClient()

    res = client.create_api_integration(neris_id=args.neris_id, title=args.title)

    print(json.dumps(res.json(), indent=2))
