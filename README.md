# Screenshot tagger

Small pipeline that ingests images from a folder, asks a **local** [Ollama](https://ollama.com/) vision model to describe each screenshot and pick a tag, and stores the results in **SQLite** so you can search by filename, tag, or description.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or another way to install dependencies
- [Ollama](https://ollama.com/) running locally, with a vision model pulled (the code uses **`llava:7b`** by default):

  ```bash
  ollama pull llava:7b
  ```

The Python `ollama` client talks to the default Ollama HTTP API at `http://127.0.0.1:11434` unless you override it with the `OLLAMA_HOST` environment variable.

## Install

```bash
uv sync
```

## CLI (`main.py`)

From the repository root:

| Action | Command |
|--------|---------|
| Ingest all `.png` / `.jpg` / `.jpeg` in a directory | `uv run python main.py --dir /path/to/images` |
| Shortcuts for common folders | `uv run python main.py --dir desktop` (also `documents`, `downloads`) |
| Search the database | `uv run python main.py --query "dashboard"` |
| Ingest then search | `uv run python main.py --query "cat" --add --dir ~/Pictures` |
| Tag counts and unique tags | `uv run python main.py --stats` |

On first run, `init_db()` creates `data/screenshots.db` if it does not exist. Already-ingested paths (same `file_path`) are skipped.

## Project layout

| Path | Role |
|------|------|
| `src/tag.py` | Calls Ollama with structured JSON (Pydantic schema) for description + tag + tag suggestions |
| `src/storage.py` | SQLite access: ingest, search, stats, tag helpers |
| `schema/01.sql` | Reference DDL for the `screenshots` table |
| `describe-image.py` | Minimal script: one image path → free-form caption |
| `src/derive.py` | Similar exploratory script with a different prompt |
| `notebooks/01.ipynb` | Notebook experiments |

## Configuration notes

- **Model name** is hard-coded as `llava:7b` in `src/tag.py`, `describe-image.py`, and `src/derive.py`. Change it there if you use another vision model.
- **Default tag menu** used in prompts lives in `src/tag.py` (`default_starting_tags`).

## License

See the repository’s license file if one is present; otherwise treat usage as defined by the project owner.
