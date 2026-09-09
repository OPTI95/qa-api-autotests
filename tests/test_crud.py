"""Позитивные сценарии жизненного цикла питомца."""
from __future__ import annotations

from typing import Any, Callable

import allure
import pytest

from src.models import PetStatus
from src.pet_api import PetApi


@allure.epic("Petstore API")
@allure.feature("CRUD")
class TestPetCrud:
    @allure.story("Создание")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Питомец создаётся и возвращается с теми же полями")
    @pytest.mark.smoke
    def test_create_pet(
        self,
        pet_api: PetApi,
        pet_payload: Callable[..., dict[str, Any]],
        cleanup_ids: list[int],
    ) -> None:
        payload = pet_payload(name="created-pet")

        response = pet_api.create(payload)

        assert response.status_code == 200, response.text
        cleanup_ids.append(payload["id"])
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["name"] == payload["name"]
        assert body["status"] == payload["status"]

    @allure.story("Чтение")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Созданный питомец доступен по id")
    @pytest.mark.smoke
    def test_get_pet_by_id(self, pet_api: PetApi, created_pet: dict[str, Any]) -> None:
        response = pet_api.get(created_pet["id"])

        assert response.status_code == 200
        assert response.json()["id"] == created_pet["id"]
        assert response.json()["name"] == created_pet["name"]

    @allure.story("Обновление")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("PUT меняет имя и статус питомца")
    @pytest.mark.regression
    def test_update_pet(
        self,
        pet_api: PetApi,
        created_pet: dict[str, Any],
        pet_payload: Callable[..., dict[str, Any]],
    ) -> None:
        updated = pet_payload(
            name="renamed-pet", status=PetStatus.SOLD, id=created_pet["id"]
        )

        response = pet_api.update(updated)

        assert response.status_code == 200
        assert response.json()["name"] == "renamed-pet"
        assert response.json()["status"] == PetStatus.SOLD.value

    @allure.story("Обновление")
    @allure.title("Изменение статуса на «{status}» сохраняется при чтении")
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "status", [PetStatus.PENDING, PetStatus.SOLD], ids=lambda s: s.value
    )
    def test_status_transition_persists(
        self,
        pet_api: PetApi,
        created_pet: dict[str, Any],
        pet_payload: Callable[..., dict[str, Any]],
        status: PetStatus,
    ) -> None:
        pet_api.update(pet_payload(status=status, id=created_pet["id"]))

        response = pet_api.get(created_pet["id"])

        assert response.status_code == 200
        assert response.json()["status"] == status.value

    @allure.story("Удаление")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Удалённый питомец больше недоступен")
    @pytest.mark.smoke
    def test_delete_pet(
        self, pet_api: PetApi, pet_payload: Callable[..., dict[str, Any]]
    ) -> None:
        payload = pet_payload()
        pet_api.create(payload)

        assert pet_api.delete(payload["id"]).status_code == 200

        with allure.step("Проверяем, что питомец действительно удалён"):
            assert pet_api.get(payload["id"]).status_code == 404

    @allure.story("Поиск")
    @allure.title("Фильтр findByStatus отдаёт только питомцев со статусом «{status}»")
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "status",
        [PetStatus.AVAILABLE, PetStatus.PENDING, PetStatus.SOLD],
        ids=lambda s: s.value,
    )
    def test_find_by_status_returns_only_matching(
        self, pet_api: PetApi, status: PetStatus
    ) -> None:
        response = pet_api.find_by_status(status.value)

        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        mismatched = {
            item.get("status") for item in items if item.get("status") != status.value
        }
        assert not mismatched, f"В выдаче есть чужие статусы: {mismatched}"
