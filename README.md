# NERIS API Client

A Python class to interact with the NERIS API programmatically.

> **NOTE:** Due to the changes and transition to using Oauth 2.0 version 1.2 is now deprecated. Please upgrade to version 1.3. You can do that in a package manager with the following update: `neris-api-client = ">=1.3"` or in your `requirements.txt` you can do `neris-api-client >=1.3`. Or you can install with `pip install neris_api_client>=1.3.`.

## Versioning

This API client does not directly follow semver practices. In order to remove confusion between the NERIS API client and API, we have decided to align the major version of this client with the major version of the API release. The minor and patch versions of this client will differ from API release version, they will instead represent changes made to the API client itself.

## Installation

Requires Python 3.10 or later.

To install:

```bash
pip install neris-api-client
```

Package published on PyPi: [`NERIS API Client`](https://pypi.org/project/neris-api-client/)

## Model generation

Install the locked development dependencies with `pipenv sync --dev`. The
[generation script](./gen) downloads the live OpenAPI specification and overwrites
[models.py](./src/neris_api_client/models.py), then formats it with Black.
From a Bash shell, run `pipenv run bash gen`.

Schema downloads explicitly use the generator's HTTPX2 backend, which
datamodel-code-generator 0.76.2 labels experimental. HTTPX2 is pinned to 2.14.0
to retain Python 3.10 support; HTTPX2 2.15 and later require Python 3.11.
For manual `pipenv run datamodel-codegen` commands, include `--http-backend httpx2`
so an installed copy of HTTPX does not take precedence.
This development dependency does not change the client's Requests-based HTTP transport.

## Usage

**Auth with password `auth` flow**

All config parameters can be specified as environment variables prefixed with `NERIS_` e.g. `NERIS_GRANT_TYPE=password`.

```python
from neris_api_client import NerisApiClient, Config

client = NerisApiClient(
    Config(
        base_url="https://api-test.neris.fsri.org/v1",
        grant_type="password",
        username="neris.user@email.co",
        password="*******",
        # Supply a custom user agent header value
        user_agent="MyApp/1.0",
    )
)

# Get an entity
entity = client.get_entity("FD24027240")

# If MFA enabled, prompt for auth challenge answer
Provide MFA code for email_otp: ******
```

**Auth with `client_credentials` auth flow**

All config parameters can be specified as environment variables prefixed with `NERIS_` e.g. `NERIS_GRANT_TYPE=client_credentials`.

```python
from neris_api_client import NerisApiClient, Config

client = NerisApiClient(
    Config(
        base_url="https://api-test.neris.fsri.org/v1",
        grant_type="client_credentials",
        client_id="********************",
        client_secret="***************",
        # Supply a custom user agent header value
        user_agent="FireFirst/1.0",
    )
)

# Get an entity
entity = client.get_entity("FD24027240")
```

**Using environment varables to instantiate the library**

[Configuration should be stored in the environment](https://12factor.net/config). The following uses `dotenv` to load the configuration, but you can use whatever you like. In the cloud, you might load all of these values into the environment from an encrypted parameter store.

All variables prefixed are prefixed with `NERIS_`

- See [env.example](./examples/.env.example) for the parameter options.
- Store the `/env` file in the current working directory.

```python
from dotenv import load_dotenv
from neris_api_client import NerisApiClient, Config

 # Credentials must be defined in .env
load_dotenv()
client = NerisApiClient()

# Get an entity
entity = client.get_entity("FD24027240")
```

## Additional config parameters

### `debug`

Controls whether the application outputs debug information.

### `validate`

Controls whether the client performs model validations.

### `ssl_verify`

Controls TLS certificate verification. `True`/unset verifies with the default certifi bundle, `False` disables
verification (not recommended), or pass a path to a custom CA bundle.

> **⚠️ Warning:** Setting `ssl_verify=False` disables all TLS certificate verification, including protection against
> man-in-the-middle attacks. Credentials, tokens, and incident data would be sent over a connection that cannot
> confirm it's actually talking to the NERIS API. Only use this as a last resort for local debugging, never in
> production, and prefer supplying a custom CA bundle path instead.

### Troubleshooting `SSLCertVerificationError` / `unable to get local issuer certificate`

If you see `SSLCertVerificationError: unable to get local issuer certificate`, your network traffic is likely passing
through a TLS-inspecting proxy or firewall (common in corporate networks and hosted notebook environments such as
ArcGIS Online Notebooks) that re-signs traffic with its own root certificate, which isn't trusted by Python's
default certificate bundle. To resolve this, obtain the proxy/organization's root CA certificate (as a `.pem` file)
from your network/IT administrator and point the client at it:

```python
client = NerisApiClient(
    Config(
        ...,
        ssl_verify="/path/to/corporate-ca-bundle.pem",
    )
)
```

Or set the `NERIS_SSL_VERIFY` environment variable to the path of the CA bundle. If you don't have access to the CA
bundle, confirm with your network administrator that outbound HTTPS access to `api.neris.fsri.org` is allowed.

## Disclaimer

The models in this package are generated using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator) and are not guaranteed
to contain all of the information present in the full specification. The generated models are used to validate request payloads prior to
API submission.

## Additional Information

To ask a question, make a suggestion, or otherwise get help with the NERIS API Client, please visit [the NERIS helpdesk](https://neris.atlassian.net/servicedesk/customer/portals).

**Beta sandbox users**:

- Be sure to use the base URL `https://api-test.neris.fsri.org/v1` with the NERIS API Client. You will not be able to authenticate requests in the other environments.
- For the beta testing period, your user is only authorized to perform actions on behalf of the FSRI Fire Department `FD24027214`.
