import jwt
import json
from enum import Enum
from uuid import UUID
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
from datetime import datetime, timedelta

import boto3
import requests
from pydantic import BaseModel

from .models import (
    IncidentPayload,
    CreateDepartmentPayload,
    DepartmentPayload,
    CreateUserPayload,
    UpdateUserPayload,
)

__all__ = ("NerisApiClient",)


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    LOCAL = "local"
    TEST = "test"


BASE_URLS = {
    Environment.LOCAL: "http://localhost:8000",
    Environment.DEV: "https://api-dev.neris.fsri.org/v1",
    Environment.PROD: "https://api.neris.fsri.org/v1",
    Environment.TEST: "https://api-test.neris.fsri.org/v1",
}

COGNITO_CLIENT_CONFIG_URL = (
    "https://neris-{env}-public.s3.us-east-2.amazonaws.com/cognito_config.json"
)


class _NerisApiClient:
    def __init__(
        self,
        username: str = "",
        password: str = "",
        env: Environment = Environment.LOCAL,
        use_cache: bool = True,
    ):
        self._username = username
        self._password = password
        self._base_url = BASE_URLS[env]
        self._env = env
        self._use_cache = use_cache

        self._access_token: str = None
        self._access_token_exp: datetime = None
        self._refresh_token: str = None
        self._id_token: str = None
        self._id_token_exp: datetime = None
        self._cognito_config = None
        self._session: requests.Session = requests.Session()

        # Don't mess with auth on localhost
        if env == Environment.LOCAL:
            # Non-existent auth token never expires
            self._use_cache = False
            self._access_token_exp = datetime.now() + timedelta(weeks=52)
            return

        self._cognito = boto3.client("cognito-idp")

        self._token_cache_path = Path("./.token_cache")
        self._access_token_cache_path = self._token_cache_path / "access_token"
        self._refresh_token_cache_path = self._token_cache_path / "refresh_token"
        self._id_token_cache_path = self._token_cache_path / "id_token"
        self._cognito_config_cache_path = self._token_cache_path / "cognito_config.json"

        if self._use_cache:
            self._read_token_cache()

        if self._access_token:
            self._set_token_exp()

        if not self._access_token:
            self._initiate_auth()

    def _fetch_cognito_config(f: Callable) -> Callable:
        def fetch_cognito_config(self):
            if self._cognito_config is None:
                self._cognito_config = requests.get(
                    COGNITO_CLIENT_CONFIG_URL.format(env=self._env)
                ).json()
            return f(self)

        return fetch_cognito_config

    @_fetch_cognito_config
    def _initiate_auth(self) -> None:
        res = self._cognito.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": self._username, "PASSWORD": self._password},
            ClientId=self._cognito_config["client_id"],
        )

        self._access_token = res["AuthenticationResult"]["AccessToken"]
        self._refresh_token = res["AuthenticationResult"]["RefreshToken"]
        self._id_token = res["AuthenticationResult"]["IdToken"]

        self._set_token_exp()

        if self._use_cache:
            self._write_token_cache()

    @_fetch_cognito_config
    def _refresh_auth(self) -> None:
        res = self._cognito.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": self._refresh_token},
            ClientId=self._cognito_config["client_id"],
        )

        self._access_token = res["AuthenticationResult"]["AccessToken"]
        self._id_token = res["AuthenticationResult"]["IdToken"]

        self._set_token_exp()

        self._write_token_cache()

    def _set_token_exp(self):
        self._access_token_exp = datetime.fromtimestamp(
            self._decode_token(self._access_token)["exp"]
        )
        self._id_token_exp = datetime.fromtimestamp(
            self._decode_token(self._id_token)["exp"]
        )

    def _read_token_cache(self):
        if self._access_token_cache_path.exists():
            self._access_token = self._access_token_cache_path.read_text()
        if self._refresh_token_cache_path.exists():
            self._refresh_token = self._refresh_token_cache_path.read_text()
        if self._id_token_cache_path.exists():
            self._id_token = self._id_token_cache_path.read_text()
        if self._cognito_config_cache_path.exists():
            self._cognito_config = json.loads(
                self._cognito_config_cache_path.read_text()
            )

    def _write_token_cache(self):
        self._token_cache_path.mkdir(exist_ok=True)
        self._access_token_cache_path.write_text(self._access_token)
        self._refresh_token_cache_path.write_text(self._refresh_token)
        self._id_token_cache_path.write_text(self._id_token)
        self._cognito_config_cache_path.write_text(json.dumps(self._cognito_config))

    @staticmethod
    def _decode_token(token: str, verify: bool = False):
        return jwt.decode(token, options={"verify_signature": verify})

    def _call(
        self,
        method: str,
        path: str,
        data: Optional[str | Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        model: Optional[BaseModel] = None,
    ):
        if self._access_token_exp - datetime.now() <= timedelta(seconds=0):
            try:
                self._refresh_auth()
            except:
                self._initiate_auth()

        if self._env != Environment.LOCAL:
            self._session.headers.update(
                {"Authorization": f"Bearer {self._access_token}"}
            )

        if model:
            if isinstance(data, str):
                data = model.model_validate_json(data).model_dump(
                    mode="json", by_alias=True
                )
            if isinstance(data, dict):
                data = model.model_validate(data).model_dump(mode="json", by_alias=True)

        res = getattr(self._session, method)(
            f"{self._base_url}{path}", json=data, params=params
        )

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                e.args = e.args + (e.response.json(),)
                raise e
            except requests.exceptions.JSONDecodeError as f:
                e.args = e.args + (e.response.text,)
                raise e

        return res.json()


class NerisApiClient(_NerisApiClient):
    def health(self):
        return self._call("get", "/health")

    def get_entity(self, neris_id: str) -> Dict[str, Any]:
        return self._call("get", f"/entity/{neris_id}")

    def create_entity(self, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("post", "/entity/", body, model=CreateDepartmentPayload)

    def update_entity(
        self, neris_id: str, body: str | Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._call("put", f"/entity/{neris_id}", body, model=DepartmentPayload)

    def get_user(self, sub: str | UUID) -> Dict[str, Any]:
        return self._call("get", f"/user/{sub}")

    def create_user(self, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("post", "/user", body, model=CreateUserPayload)

    def update_user(
        self, sub: str | UUID, body: str | Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._call("put", f"/user/{sub}", body, model=UpdateUserPayload)

    def delete_user(self, sub: str | UUID) -> None:
        self._call("delete", f"/user/{sub}")

    def create_user_entity_membership(self, sub: str | UUID, neris_id: str) -> None:
        self._call("post", f"/user/{sub}/user_entity_membership/{neris_id}")

    def delete_user_entity_membership(self, sub: str | UUID, neris_id: str) -> None:
        self._call("delete", f"/user/{sub}/user_entity_membership/{neris_id}")

    def update_user_entity_activation(
        self, sub: str | UUID, neris_id: str, active: bool
    ) -> None:
        self._call(
            "put",
            f"/user/{sub}/user_entity_activation/{neris_id}",
            data={"active": active},
        )

    def list_user_entity_memberships(self, sub: str | UUID) -> List[Dict[str, Any]]:
        return self._call("get", f"/user/{sub}/user_entity_membership")

    def create_incident(
        self, neris_id: str, body: str | Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._call(
            "post", f"/incident/{neris_id}", data=body, model=IncidentPayload
        )
