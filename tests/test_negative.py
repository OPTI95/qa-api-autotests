"""Негативные сценарии и зафиксированные расхождения со спецификацией."""
from __future__ import annotations

from typing import Any, Callable

import allure
import pytest

from src.models import ApiError
from src.pet_api import PetApi

MISSING_ID = 999_999_123


@allure.epic("Petstore API")
@allure.feature("Негативные сценарии")
class TestPetNegative:
    @allure.story("Несуществующий питомец")
    @allure.title("GET по несуществующему id возвращает 404 и тело ошибки")
    @pytest.mark.smoke
    def test_get_missing_pet_returns_404(self, pet_api: PetApi) -> None:
        response = pet_api.get(MISSING_ID)

        assert response.status_code == 404
        error = ApiError.model_validate(response.json())
        assert error.message == "Pet not found"

    @allure.story("Несуществующий питомец")
    @allure.title("DELETE по несуществующему id возвращает 404")
    @pytest.mark.regression
    def test_delete_missing_pet_returns_404(self, pet_api: PetApi) -> None:
        assert pet_api.delete(MISSING_ID).status_code == 404

    @allure.story("Некорректный ввод")
    @allure.title("Нечисловой id не приводит к ошибке сервера")
    @pytest.mark.regression
    def test_non_numeric_id_handled(self, pet_api: PetApi) -> None:
        response = pet_api.get("not-a-number")

        assert response.status_code == 404, "Ожидали 404, а не падение сервера"
        assert response.status_code < 500

    @allure.story("Некорректный ввод")
    @allure.title("Синтаксически битый JSON отклоняется с 400")
    @pytest.mark.regression
    def test_malformed_json_rejected(self, pet_api: PetApi) -> None:
        response = pet_api.client.post(
            "/pet", data='{"name": ', headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400

    @allure.story("Валидация по спецификации")
    @allure.title("BUG-001: питомец без обязательного name создаётся успешно")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.xfail(
        reason="BUG-001: в swagger.json name обязателен, сервер принимает без него",
        strict=True,
    )
    def test_pet_without_required_name_rejected(
        self, pet_api: PetApi, cleanup_ids: list[int]
    ) -> None:
        response = pet_api.create({"id": 91_234_567, "photoUrls": []})

        if response.status_code == 200:
            cleanup_ids.append(91_234_567)
        assert response.status_code == 400

    @allure.story("Валидация по спецификации")
    @allure.title("BUG-002: полностью пустое тело принимается со статусом 200")
    @pytest.mark.regression
    @pytest.mark.xfail(
        reason="BUG-002: пустой объект проходит валидацию и создаёт запись",
        strict=True,
    )
    def test_empty_payload_rejected(self, pet_api: PetApi) -> None:
        assert pet_api.create({}).status_code == 400

    @allure.story("Валидация по спецификации")
    @allure.title("BUG-003: findByStatus принимает несуществующий статус")
    @pytest.mark.regression
    @pytest.mark.xfail(
        reason="BUG-003: спецификация обещает 400 Invalid status value, приходит 200",
        strict=True,
    )
    def test_invalid_status_rejected(self, pet_api: PetApi) -> None:
        assert pet_api.find_by_status("bogus-status").status_code == 400
