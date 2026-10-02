from __future__ import annotations

from copy import deepcopy
from typing import Any

_ATTEMPT_STORE: dict[str, dict[str, Any]] = {}


def save_attempt(attempt_id: str, payload: dict[str, Any]) -> None:
    _ATTEMPT_STORE[attempt_id] = deepcopy(payload)


def get_attempt(attempt_id: str | None) -> dict[str, Any] | None:
    if not attempt_id:
        return None
    attempt = _ATTEMPT_STORE.get(attempt_id)
    return deepcopy(attempt) if attempt else None


def update_attempt(attempt_id: str, payload: dict[str, Any]) -> None:
    _ATTEMPT_STORE[attempt_id] = deepcopy(payload)


def clear_attempt(attempt_id: str | None) -> None:
    if attempt_id:
        _ATTEMPT_STORE.pop(attempt_id, None)
