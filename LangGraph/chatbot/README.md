<div align="center">

```
██████╗██╗  ██╗ █████╗ ████████╗██████╗  ██████╗ ████████╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
██║     ███████║███████║   ██║   ██████╔╝██║   ██║   ██║
██║     ██╔══██║██╔══██║   ██║   ██╔══██╗██║   ██║   ██║
╚██████╗██║  ██║██║  ██║   ██║   ██████╔╝╚██████╔╝   ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝  ╚═════╝    ╚═╝
```

### *Graph-Orchestrated Conversational AI · Persistent Memory · Local LLM · Beautiful UI*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1%2B-FF6B6B?style=for-the-badge&logo=graphql&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![SQLite](https://img.shields.io/badge/SQLite-Persistent-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **"From a simple message to a stateful AI response — orchestrated by a graph."**

<br/>

</div>

---

## ✦ What Is This?

**LangGraph Chatbot** is a full-stack conversational AI application that combines graph-based workflow orchestration with a beautiful dark-themed Streamlit interface and fully local LLM inference via Ollama.

Unlike toy chatbot demos, this project demonstrates **real architectural patterns** used in production AI systems:

- 🕸️ **Typed state management** across LLM calls via `StateGraph`
- 📨 **Message accumulation** with LangGraph's `add_messages` reducer
- 🗃️ **Persistent multi-session memory** via SQLite (survives restarts)
- 🎯 **Clean three-layer separation** — Intelligence / Persistence / Presentation

---

## ✦ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│                           app.py                                 │
│  ┌──────────────┐   ┌───────────────────┐   ┌────────────────┐  │
│  │   Sidebar    │   │    Chat Window    │   │  Input Area    │  │
│  │ ─ History   │   │ ─ AI Bubbles     │   │ ─ Chat Input  │  │
│  │ ─ New Chat  │   │ ─ User Bubbles   │   │ ─ Spinner     │  │
│  │ ─ Delete    │   │ ─ Animations    │   │                │  │
│  └──────────────┘   └───────────────────┘   └────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │  get_ai_response(history)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE LAYER                          │
│                          graph.py                                │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────────┐ │
│  │  ChatState  │───▶│  chat_node  │───▶│     ChatOllama       │ │
│  │             │    │             │    │   (llama3.2:1b)      │ │
│  │  messages:  │    │ + System    │    │   Local Inference    │ │
│  │  [BaseMsg]  │    │   Prompt    │    └──────────────────────┘ │
│  └─────────────┘    └─────────────┘                             │
│                                                                  │
│          StateGraph: [ENTRY] ──▶ [chat] ──▶ [END]               │
│          add_messages reducer handles deduplication              │
└────────────────────────────┬─────────────────────────────────────┘
                             │  save_message() / get_messages()
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER                           │
│                           db.py                                  │
│                                                                  │
│  ┌──────────────────────┐    ┌───────────────────────────────┐  │
│  │    conversations     │    │           messages            │  │
│  │  ─────────────────   │    │  ───────────────────────────  │  │
│  │  id        TEXT PK   │◀──▶│  id              INT PK       │  │
│  │  title     TEXT      │    │  conversation_id  TEXT FK     │  │
│  │  created_at TEXT     │    │  role             TEXT        │  │
│  └──────────────────────┘    │  content          TEXT        │  │
│                              │  created_at       TEXT        │  │
│           SQLite             └───────────────────────────────┘  │
│        chat_history.db                                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✦ LangGraph Workflow — Deep Dive

