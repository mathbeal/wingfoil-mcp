# wingfoil-mcp

**An MCP server that lets an AI assistant query your Airtable base directly —
shown here on seven months of wind readings across twelve French wingfoil spots.**

![Wingfoil spots in France, scored and mapped by Claude](results/claude_spots.png)

> **Asked:** *Which spot has the longest streak of consecutive ideal wingfoil days,
> according to the satisfaction score?*

Claude produced the map above by calling a single tool from this server. No plugin,
no scraping, no orchestration framework — about ninety lines of Python over the
Airtable REST API.

---

## What it is

Giving a language model access to your own structured data usually means either
copying it into the prompt or building an integration. The Model Context Protocol
removes that choice: the model calls a tool, your code answers.

This repository is the smallest useful example of that. It wraps one Airtable table
as one MCP tool, and it is meant to be **forked and pointed at your own base** —
wind readings here, but the code neither knows nor cares what the records contain.

Read it in one sitting: `airtable_client.py` fetches and paginates, `main.py`
registers the tool. That is the whole program.

## Quick start

**Requirements:** Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/mathbeal/wingfoil-mcp
cd wingfoil-mcp
uv sync
```

Create `env.sh` with your three Airtable values:

```bash
export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
export AIRTABLE_TABLE_ID="tblXXXXXXXXXXXXXX"
export AIRTABLE_TOKEN="patXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

Check that the client reaches your data before wiring anything to Claude:

```bash
source env.sh
uv run python -c "from airtable_client import list_records; print(len(list_records()), 'records')"
```

If that prints a count, everything downstream will work.

## Connect it to Claude Desktop

Edit the configuration file:

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Add an entry under `mcpServers` (create the file if it does not exist), replacing
`/path/to/wingfoil-mcp` with your clone:

```json
{
  "mcpServers": {
    "wingfoil": {
      "command": "/path/to/wingfoil-mcp/.venv/bin/python",
      "args": ["/path/to/wingfoil-mcp/main.py"],
      "env": {
        "AIRTABLE_BASE_ID": "appXXXXXXXXXXXXXX",
        "AIRTABLE_TABLE_ID": "tblXXXXXXXXXXXXXX",
        "AIRTABLE_TOKEN": "patXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
      }
    }
  }
}
```

<details>
<summary>Running from WSL on Windows</summary>

```json
{
  "mcpServers": {
    "wingfoil": {
      "command": "wsl.exe",
      "args": ["bash", "-lc",
        "cd ~/wingfoil-mcp && source .venv/bin/activate && source env.sh && python main.py"]
    }
  }
}
```
</details>

Restart Claude Desktop. The tool appears in the tool list; ask a question about your
data and watch it get called.

## The tool

One tool, deliberately:

| Tool | Returns |
|---|---|
| `read_airtable_winds()` | every record of the configured table, as JSON |

The model does the filtering, ranking and reasoning. Pushing query logic into the
tool is possible, but on a table of this size it buys nothing and costs flexibility.

You can also run the server through the FastMCP CLI:

```bash
source env.sh
uv run fastmcp run main.py
```

## What that makes possible

Ask for a ranking and the model works across the whole dataset — streaks, averages,
seasonality — none of which is coded anywhere:

![Ranked wingfoil spots with ideal-day streaks and wind averages](results/claude_results.png)

## Airtable setup

Generate a Personal Access Token at
[airtable.com/create/tokens](https://airtable.com/create/tokens) with at least the
`data.records:read` scope on the target base.

| Variable | Description |
|---|---|
| `AIRTABLE_BASE_ID` | ID of your base — starts with `app` |
| `AIRTABLE_TABLE_ID` | ID of the table to read — starts with `tbl` |
| `AIRTABLE_TOKEN` | Personal Access Token — starts with `pat` |

The client follows pagination and fetches up to 1000 records by default.

## Layout

```
main.py             the FastMCP server and its single tool
airtable_client.py  REST client, authentication and pagination
results/            the screenshots above
```

## Licence

MIT — voir [LICENSE](LICENSE).
