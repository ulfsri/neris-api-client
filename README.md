# NERIS API Client

A Python class to interact with the NERIS API programmatically.

> **NOTE:** Due to the changes and transition to using Oauth 2.0 version 1.2 is now deprecated. Please upgrade to version 1.3. You can do that in a package manager with the following update: `neris-api-client = ">=1.3"` or in your `requirements.txt` you can do `neris-api-client >=1.3`. Or you can install with `pip install neris_api_client>=1.3.`.

## Versioning

This API client does not directly follow semver practices. In order to remove confusion between the NERIS API client and API, we have decided to align the major version of this client with the major version of the API release. The minor and patch versions of this client will differ from API release version, they will instead represent changes made to the API client itself.

## Installation

To install:
```bash
pip install neris-api-client
```
Package published on PyPi: [`NERIS API Client`](https://pypi.org/project/neris-api-client/)

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
    )
)

# Get an entity
entity = client.get_entity("FD24027240")
```

**Using environment varables to instantiate the library**

[Configuration should be stored in the environment](https://12factor.net/config). The following uses `dotenv` to load the configuration, but you can use whatever you like. In the cloud, you might load all of these values into the environment from an encrypted parameter store. 

All variables prefixed are prefixed with `NERIS_`

* See [env.example](./examples/.env.example) for the parameter options. 
* Store the `/env` file in the current working directory. 

```python
from dotenv import load_dotenv
from neris_api_client import NerisApiClient, Config

 # Credentials must be defined in .env
load_dotenv()
client = NerisApiClient()

# Get an entity
entity = client.get_entity("FD24027240")
```

## Disclaimer
The models in this package are generated using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator) and are not guaranteed
to contain all of the information present in the full specification. The generated models are used to validate request payloads prior to
API submission.

## Additional Information
To ask a question, make a suggestion, or otherwise get help with the NERIS API Client, please visit [the NERIS helpdesk](https://neris.atlassian.net/servicedesk/customer/portals).

**Beta sandbox users**:
- Be sure to use the base URL `https://api-test.neris.fsri.org/v1` with the NERIS API Client. You will not be able to authenticate requests in the other environments.
- For the beta testing period, your user is only authorized to perform actions on behalf of the FSRI Fire Department `FD24027214`.
