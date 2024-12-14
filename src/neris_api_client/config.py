from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os

class GrantType(str, Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"

@dataclass
class Config:
    base_url: str = "https://api.neris.fsri.org/v1"
    debug: bool = False
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    grant_type: GrantType | None = None

    def __post_init__(self):
        # env var overrides
        if os.getenv("NERIS_BASE_URL"):
            self.base_url = os.environ["NERIS_BASE_URL"]

        if os.getenv("NERIS_DEBUG"):
            self.debug = os.environ["NERIS_DEBUG"]

        match os.getenv("NERIS_GRANT_TYPE"):
            case GrantType.PASSWORD:
                self.grant_type = GrantType.PASSWORD
                self.username = os.getenv("NERIS_USERNAME")
                self.password = os.getenv("NERIS_PASSWORD")
            case GrantType.CLIENT_CREDENTIALS:
                self.grant_type = GrantType.CLIENT_CREDENTIALS
                self.client_id = os.getenv("NERIS_CLIENT_ID")
                self.client_secret = os.getenv("NERIS_CLIENT_SECRET")


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    expires_at: datetime
