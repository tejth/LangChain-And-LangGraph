import streamlit as st
from db import (
    init_db,
    create_conversation,
    get_all_conversations,
    get_messages,
    save_message,
    update_conversation_title,
    delete_conversation,
)
from graph import get_ai_response

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LangGraph Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit default header */
/* Hide Streamlit default menu + footer only */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e2e;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Sidebar title */
.sidebar-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #a78bfa !important;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* New chat button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
    width: 100%;
    cursor: pointer;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6d28d9, #7c3aed);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
}

/* Conversation list item */
.conv-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 0.9rem;
    border-radius: 10px;
    margin-bottom: 0.4rem;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    background: #1a1a2e;
}
.conv-item:hover { background: #1e1e3a; border-color: #7c3aed33; }
.conv-item.active { background: #2d1b69; border-color: #7c3aed; }
.conv-item .conv-title {
    font-size: 0.85rem;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 140px;
}
.conv-item .conv-date {
    font-size: 0.7rem;
    color: #64748b !important;
}

/* ── Main area ── */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c3aed, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.main-header p {
    color: #64748b;
    font-size: 0.95rem;
}

/* ── Chat messages ── */
.chat-container {
    max-width: 760px;
    margin: 0 auto;
    padding: 1rem 0;
}

.msg-row {
    display: flex;
    margin-bottom: 1.2rem;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.msg-row.user  { justify-content: flex-end; }
.msg-row.ai    { justify-content: flex-start; }

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.avatar.ai-avatar  { background: linear-gradient(135deg, #7c3aed, #a78bfa); margin-right: 0.75rem; }
.avatar.usr-avatar { background: linear-gradient(135deg, #0891b2, #38bdf8); margin-left: 0.75rem; order: 1; }

.bubble {
    max-width: 78%;
    padding: 0.9rem 1.2rem;
    border-radius: 18px;
    font-size: 0.93rem;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble.ai-bubble {
    background: #1e1b4b;
    color: #e2e8f0;
    border-top-left-radius: 4px;
    border: 1px solid #312e81;
}
.bubble.usr-bubble {
    background: linear-gradient(135deg, #0891b2, #0e7490);
    color: #f0f9ff;
    border-top-right-radius: 4px;
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    gap: 5px;
    padding: 1rem 1.2rem;
    background: #1e1b4b;
    border-radius: 18px;
    border-top-left-radius: 4px;
    border: 1px solid #312e81;
    width: fit-content;
}
.dot {
    width: 8px; height: 8px;
    background: #a78bfa;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
    40%            { transform: translateY(-6px); opacity: 1; }
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #475569;
}
.empty-state .icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h3 { font-size: 1.3rem; color: #64748b; margin-bottom: 0.5rem; }
.empty-state p { font-size: 0.9rem; }

/* Input area */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    background: #1e1b4b !important;
    border: 1px solid #312e81 !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e2e8f0 !important;
}

/* Section label in sidebar */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569 !important;
    margin: 1rem 0 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_conversation(conv_id):
    st.session_state.current_conv_id = conv_id
    st.session_state.messages = get_messages(conv_id)


def start_new_conversation():
    conv_id = create_conversation("New Chat")
    st.session_state.current_conv_id = conv_id
    st.session_state.messages = []


def format_date(iso_str):
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return iso_str[:16]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 LangGraph Chat</div>', unsafe_allow_html=True)

    if st.button("✦  New Conversation", use_container_width=True):
        start_new_conversation()
        st.rerun()

    conversations = get_all_conversations()

    if conversations:
        st.markdown('<div class="section-label">Recent Conversations</div>', unsafe_allow_html=True)
        for conv in conversations:
            is_active = conv["id"] == st.session_state.current_conv_id
            active_class = "active" if is_active else ""

            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"💬  {conv['title'][:28]}{'…' if len(conv['title']) > 28 else ''}",
                    key=f"conv_{conv['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    load_conversation(conv["id"])
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{conv['id']}", help="Delete"):
                    delete_conversation(conv["id"])
                    if st.session_state.current_conv_id == conv["id"]:
                        st.session_state.current_conv_id = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.markdown(
            '<p style="color:#475569; font-size:0.82rem; margin-top:1rem;">'
            'No conversations yet. Start a new chat!</p>',
            unsafe_allow_html=True
        )

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="color:#334155; font-size:0.75rem; text-align:center;">'
        'Powered by LangGraph + Ollama</p>',
        unsafe_allow_html=True
    )

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 LangGraph Chatbot</h1>
    <p>Powered by LangGraph · LangChain · Ollama · SQLite</p>
</div>
""", unsafe_allow_html=True)

# Chat area
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if st.session_state.current_conv_id is None or len(st.session_state.messages) == 0:
    if st.session_state.current_conv_id is None:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">💬</div>
            <h3>Start a Conversation</h3>
            <p>Click <strong>"New Conversation"</strong> in the sidebar<br>or select a past chat to continue.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">✨</div>
            <h3>New Chat Started</h3>
            <p>Type a message below to begin!</p>
        </div>
        """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row user">
                <div class="bubble usr-bubble">{msg["content"]}</div>
                <div class="avatar usr-avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row ai">
                <div class="avatar ai-avatar">🤖</div>
                <div class="bubble ai-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
if st.session_state.current_conv_id is not None:
    user_input = st.chat_input("Type your message…")

    if user_input and user_input.strip():
        # Save user message
        save_message(st.session_state.current_conv_id, "user", user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Auto-title from first message
        all_convs = get_all_conversations()
        current = next((c for c in all_convs if c["id"] == st.session_state.current_conv_id), None)
        if current and current["title"] == "New Chat":
            new_title = user_input[:40]
            update_conversation_title(st.session_state.current_conv_id, new_title)

        # Show typing indicator briefly, then get response
        with st.spinner("🤖 Thinking…"):
            try:
                ai_reply = get_ai_response(st.session_state.messages)
            except Exception as e:
                ai_reply = f"⚠️ Error: {e}\n\nMake sure Ollama is running with: `ollama run llama3.2:1b`"

        save_message(st.session_state.current_conv_id, "assistant", ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()
else:
    st.markdown(
        '<p style="text-align:center; color:#475569; font-size:0.85rem; margin-top:1rem;">'
        '← Start or select a conversation from the sidebar</p>',
        unsafe_allow_html=True
    )
