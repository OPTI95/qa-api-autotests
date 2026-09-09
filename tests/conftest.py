"""Общие фикстуры: клиент, генерация данных и уборка за тестами."""
from __future__ import annotations

import os
import random
from typing import Any, Callable, Iterator

import pytest

from src.client import ApiClient
from src.models import PetStatus
from src.pet_api import PetApi

BASE_URL = os.getenv("BASE_URL", "https://petstore.swagger.io/v2")


@pytest.fixture(scope="session")
def api_client() -> Iterator[ApiClient]:
    client = ApiClient(BASE_URL)
    yield client
    client.session.close()


@pytest.fixture(scope="session")
def pet_api(api_client: ApiClient) -> PetApi:
    return PetApi(api_client)


@pytest.fixture
def pet_payload() -> Callable[..., dict[str, Any]]:
    """Фабрика тел запроса.

    id генерируется случайным, потому что Petstore — общий стенд:
    фиксированные id ломались бы о данные других пользователей.
    """

    def _make(
        name: str = "portfolio-pet",
        status: PetStatus = PetStatus.AVAILABLE,
        **overrides: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": random.randint(10_000_000, 99_999_999),
            "name": name,
            "photoUrls": ["https://example.com/pet.jpg"],
            "category": {"id": 1, "name": "dogs"},
            "tags": [{"id": 1, "name": "qa-portfolio"}],
            "status": status.value,
        }
        payload.update(overrides)
        return payload

    return _make


@pytest.fixture
def created_pet(
    pet_api: PetApi,
    pet_payload: Callable[..., dict[str, Any]],
    cleanup_ids: list[int],
) -> dict[str, Any]:
    """Создаёт питомца перед тестом; удаление берёт на себя cleanup_ids."""
    payload = pet_payload()
    response = pet_api.create(payload)
    assert response.status_code == 200, "Не удалось подготовить питомца для теста"
    cleanup_ids.append(payload["id"])
    return response.json()


@pytest.fixture
def cleanup_ids(pet_api: PetApi) -> Iterator[list[int]]:
    """Список id, которые удаляются после теста, чем бы он ни кончился."""
    ids: list[int] = []
    yield ids
    for pet_id in ids:
        pet_api.delete(pet_id)
