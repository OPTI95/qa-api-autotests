# API-автотесты Swagger Petstore

Набор автотестов на REST API [Swagger Petstore](https://petstore.swagger.io/v2)
с валидацией контракта, отчётами Allure и ежедневным прогоном в GitHub Actions.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-8.3-0A9EDC?logo=pytest&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-2.13-FF6B6B)
![Pydantic](https://img.shields.io/badge/Pydantic-2.10-E92063)

## Что покрыто

**21 тест**: 18 проходят, 3 зафиксированы как известные дефекты.

| Набор | Тестов | Что проверяет |
|---|---|---|
| CRUD | 9 | создание, чтение, обновление, удаление, переходы статусов, фильтр `findByStatus` |
| Негативные | 7 | 404 на несуществующих, битый JSON, нечисловой id, валидация по спецификации |
| Контракт | 5 | схемы ответов, типы полей, заголовки, время ответа |

Найдено и задокументировано **3 расхождения со спецификацией** — см.
[docs/BUGS.md](docs/BUGS.md). Каждое закрыто тестом с `xfail(strict=True)`:
если дефект починят, тест упадёт и заставит обновить документацию.

## Стек

- **pytest** — фикстуры, параметризация, маркеры `smoke` / `regression`
- **requests** — HTTP-клиент с общей сессией
- **pydantic v2** — валидация схем ответов, `extra="forbid"` ловит расширение контракта
- **Allure** — шаги, вложения с телами запроса и ответа, severity
- **GitHub Actions** — прогон на push, PR и по расписанию; отчёт публикуется на Pages

## Запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Только критичный минимум:

```bash
pytest -m smoke
```

Отчёт Allure локально (нужен [Allure CLI](https://allurereport.org/docs/install/)):

```bash
allure serve allure-results
```

Другой стенд — через переменную окружения:

```bash
BASE_URL=https://petstore.swagger.io/v2 pytest
```

## Структура

```
├── src/
│   ├── client.py      # HTTP-клиент: сессия, шаги и вложения Allure
│   ├── pet_api.py     # обёртка над /pet — тесты не знают об URL
│   └── models.py      # pydantic-схемы ответов
├── tests/
│   ├── conftest.py    # фикстуры, генерация данных, уборка после тестов
│   ├── test_crud.py
│   ├── test_negative.py
│   └── test_schema.py
├── docs/BUGS.md       # баг-репорты
└── .github/workflows/tests.yml
```

## Решения, которые стоит пояснить

**Случайные id.** Petstore — общий публичный стенд, на нём одновременно работают
другие люди. Фиксированные идентификаторы приводили бы к конфликтам, поэтому
каждый тест генерирует свой id.

**Уборка через фикстуру.** Созданные питомцы удаляются в `cleanup_ids` независимо
от того, упал тест или прошёл, — прогоны не оставляют мусора и не зависят друг от друга.

**`extra="forbid"` в схемах.** Намеренно строгая проверка: если API начнёт отдавать
новое поле, тест упадёт, и контракт будет пересмотрен осознанно, а не по факту
сломавшегося клиента.

**Типы выведены из ответов, а не из документации.** Например, `createdAt`
у части эндпоинтов приходит числом, хотя выглядит как дата.
