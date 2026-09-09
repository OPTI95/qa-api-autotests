"""Базовый HTTP-клиент: логирование запросов и вложения в Allure-отчёт."""
from __future__ import annotations

import json
from typing import Any

import allure
import requests
from requests import Response


class ApiClient:
    """Тонкая обёртка над requests.Session.

    Каждый вызов оформляется как шаг Allure, а тело запроса и ответа
    прикладываются к отчёту — по упавшему тесту сразу видно, что ушло и что вернулось.
    """

    def __init__(self, base_url: str, timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        with allure.step(f"{method.upper()} {path}"):
            response = self.session.request(method, url, **kwargs)
            self._attach("Request", kwargs.get("json"))
            self._attach("Response", self._safe_json(response))
            allure.attach(
                str(response.status_code),
                name="Status code",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response

    def get(self, path: str, **kwargs: Any) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self.request("DELETE", path, **kwargs)

    @staticmethod
    def _safe_json(response: Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _attach(name: str, payload: Any) -> None:
        if payload is None:
            return
        allure.attach(
            json.dumps(payload, indent=2, ensure_ascii=False),
            name=name,
            attachment_type=allure.attachment_type.JSON,
        )
