"""
Scraper for nflreadpy documentation
Fetches documentation pages and saves them for MCP documentation-server indexing
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import sys

# Base URL for nflreadpy documentation
BASE_URL = "https://nflreadpy.nflverse.com"

# Pages to scrape
PAGES = [
    "/api/load_functions/",
    "/api/configuration/",
    "/guides/",
    "/guides/caching/",
    "/guides/polars/",
]

def scrape_page(url: str, output_path: Path) -> bool:
    """
    Scrape a single documentation page and save as markdown

    Args:
        url: Full URL to scrape
        output_path: Path to save the scraped content

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content (try multiple common containers)
        content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_='content') or
            soup.find('div', class_='documentation') or
            soup.body
        )

        if not content:
            print(f"  ⚠️  Warning: Could not find main content in {url}")
            content = soup

        # Extract title
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else url.split('/')[-2]

        # Build markdown content
        md_content = f"# {title_text}\n\n"
        md_content += f"**Source:** {url}\n\n"
        md_content += "---\n\n"

        # Extract and clean text
        # Remove script and style elements
        for script in content(["script", "style", "nav", "footer"]):
            script.decompose()

        # Get text with some structure preserved
        for elem in content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'code', 'li']):
            text = elem.get_text().strip()
            if not text:
                continue

            # Add markdown formatting based on element type
            if elem.name == 'h1':
                md_content += f"\n# {text}\n\n"
            elif elem.name == 'h2':
                md_content += f"\n## {text}\n\n"
            elif elem.name == 'h3':
                md_content += f"\n### {text}\n\n"
            elif elem.name == 'h4':
                md_content += f"\n#### {text}\n\n"
            elif elem.name == 'pre' or elem.name == 'code':
                md_content += f"\n```\n{text}\n```\n\n"
            elif elem.name == 'li':
                md_content += f"- {text}\n"
            else:
                md_content += f"{text}\n\n"

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  ✓ Saved: {output_path.name}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {url}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error processing {url}: {e}")
        return False

def main():
    """Main scraper function"""
    print("=" * 60)
    print("nflreadpy Documentation Scraper")
    print("=" * 60)

    # Determine output directory
    # Use MCP server's uploads directory if it exists, otherwise use local
    mcp_uploads = Path.home() / ".mcp-documentation-server" / "uploads"
    local_uploads = Path(__file__).parent.parent / "docs" / "scraped"

    if mcp_uploads.exists():
        output_dir = mcp_uploads
        print(f"\n📁 Using MCP uploads directory: {output_dir}")
    else:
        output_dir = local_uploads
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 MCP directory not found, using local: {output_dir}")
        print(f"   (MCP server will need to be configured to watch this directory)")

    print(f"\n🔍 Scraping {len(PAGES)} documentation pages...\n")

    successful = 0
    failed = 0

    for page in PAGES:
        url = BASE_URL + page

        # Create safe filename from URL path
        filename = page.strip('/').replace('/', '_')
        if not filename:
            filename = "index"
        filename = f"nflreadpy_{filename}.md"

        output_path = output_dir / filename

        if scrape_page(url, output_path):
            successful += 1
        else:
            failed += 1

        # Be nice to the server
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"✓ Successfully scraped: {successful}/{len(PAGES)} pages")
    if failed > 0:
        print(f"✗ Failed: {failed}/{len(PAGES)} pages")
    print("=" * 60)

    print(f"\n📄 Documentation saved to: {output_dir}")
    print("\n💡 Next steps:")
    print("   1. Configure MCP documentation-server in .mcp.json")
    print("   2. Restart Claude Code to load the MCP server")
    print("   3. Use search_documents tool to query nflreadpy docs")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
