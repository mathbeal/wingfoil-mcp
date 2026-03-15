"""Airtable REST API client for reading records from a base/table.

This module provides a thin wrapper around the Airtable REST API with
automatic pagination support. Configuration is read from environment
variables.

Environment Variables:
    AIRTABLE_BASE_ID: The Airtable base identifier (starts with ``app``).
    AIRTABLE_TABLE_ID: The table identifier (starts with ``tbl``).
    AIRTABLE_TOKEN: A Personal Access Token with ``data.records:read`` scope.

Example:
    >>> import os
    >>> os.environ.setdefault("AIRTABLE_BASE_ID", "appTEST")
    'appTEST'
    >>> os.environ.setdefault("AIRTABLE_TABLE_ID", "tblTEST")
    'tblTEST'
    >>> os.environ.setdefault("AIRTABLE_TOKEN", "patTEST")
    'patTEST'
"""

import logging
import os
from typing import Any

import requests

logger: logging.Logger = logging.getLogger(__name__)

BASE_ID: str = os.environ.get("AIRTABLE_BASE_ID", "")
TABLE_ID: str = os.environ.get("AIRTABLE_TABLE_ID", "")
TOKEN: str = os.environ.get("AIRTABLE_TOKEN", "")

_API_BASE_URL: str = "https://api.airtable.com/v0"
_DEFAULT_PAGE_SIZE: int = 100
_DEFAULT_MAX_RECORDS: int = 1000
_DEFAULT_TIMEOUT_SECONDS: int = 30


def _validate_config() -> None:
    """Raise if required environment variables are missing.

    Raises:
        RuntimeError: When any of the required env vars is empty.
    """
    missing: list[str] = []
    if not BASE_ID:
        missing.append("AIRTABLE_BASE_ID")
    if not TABLE_ID:
        missing.append("AIRTABLE_TABLE_ID")
    if not TOKEN:
        missing.append("AIRTABLE_TOKEN")
    if missing:
        msg = f"Missing required environment variables: {', '.join(missing)}"
        raise RuntimeError(msg)


def list_records(
    view: str | None = None,
    max_records: int = _DEFAULT_MAX_RECORDS,
) -> list[dict[str, Any]]:
    """Fetch records from the configured Airtable table.

    Handles automatic pagination through the Airtable API, collecting
    all pages up to *max_records*.

    Args:
        view: Optional Airtable view name or ID to filter records.
        max_records: Maximum number of records to return. Defaults to 1000.

    Returns:
        A list of record dictionaries as returned by the Airtable API.

    Raises:
        RuntimeError: If required environment variables are not set.
        requests.HTTPError: If the Airtable API returns a non-2xx response.

    Example:
        >>> # list_records returns a list (requires valid credentials to run)
        >>> callable(list_records)
        True
    """
    _validate_config()

    url: str = f"{_API_BASE_URL}/{BASE_ID}/{TABLE_ID}"
    headers: dict[str, str] = {"Authorization": f"Bearer {TOKEN}"}
    params: dict[str, str | int] = {
        "pageSize": _DEFAULT_PAGE_SIZE,
        "maxRecords": max_records,
    }
    if view:
        params["view"] = view

    records: list[dict[str, Any]] = []

    while True:
        logger.debug("Fetching records from %s (offset=%s)", url, params.get("offset"))
        resp: requests.Response = requests.get(
            url, headers=headers, params=params, timeout=_DEFAULT_TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        records.extend(data.get("records", []))

        offset: str | None = data.get("offset")
        if not offset:
            break
        params["offset"] = offset

    logger.info("Fetched %d records from %s/%s", len(records), BASE_ID, TABLE_ID)
    return records
