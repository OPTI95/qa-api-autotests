"""Обёртка над ресурсом /pet — тесты не знают о путях и деталях HTTP."""
from __future__ import annotations

from typing import Any

from requests import Response

from src.client import ApiClient

RESOURCE = "/pet"


class PetApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict[str, Any]) -> Response:
        return self.client.post(RESOURCE, json=payload)

    def get(self, pet_id: int | str) -> Response:
        return self.client.get(f"{RESOURCE}/{pet_id}")

    def update(self, payload: dict[str, Any]) -> Response:
        return self.client.put(RESOURCE, json=payload)

    def delete(self, pet_id: int | str) -> Response:
        return self.client.delete(f"{RESOURCE}/{pet_id}")

    def find_by_status(self, status: str) -> Response:
        return self.client.get(f"{RESOURCE}/findByStatus", params={"status": status})
