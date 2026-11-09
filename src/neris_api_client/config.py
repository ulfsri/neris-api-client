import os
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


def get_default_user_agent() -> str:
    from . import __version__
    return f"NerisApiClient/{__version__}"


class GrantType(str, Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"


@dataclass
class Config:
    base_url: str | None = None
    debug: bool | None = None
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    grant_type: GrantType | None = None
    validate: bool | None = None
    user_agent: str | None = None
    # True/unset = verify with certifi's bundle, False = disable verification (insecure),
    # or a path to a CA bundle/cert file for environments behind TLS-inspecting proxies.
    ssl_verify: bool | str | None = None

    def __post_init__(self):
        # env var handling
        self.base_url = self.base_url or os.getenv("NERIS_BASE_URL")
        self.debug = self.debug if self.debug is not None else os.getenv("NERIS_DEBUG") == "true"
        self.validate = self.validate if self.validate is not None else os.getenv("NERIS_VALIDATE") == "true"
        self.user_agent = self.user_agent or os.getenv("NERIS_USER_AGENT", get_default_user_agent())

        if self.ssl_verify is None:
            env_ssl_verify = os.getenv("NERIS_SSL_VERIFY")
            if env_ssl_verify:
                if env_ssl_verify.lower() in ("true", "1", "yes"):
                    self.ssl_verify = True
                elif env_ssl_verify.lower() in ("false", "0", "no"):
                    self.ssl_verify = False
                else:
                    self.ssl_verify = env_ssl_verify  # path to CA bundle/cert file

        match os.getenv("NERIS_GRANT_TYPE"):
            case GrantType.PASSWORD:
                self.grant_type = self.grant_type or GrantType.PASSWORD
                self.username = self.username or os.getenv("NERIS_USERNAME")
                self.password = self.password or os.getenv("NERIS_PASSWORD")
            case GrantType.CLIENT_CREDENTIALS:
                self.grant_type = self.grant_type or GrantType.CLIENT_CREDENTIALS
                self.client_id = self.client_id or os.getenv("NERIS_CLIENT_ID")
                self.client_secret = self.client_secret or os.getenv("NERIS_CLIENT_SECRET")


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    expires_at: datetime