```
  User sends a message
         │
         ▼
  ┌─────────────────────────────────────────────┐
  │  app.py                                     │
  │  1. Append user msg to session_state        │
  │  2. Save user msg → SQLite                  │
  │  3. Build history list of dicts             │
  │  4. Call get_ai_response(history)           │
  └──────────────────────┬──────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────┐
  │  graph.py — get_ai_response()               │
  │                                             │
  │  Convert dicts → BaseMessage objects:       │
  │  {"role":"user"}      → HumanMessage        │
  │  {"role":"assistant"} → AIMessage           │
  └──────────────────────┬──────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────┐
  │  StateGraph.invoke({"messages": [...]})     │
  │                                             │
  │  ChatState = {                              │
  │    messages: Annotated[                     │
  │      list[BaseMessage],                     │
  │      add_messages   ◀── deduplication magic │
  │    ]                                        │
  │  }                                          │
  └──────────────────────┬──────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────┐
  │  chat_node(state)                           │
  │                                             │
  │  llm = ChatOllama(model="llama3.2:1b")      │
  │  system = SystemMessage("You are ...")      │
  │  response = llm.invoke([system]+messages)   │
  │  return {"messages": [AIMessage(response)]} │
  └──────────────────────┬──────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────┐
  │  Back in app.py                             │
  │  1. Extract last message content            │
  │  2. Save AI reply → SQLite                  │
  │  3. Append to session_state.messages        │
  │  4. st.rerun() → re-render chat             │
  └─────────────────────────────────────────────┘
```

---

## ✦ Project Structure

```
chatbot/
│
├── 🎨  app.py               ← Streamlit frontend (UI + session state)
│         ├── Custom CSS     ← Dark theme, gradient bubbles, animations
│         ├── Sidebar        ← Conversation list, new chat, delete
│         └── Chat window    ← Message rendering + input handling
│
├── 🧠  graph.py             ← LangGraph StateGraph (the AI brain)
│         ├── ChatState      ← TypedDict with add_messages reducer
│         ├── chat_node()    ← LLM call with system persona
│         ├── build_graph()  ← Compiles the StateGraph at startup
│         └── get_ai_response() ← Public API consumed by app.py
│
├── 🗃️  db.py                ← SQLite persistence helpers
│         ├── init_db()      ← Creates tables on first run
│         ├── create/get     ← Conversation CRUD operations
│         ├── save/get msgs  ← Message CRUD operations
│         └── update/delete  ← Title update, conversation cleanup
│
├── 📋  requirements.txt     ← All Python dependencies
├── 📖  README.md            ← You are here
└── 💾  chat_history.db      ← Auto-created on first run (SQLite file)
```

---

## ✦ Installation & Setup

### Prerequisites

| Requirement | Minimum Version | Purpose |
|---|:---:|---|
| Python | 3.10+ | Runtime |
| Ollama | Latest | Local LLM inference engine |
| pip | Latest | Package manager |

---

### Step 1 — Install Ollama

```bash
# macOS / Linux (one-liner)
curl -fsSL https://ollama.com/install.sh | sh

# Windows → download installer from https://ollama.com/download
```

### Step 2 — Pull Your Model

```bash
# Lightweight & fast (recommended for most machines)
ollama pull llama3.2:1b

# Better quality (needs ~2GB RAM more)
ollama pull llama3.2:3b

# Best quality (needs ~8GB RAM)
ollama pull mistral

# Verify the model is ready
ollama list
```

### Step 3 — Clone & Install

```bash
git clone https://github.com/yourusername/langgraph-chatbot.git
cd langgraph-chatbot

# Recommended: use a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Step 4 — Launch 🚀

```bash
streamlit run app.py
```

Visit **http://localhost:8501** in your browser. The SQLite database is auto-created on first run. That's it — no `.env` files, no API keys, no cloud setup.

---

## ✦ Configuration

### Switching Models

Only one line to change in `graph.py`:

```python
# Fast (default)
return ChatOllama(model="llama3.2:1b", temperature=0.7)

# Higher quality
return ChatOllama(model="mistral", temperature=0.7)

# Creative / storytelling
return ChatOllama(model="llama3.2:3b", temperature=0.95)

# Precise / factual / code
return ChatOllama(model="llama3.2:1b", temperature=0.1)
```

### Customising the AI Persona

In `graph.py` inside `chat_node()`:

```python
system = SystemMessage(content=(
    "You are a helpful, friendly, and concise AI assistant."
    # Examples of custom personas:
    # "You are a senior Python developer who always includes code examples."
    # "You are a Socratic tutor who answers questions with questions."
    # "You are a witty assistant who uses dry humour in every response."
))
```

### Custom Port

```bash
streamlit run app.py --server.port 8080
```

---

## ✦ Database Schema

Every message is persisted to SQLite immediately after generation. Nothing is ever lost between sessions.

```sql
-- Conversation sessions
CREATE TABLE conversations (
    id          TEXT PRIMARY KEY,   -- UUID (auto-generated)
    title       TEXT NOT NULL,      -- First user message (auto-set)
    created_at  TEXT NOT NULL       -- ISO 8601 timestamp
);

