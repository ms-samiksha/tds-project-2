from langchain_core.tools import tool
import requests
import os


@tool
def download_file(url: str, filename: str) -> str:
    """
    Download a file from a URL and save it with the given filename
    into an LLMFiles/ directory.

    Args:
        url (str): Direct URL to the file.
        filename (str): The filename to save the downloaded content as.

    Returns:
        str: The saved filename (not full path).
    """

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create folder to store downloaded files
        directory_name = "LLMFiles"
        os.makedirs(directory_name, exist_ok=True)

        path = os.path.join(directory_name, filename)

        # Write file in chunks
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return filename

    except Exception as e:
        return f"Error downloading file: {str(e)}"
