"""Проверка контракта: структура и типы полей в ответах."""
from __future__ import annotations

from typing import Any, Callable

import allure
import pytest

from src.models import Pet
from src.pet_api import PetApi


@allure.epic("Petstore API")
@allure.feature("Контракт")
class TestPetSchema:
    @allure.story("Схема ответа")
    @allure.title("Ответ на создание соответствует схеме Pet")
    @pytest.mark.smoke
    def test_create_response_matches_schema(
        self,
        pet_api: PetApi,
        pet_payload: Callable[..., dict[str, Any]],
        cleanup_ids: list[int],
    ) -> None:
        payload = pet_payload()

        response = pet_api.create(payload)
        cleanup_ids.append(payload["id"])

        pet = Pet.model_validate(response.json())
        assert pet.id == payload["id"]
        assert pet.photo_urls == payload["photoUrls"]
        assert pet.category is not None and pet.category.name == "dogs"

    @allure.story("Схема ответа")
    @allure.title("Ответ на чтение соответствует схеме Pet")
    @pytest.mark.regression
    def test_get_response_matches_schema(
        self, pet_api: PetApi, created_pet: dict[str, Any]
    ) -> None:
        response = pet_api.get(created_pet["id"])

        Pet.model_validate(response.json())

    @allure.story("Схема ответа")
    @allure.title("Каждый элемент выдачи findByStatus соответствует схеме Pet")
    @pytest.mark.regression
    def test_find_by_status_items_match_schema(self, pet_api: PetApi) -> None:
        items = pet_api.find_by_status("available").json()

        assert items, "Выдача пуста — проверить нечего"
        for item in items[:25]:
            Pet.model_validate(item)

    @allure.story("Заголовки")
    @allure.title("Content-Type ответа — application/json")
    @pytest.mark.smoke
    def test_content_type_is_json(
        self, pet_api: PetApi, created_pet: dict[str, Any]
    ) -> None:
        response = pet_api.get(created_pet["id"])

        assert "application/json" in response.headers.get("Content-Type", "")

    @allure.story("Стабильность")
    @allure.title("Ответ приходит быстрее 5 секунд")
    @pytest.mark.regression
    def test_response_time_within_limit(
        self, pet_api: PetApi, created_pet: dict[str, Any]
    ) -> None:
        response = pet_api.get(created_pet["id"])

        elapsed = response.elapsed.total_seconds()
        assert elapsed < 5, f"Ответ шёл {elapsed:.2f} с"
