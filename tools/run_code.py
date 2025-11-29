from google import genai
import subprocess
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from google.genai import types

load_dotenv()
client = genai.Client()


def run_code(code: str) -> str:
    """
    Removes markdown-style ```python ... ``` wrappers from code.
    """
    code = code.strip()

    if code.startswith("```"):
        # Remove first line (```python or ```)
        code = code.split("\n", 1)[1]

    if code.endswith("```"):
        # Remove last line (```)
        code = code.rsplit("\n", 1)[0]

    return code.strip()


@tool
def run_code(code: str) -> dict:
    """
    Executes Python code in an isolated temporary file.

    Steps:
    1. Receives raw Python code.
    2. Writes it into LLMFiles/runner.py.
    3. Executes it using `uv run`.
    4. Returns stdout, stderr, and return code.
    """

    try:
        filename = "runner.py"
        os.makedirs("LLMFiles", exist_ok=True)

        # Write code to file
        with open(os.path.join("LLMFiles", filename), "w") as f:
            f.write(code)

        # Execute code
        proc = subprocess.Popen(
            ["uv", "run", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="LLMFiles"
        )

        stdout, stderr = proc.communicate()

        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }
