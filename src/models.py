"""Схемы Petstore. Типы сверены с фактическими ответами и swagger.json."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PetStatus(str, Enum):
    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"


class Category(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int | None = None
    name: str | None = None


class Tag(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int | None = None
    name: str | None = None


class Pet(BaseModel):
    """Ответ /pet.

    По спецификации name и photoUrls обязательны, но сервер отдаёт объекты
    и без них — см. docs/BUGS.md, BUG-001.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: int
    name: str | None = None
    photo_urls: list[str] | None = Field(default=None, alias="photoUrls")
    category: Category | None = None
    tags: list[Tag] | None = None
    status: str | None = None


class ApiError(BaseModel):
    """Тело ошибки: {"code":1,"type":"error","message":"Pet not found"}"""

    model_config = ConfigDict(extra="forbid")
    code: int
    type: str
    message: str
