# NERIS API Client

A Python class to interact with the NERIS API programmatically.

## Usage
The client requires a username and password for authentication and authorization of requests unless the `env` argument is set to `local`
at instantiation. The `local` environment is intended for development use on local machines and bypasses auth.

```python
from neris_api_client import NerisApiClient

client = NerisApiClient(username="neris.user@email.co", password="*******", env="dev")

# Get an entity
entity = client.get_entity("FD24027240")
```

API auth tokens are cached locally in `./.token_cache`. If there are auth issues first try instantiating the client with `use_cache=False`
keyword argument or deleting the token cache.

## Disclaimer
The models in this package are generated using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator) and are not guaranteed
to contain all of the information present in the full specification. The generated models are used to validate request payloads prior to
API submission.
