from langchain_core.tools import tool
import requests
import json
from typing import Any, Dict, Optional


@tool
def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Send an HTTP POST request to the given URL with the provided payload.

    Args:
        url (str): The endpoint to send the POST request to.
        payload (Dict[str, Any]): The JSON request body.
        headers (Optional[Dict[str, str]]): Optional HTTP headers.

    Returns:
        Any: Parsed JSON response or raw text.
    """

    headers = headers or {"Content-Type": "application/json"}

    try:
        print(f"\nSending Answer \n{json.dumps(payload, indent=4)}\n to url: {url}")

        response = requests.post(url, json=payload, headers=headers)

        # Raise for 4xx/5xx errors
        response.raise_for_status()

        data = response.json()

        delay = data.get("delay", 0)
        delay = delay if isinstance(delay, (int, float)) else 0

        correct = data.get("correct")

        # If wrong and retry still allowed (<180 seconds)
        if correct is False and delay < 180:
            if "url" in data:
                del data["url"]

        # If >180 seconds time limit reached
        if delay >= 180:
            data = {"url": data.get("url")}

        print("Got the response: \n", json.dumps(data, indent=4), "\n")
        return data

    except requests.HTTPError as e:
        # Extract backend error
        try:
            err = e.response.json()
        except Exception:
            err = e.response.text

        print("HTTP Error Response:\n", err)
        return err

    except Exception as e:
        print("Unexpected error:", e)
        return str(e)
