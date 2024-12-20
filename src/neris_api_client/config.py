from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os

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

    def __post_init__(self):
        # env var handling
        self.base_url = self.base_url or os.getenv("NERIS_BASE_URL")
        self.debug = self.debug if self.debug is not None else os.getenv("NERIS_DEBUG") == "true"

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
