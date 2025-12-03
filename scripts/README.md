# Scripts Directory

Utility scripts for the NFL Play Prediction project.

## Documentation Scraper

### `scrape_nflreadpy_docs.py`

Scrapes the nflreadpy documentation website and saves it for semantic search via the MCP documentation server.

#### Prerequisites

Install scraping dependencies:
```bash
pip install beautifulsoup4 requests
```

Or update your environment:
```bash
conda activate nfl-play-prediction
pip install -r ../requirements.txt
```

#### Usage

```bash
# Run the scraper
python scrape_nflreadpy_docs.py
```

The script will:
1. Fetch documentation pages from https://nflreadpy.nflverse.com
2. Convert HTML to clean Markdown
3. Save to `~/.mcp-documentation-server/uploads/` (or local `docs/scraped/` if MCP directory doesn't exist)
4. Files are automatically indexed by the MCP documentation server

#### What Gets Scraped

- `/api/load_functions/` - All load function signatures
- `/api/configuration/` - Configuration options
- `/guides/` - User guides
- `/guides/caching/` - Caching guide
- `/guides/polars/` - Polars integration guide

#### Adding More Pages

Edit the `PAGES` list in the script:

```python
PAGES = [
    "/api/load_functions/",
    "/your/new/page/",
]
```

#### Using the Indexed Docs

Once scraped and indexed, use the MCP documentation tools in Claude Code:

```python
# Search the docs semantically
search_documents(
    query="load_nextgen_stats parameters",
    max_results=5
)

# AI-powered search (requires GEMINI_API_KEY)
search_documents_with_ai(
    query="What are all the optional parameters for loading NextGen stats?"
)

# List all indexed documents
list_documents()
```

#### Troubleshooting

**"MCP directory not found"**
- The scraper will save locally to `docs/scraped/`
- Make sure the MCP documentation-server is configured in `.mcp.json`
- Restart Claude Code to load the MCP server

**"Failed to scrape page"**
- Check your internet connection
- Verify the URL is correct
- The website might be down or blocking requests

**"Documents not appearing in search"**
- Ensure the MCP server is running (check Claude Code MCP status)
- Files in the uploads folder are auto-indexed
- Try restarting Claude Code

## Future Scripts

Additional utility scripts will be added here as needed:
- Data preprocessing scripts
- Model training scripts
- Evaluation and analysis scripts
