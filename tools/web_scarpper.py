from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


@tool
def web_scapper(url: str) -> str:
    """
    Fetch and return the fully rendered HTML of a webpage using Playwright.

    IMPORTANT:
    - ONLY use for real HTML webpages.
    - DO NOT use for direct file URLs (.pdf, .csv, .png, etc.)
      Use `download_file` for that instead.
    """

    print("\nFetching and rendering:", url)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Load and wait for all JS execution
            page.goto(url, wait_until="networkidle")

            # Extract final HTML after JS rendered everything
            content = page.content()

            browser.close()
            return content

    except Exception as e:
        return f"Error fetching/rendering page: {str(e)}"
