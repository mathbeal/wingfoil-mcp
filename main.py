"""MCP server exposing Airtable data as tools for AI assistants.

This module bootstraps a FastMCP server named ``diymcp`` and registers
tools that allow MCP-compatible clients to interact with Airtable.

Usage:
    Run directly::

        $ source env.sh
        $ uv run python main.py

    Or via FastMCP CLI::

        $ source env.sh
        $ uv run fastmcp run main.py

Example:
    >>> # The MCP server instance is available as a module attribute.
    >>> from main import mcp
    >>> mcp.name
    'diymcp'
"""

import logging
import sys
from typing import Any

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)

from mcp.server.fastmcp import FastMCP  # noqa: E402

logger: logging.Logger = logging.getLogger(__name__)

mcp: FastMCP = FastMCP("diymcp")


@mcp.tool()
def read_airtable_winds() -> dict[str, list[dict[str, Any]]]:
    """Read all records from the configured Airtable table.

    Fetches records using the Airtable client and returns them in
    MCP content format.

    Returns:
        A dictionary with a ``content`` key containing the records
        serialised as JSON.

    Example:
        >>> callable(read_airtable_winds)
        True
    """
    from airtable_client import list_records

    recs: list[dict[str, Any]] = list_records()
    return {
        "content": [
            {
                "type": "json",
                "json": recs,
            }
        ]
    }


if __name__ == "__main__":
    logger.info("Starting MCP server diymcp")
    mcp.run()
