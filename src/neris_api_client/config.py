from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field

class GrantType(StrEnum):
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"

class BaseUrl(StrEnum):
    LOCAL = "http://localhost:8000"
    DEV = "https://api-dev.neris.fsri.org/v1"
    TEST = "https://api-test.neris.fsri.org/v1"
    PROD = "https://api.neris.fsri.org/v1"


class Config(BaseModel):
    base_url: str = BaseUrl.PROD
    debug: bool = False
    username: Optional[str] = Field(
        description="The username if grant_type is ""password""", default=None
    )
    password: Optional[str] = Field(
        description="The password if grant_type is ""password""", default=None
    )
    client_id: Optional[str] = Field(
        description="The client id if grant_type is ""client_credentials""", default=None
    )
    client_secret: Optional[str] = Field(
        description="The client secret if grant_type is ""client_credentials""", default=None
    )
    refresh_token: Optional[str] = Field(
        description="The refresh token if the grant_type is ""refresh_token""", default=None
    )
    grant_type: GrantType = Field(
        description='requested grant_type. options are "client_credentials", "password", or "refresh_token"',
    )

@dataclass
class TokenSet:
    access_token: str 
    refresh_token: str
    expires_at: datetime