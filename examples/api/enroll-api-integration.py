#!/usr/bin/env python
import json
from uuid import UUID
from dotenv import load_dotenv
from argparse import ArgumentParser

from src.neris_api_client import NerisApiClient


if __name__ == "__main__":
    parser = ArgumentParser(description="Enrolls an entity in a NERIS API integration")
    parser.add_argument("-n", "--neris-id", help="NERIS ID of the entity")
    parser.add_argument("-c", "--client-id", help="Client ID of the integration being enrolled", type=UUID)
    args = parser.parse_args()

    # Credentials must be defined in .env
    load_dotenv()
    client = NerisApiClient()

    res = client.enroll_integration(neris_id=args.neris_id, client_id=args.client_id)

    print(json.dumps(res.json(), indent=2))