-- Individual messages
CREATE TABLE messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id  TEXT NOT NULL,
    role             TEXT NOT NULL,   -- "user" or "assistant"
    content          TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

Inspect directly anytime:
```bash
sqlite3 chat_history.db
sqlite> SELECT title, created_at FROM conversations ORDER BY created_at DESC;
sqlite> SELECT role, substr(content,1,60) FROM messages WHERE conversation_id='<id>';
sqlite> .quit
```

---

## ✦ Features

| Feature | Status | Notes |
|---|:---:|---|
| Multi-turn conversation | ✅ | Full history sent to LLM every turn |
| Persistent storage | ✅ | SQLite — survives app restarts |
| Multiple sessions | ✅ | Unlimited conversations, all stored |
| Auto-titling | ✅ | First message becomes chat title |
| Delete conversations | ✅ | Cascades — removes messages too |
| Dark theme | ✅ | Custom CSS, gradient bubbles, animations |
| Fully local LLM | ✅ | Ollama — zero API cost, full privacy |
| Model switching | ✅ | One line change in graph.py |
| LangGraph StateGraph | ✅ | Production-ready orchestration pattern |
| Extensible graph | ✅ | Add tools, agents, routers easily |

---

## ✦ Extending the Graph

The single-node graph is intentionally minimal. Here's how to grow it:

### Add a Web Search Tool Node

```python
from langchain_community.tools import DuckDuckGoSearchRun

def search_node(state: ChatState):
    search = DuckDuckGoSearchRun()
    query = state["messages"][-1].content
    result = search.run(query)
    return {"messages": [AIMessage(content=f"[Search Result]\n{result}")]}

# In build_graph():
g.add_node("search", search_node)
g.add_conditional_edges("router", route_fn, {"search": "search", "chat": "chat"})
```

### Add Conversation Summarisation (Long Context Management)

```python
def summarise_node(state: ChatState):
    if len(state["messages"]) > 20:
        summary_prompt = "Summarise this conversation in 3 sentences."
        summary = llm.invoke(state["messages"] + [HumanMessage(summary_prompt)])
        return {"messages": [SystemMessage(f"Summary: {summary.content}")]}
    return state
```

### Enable Streaming Responses

```python
async for chunk in graph.astream({"messages": messages}):
    token = chunk.get("chat", {}).get("messages", [None])[-1]
    if token:
        yield token.content
```

---

## ✦ Tech Stack

```
┌────────────────────────────────────────────┐
│  🎨  Streamlit 1.35+    Frontend & UI       │
│  🦜  LangChain 0.2+     LLM abstraction     │
│  🕸️  LangGraph 0.1+     Graph orchestration │
│  🦙  Ollama             Local inference     │
│  🤖  llama3.2:1b        Default LLM model   │
│  🗃️  SQLite (built-in)  Persistence         │
│  🐍  Python 3.10+       Runtime             │
└────────────────────────────────────────────┘
```

---

## ✦ Troubleshooting

**`Connection refused` — Ollama not running**
```bash
ollama serve           # Start in one terminal
streamlit run app.py   # Run in another terminal
```

**`Model not found` error**
```bash
ollama pull llama3.2:1b
```

**Slow responses**
- Use `llama3.2:1b` (smallest/fastest)
- Set `temperature=0.1` for faster token selection
- On Apple Silicon Macs, Ollama uses GPU automatically

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt --upgrade
```

**Fresh start (delete all conversations)**
```bash
rm chat_history.db
```

---

## ✦ About the Author

Built by **Tejendra Pal Singh**  
B.Tech CSE  
AI Engineer

---

## ✦ License

MIT — free to use, modify, and distribute with attribution.

---

<div align="center">

*Crafted with 🕸️ LangGraph · 🦜 LangChain · 🎨 Streamlit · 🦙 Ollama*

**Star ⭐ the repo if this helped you build something awesome.**

</div>
