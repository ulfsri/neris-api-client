import base64
from http import HTTPStatus
import json
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from pydantic import BaseModel

from .config import Config, GrantType, TokenSet

from .models import (
    IncidentPayload,
    PatchUnitPayload,
    CreateUserPayload,
    DepartmentPayload,
    UpdateUserPayload,
    PatchStationPayload,
    PatchDepartmentPayload,
    CreateDepartmentPayload,
    PatchIncidentAction,
    TypeIncidentStatusValue,
)

__all__ = ("NerisApiClient",)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, requests.structures.CaseInsensitiveDict):
            return {k: v for k, v in obj.items()}

        return super().default(obj)


class _NerisApiClient:
    config: Config
    tokens: TokenSet | None = TokenSet(access_token="", refresh_token="", expires_at=datetime.min)
    _session: requests.Session = requests.Session()

    def __init__(self, config: Config | None = None):
        if config is None:
            config = Config()  # by default it loads from env

        match config.grant_type:
            case GrantType.CLIENT_CREDENTIALS:
                assert config.client_id is not None
                assert config.client_secret is not None
            case GrantType.PASSWORD:
                assert config.username is not None
                assert config.password is not None
            case _:
                raise Exception("Bad grant type. Must be \"password\" or \"client_credentials\"")

        self.config = config

    def _update_auth(self) -> None:
        res: requests.Response | None = None
        token_url: str = f"{self.config.base_url}/token"

        if self.tokens.expires_at <= datetime.now() and not self.tokens.refresh_token:
            match self.config.grant_type:
                case GrantType.PASSWORD:
                    res = self._session.post(
                        token_url,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        data={
                            "grant_type": GrantType.PASSWORD,
                            "username": self.config.username,
                            "password": self.config.password,
                        },
                    )

                case GrantType.CLIENT_CREDENTIALS:
                    client_creds = base64.b64encode(f"{self.config.client_id}:{self.config.client_secret}".encode("utf-8")).decode("utf-8")

                    res = self._session.post(
                        token_url,
                        headers={"Authorization": f"Basic {client_creds}", 'Content-Type': 'application/x-www-form-urlencoded'},
                        data={"grant_type": GrantType.CLIENT_CREDENTIALS},
                    )

        elif self.tokens.expires_at <= datetime.now():
            match self.config.grant_type:
                case GrantType.PASSWORD:
                    res = self._session.post(
                        token_url,
                        # No basic auth needed for Cognito refresh tokens
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        data={
                            "grant_type": "refresh_token",
                            "refresh_token": self.tokens.refresh_token,
                        },
                    )

                case GrantType.CLIENT_CREDENTIALS:
                    res = self._session.post(
                        token_url,
                        headers={"Authorization": f"Basic {client_creds}", 'Content-Type': 'application/x-www-form-urlencoded'},
                        data={
                            "grant_type": "refresh_token",
                            "refresh_token": self.tokens.refresh_token,
                        },
                    )

        if not res:
            return

        while True:
            if self.config.debug:
                print(
                    json.dumps(
                        {
                            "token_response": {
                                "status_code": res.status_code,
                                "headers": res.headers,
                                "content": res.text,
                            }
                        },
                        indent=4,
                        cls=Encoder,
                    ),
                )

            got: dict = res.json()

            # Successfully generated tokens
            if res.status_code == HTTPStatus.OK:
                self.tokens = TokenSet(
                    access_token=got["access_token"],
                    refresh_token=got["refresh_token"],
                    expires_at=datetime.now() + timedelta(seconds=got["expires_in"]),
                )

                break

            # Respond to MFA challenge
            elif res.status_code == HTTPStatus.ACCEPTED:
                code: str = input(f"Provide MFA code for {got['challenge_name']}: ")

                res = self._session.post(
                    token_url,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    data={
                        "grant_type": got["challenge_name"],
                        "username": self.config.username,
                        "session": got["session"],
                        got["challenge_name"]: code,
                    }
                )

    def _call(
        self,
        method: str,
        path: str,
        data: Optional[str | Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        model: Optional[BaseModel] = None,
    ):
        self._update_auth()
        self._session.headers.update({"Authorization": f"Bearer {self.tokens.access_token}"})

        if model:
            if isinstance(data, str):
                data = model.model_validate_json(data).model_dump(mode="json", by_alias=True)
            if isinstance(data, dict):
                data = model.model_validate(data).model_dump(mode="json", by_alias=True)


        res = getattr(self._session, method)(f"{self.config.base_url}{path}", json=data, params=params)

        if self.config.debug:
            print(
                json.dumps(
                    {
                        "request": {
                            "url": f"{self.config.base_url}{path}",
                            "body": data,
                            "headers": self._session.headers,
                            "params": params,
                        },

                        "response": {
                            "status_code": res.status_code,
                            "headers": res.headers,
                            "content": res.text,
                        }
                    },
                    indent=4,
                    cls=Encoder,
                ),
            )

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                e.args = e.args + (e.response.json(),)
            except requests.exceptions.JSONDecodeError as f:
                e.args = e.args + (e.response.text,)
            finally:
                print(str(e))
                return res

        try:
            response = res.json()
        except requests.exceptions.JSONDecodeError:
            response = res.text

        return response


class NerisApiClient(_NerisApiClient):
    def health(self):
        return self._call("get", "/health")

    def get_entity(self, neris_id: str) -> Dict[str, Any]:
        return self._call("get", f"/entity/{neris_id}")

    def create_entity(self, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("post", "/entity/", body, model=CreateDepartmentPayload)

    def update_entity(self, neris_id: str, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("put", f"/entity/{neris_id}", body, model=DepartmentPayload)

    def get_user(self, sub: str | UUID) -> Dict[str, Any]:
        return self._call("get", f"/user/{sub}")

    def create_user(self, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("post", "/user", body, model=CreateUserPayload)

    def update_user(self, sub: str | UUID, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("put", f"/user/{sub}", body, model=UpdateUserPayload)

    def delete_user(self, sub: str | UUID) -> None:
        self._call("delete", f"/user/{sub}")

    def create_user_role_entity_set_attachment(self, sub_user: str | UUID, nuid_role: str | UUID, nuid_entity_set: str | UUID) -> Dict[str, Any]:
        return self._call(
            "post",
            "/auth/user_role_entity_set_attachment",
            params={"sub_user": str(sub_user), "nuid_role": str(nuid_role), "nuid_entity_set": str(nuid_entity_set)},
        )

    def create_user_entity_membership(self, sub: str | UUID, neris_id: str) -> None:
        self._call("post", f"/user/{sub}/user_entity_membership/{neris_id}")

    def delete_user_entity_membership(self, sub: str | UUID, neris_id: str) -> None:
        self._call("delete", f"/user/{sub}/user_entity_membership/{neris_id}")

    def update_user_entity_activation(self, sub: str | UUID, neris_id: str, active: bool) -> None:
        self._call(
            "put",
            f"/user/{sub}/user_entity_activation/{neris_id}",
            data={"active": active},
        )

    def list_user_entity_memberships(self, sub: str | UUID) -> List[Dict[str, Any]]:
        return self._call("get", f"/user/{sub}/user_entity_membership")

    def create_incident(self, neris_id: str, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("post", f"/incident/{neris_id}", data=body, model=IncidentPayload)

    def validate_incident(self, neris_id: str, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call(
            "post", f"/incident/{neris_id}/validate", data=body, model=IncidentPayload
        )

    def patch_entity(self, neris_id: str, body: str | Dict[str, Any]) -> Dict[str, Any]:
        return self._call("patch", f"/entity/{neris_id}", data=body, model=PatchDepartmentPayload)

    def patch_station(
        self, neris_id_entity: str, neris_id_station: str, body: str | Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._call(
            "patch",
            f"/entity/{neris_id_entity}/station/{neris_id_station}",
            data=body,
            model=PatchStationPayload,
        )

    def patch_unit(
        self,
        neris_id_entity: str,
        neris_id_station: str,
        neris_id_unit: str,
        body: str | Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._call(
            "patch",
            f"/entity/{neris_id}/station/{neris_id_station}/unit/{neris_id_unit}",
            data=body,
            model=PatchUnitPayload,
        )

    def patch_incident(
        self, neris_id_entity: str, neris_id_incident: str, body: str | Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._call(
            "patch",
            f"/incident/{neris_id_entity}/{neris_id_incident}",
            data=body,
            model=PatchIncidentAction,
        )

    def update_incident_status(
        self, neris_id_entity: str, neris_id_incident: str, status: TypeIncidentStatusValue
    ) -> Dict[str, Any]:
        return self._call(
            "put",
            f"/incident/{neris_id_entity}/{neris_id_incident}/status",
            data={"status": str(status)},
        )

    def create_api_integration(self, neris_id: str, title: str) -> Dict[str, Any]:
        return self._call("post", f"/account/integration/{neris_id}", data={ "title": title })

    def generate_api_secret(self, client_id: str) -> Dict[str, Any]:
        return self._call("post", f"/account/credential/{client_id}")

    def list_integrations(self, neris_id: str) -> Dict[str, Any]:
        return self._call("get", f"/account/integration/{neris_id}/list")

    def enroll_integration(self, neris_id: str, client_id: UUID | str) -> Dict[str, Any]:
        return self._call("post", f"/account/enrollment/{neris_id}/{client_id}")
