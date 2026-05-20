from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


# ── State ────────────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ── LLM ──────────────────────────────────────────────────────────────────────

def get_llm():
    return ChatOllama(model="llama3.2:1b", temperature=0.7)


# ── Node ─────────────────────────────────────────────────────────────────────

def chat_node(state: ChatState):
    llm = get_llm()
    system = SystemMessage(content=(
        "You are a helpful, friendly, and concise AI assistant. "
        "Answer clearly and accurately."
    ))
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


# ── Graph ────────────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(ChatState)
    g.add_node("chat", chat_node)
    g.set_entry_point("chat")
    g.add_edge("chat", END)
    return g.compile()


graph = build_graph()


# ── Public helper ────────────────────────────────────────────────────────────

def get_ai_response(history: list[dict]) -> str:
    """
    history: list of {"role": "user"|"assistant", "content": "..."}
    Returns the AI reply string.
    """
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    result = graph.invoke({"messages": messages})
    last = result["messages"][-1]
    return last.content
