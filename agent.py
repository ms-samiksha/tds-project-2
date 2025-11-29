from langgraph.graph import StateGraph, END, START
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_rendered_html, download_file, post_request, run_code, add_dependencies
from typing import TypedDict, Annotated, List
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
RECURSION_LIMIT = 5000

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


TOOLS = [run_code, get_rendered_html, download_file, post_request, add_dependencies]

# -------------------------------------------------
# GEMINI LLM (FREE)
# -------------------------------------------------
rate_limiter = InMemoryRateLimiter(
    requests_per_second=9/60,
    check_every_n_seconds=1,
    max_bucket_size=9
)

llm = init_chat_model(
    model_provider="google_genai",
    model="gemini-2.5-flash",
    rate_limiter=rate_limiter
).bind_tools(TOOLS)

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent.

Your job is to:
1. Load the quiz page from the given URL.
2. Extract ALL instructions, required parameters, submission rules, and the submit endpoint.
3. Solve the task exactly as required.
4. Submit the answer ONLY to the endpoint specified on the current page.
5. Read the server response and:
   - If it contains a new quiz URL → fetch it immediately and continue.
   - If no new URL is present → return "END".

STRICT RULES:
- NEVER hallucinate URLs, JSON fields, or endpoints.
- NEVER modify or shorten URLs.
- ALWAYS include: email={EMAIL} and secret={SECRET} when submitting.
- NEVER stop early.
- Continue until no new URL is returned.
- Then output: END.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages")
])

llm_with_prompt = prompt | llm

# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    result = llm_with_prompt.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}

# -------------------------------------------------
# ROUTING
# -------------------------------------------------
def route(state):
    last = state["messages"][-1]

    tool_calls = None
    if hasattr(last, "tool_calls"):
        tool_calls = last.tool_calls
    elif isinstance(last, dict):
        tool_calls = last.get("tool_calls")

    if tool_calls:
        return "tools"

    content = None
    if hasattr(last, "content"):
        content = last.content
    elif isinstance(last, dict):
        content = last.get("content")

    if isinstance(content, str) and content.strip() == "END":
        return END

    if isinstance(content, list) and content[0].get("text", "").strip() == "END":
        return END

    return "agent"

# -------------------------------------------------
# GRAPH
# -------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")

graph.add_conditional_edges(
    "agent",
    route
)

app = graph.compile()

# -------------------------------------------------
# RUN AGENT
# -------------------------------------------------
def run_agent(url: str):
    app.invoke(
        {"messages": [{"role": "user", "content": url}]},
        config={"recursion_limit": RECURSION_LIMIT},
    )
    print("Tasks completed successfully")
