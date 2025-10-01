import streamlit as st
from streamlit_lottie import st_lottie
from langchain_core.messages import AIMessage, HumanMessage
from .custom_responses import CUSTOM_RESPONSES #
import os
import json
import hashlib
import datetime
import uuid
import re

# Constants
HISTORY_FILE = "archived/chats_history/history.json"
LOTTIE_PATH = "assets/lottie/welcome.json"
SAVED_CHAT_DIR = "archived/saved_chats"

 # Get the absolute path of the current file (main.py or this module)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure required directories exist
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
os.makedirs(SAVED_CHAT_DIR, exist_ok=True)


# -------------------- 🔑 UTILS --------------------

def generate_cid() -> str:
    """Generate a unique chat ID based on timestamp and UUID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_part = uuid.uuid4().hex[:6]
    return f"cid_{timestamp}_{random_part}"


def compute_chat_hash(chat_history) -> str:
    """Compute a SHA256 hash of the entire chat content for de-duplication"""
    try:
        content = "".join([msg.content for msg in chat_history])
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    except Exception:
        return None

def sanitize_text(text: str) -> str:
    """Remove extra whitespace, HTML tags, and sanitize text for display or filenames."""
    try:
        text = re.sub(r'<.*?>', '', text)            # Remove HTML tags
        text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)  # Remove special characters
        text = re.sub(r'\s+', ' ', text).strip()     # Normalize whitespace
        return text[:80]                             # Limit to 80 chars
    except Exception:
        return "Untitled"

def generate_chat_title(chat_history) -> str:
    """Generate a readable title from the first user message."""
    try:
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                first_msg = msg.content.strip()
                break
        else:
            return "Untitled Chat"

        title = sanitize_text(first_msg)
        if len(title) > 45:
            title = title[:45].rsplit(" ", 1)[0] + "..."
        return title or "Untitled Chat"
    except Exception:
        return "Untitled Chat"

def save_to_history(chat_history):
    """Save the current chat to history.json, avoiding duplicates."""
    try:
        if not chat_history:
            return

        history_data = {}
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history_data = json.load(f)

        # Generate unique CID and hash
        chat_hash = compute_chat_hash(chat_history)
        for existing in history_data.values():
            if existing.get("hash") == chat_hash:
                return  # Chat already exists, skip save

        cid = generate_cid()
        title = generate_chat_title(chat_history)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formatted_chat = []
        for m in chat_history:
            if isinstance(m, HumanMessage):
                formatted_chat.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                formatted_chat.append({"role": "ai", "content": m.content})
            elif isinstance(m, dict):
                formatted_chat.append({
                    "role": m.get("role", "unknown"),
                    "content": m.get("content", "")
                })
            else:
                continue  # Unknown format

        history_data[cid] = {
            "title": title,
            "hash": chat_hash,
            "timestamp": timestamp,
            "chat": formatted_chat
        }

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        st.error(f"Failed to save history: {e}")

def load_chat_history():
    """Load all chats from history.json, sorted by timestamp (latest first)."""
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            st.error("Chat history file is corrupted or has invalid format.")
            return {}

        # Sort by timestamp descending
        sorted_data = dict(
            sorted(
                data.items(),
                key=lambda item: item[1].get("timestamp", ""),
                reverse=True
            )
        )
        return sorted_data

    except Exception as e:
        st.error(f"❌ Failed to load chat history: {e}")
        return {}
    
def remove_from_history(cid: str):
    """Remove a specific chat from history.json using its CID."""
    if not os.path.exists(HISTORY_FILE):
        st.warning("No chat history found.")
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        if cid in history_data:
            del history_data[cid]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2)
            st.success(f"Removed chat history: {cid}")
        else:
            st.warning("Chat ID not found in history.")

    except Exception as e:
        st.error(f"Failed to remove history: {e}")

def clear_chat_history():
    """Clear all chat history by resetting history.json."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        st.success("All chat history cleared successfully.")
    except Exception as e:
        st.error(f"Failed to clear history: {e}")

def save_chat(chat_history):
    """Save the current chat to the saved_chats/ directory as a JSON file."""
    if not chat_history:
        st.warning("No chat to save.")
        return

    try:
        cid = generate_cid()
        title = generate_chat_title(chat_history)
        filename = f"{cid}_{title}.json"
        filepath = os.path.join(SAVED_CHAT_DIR, filename)

        chat_data = {
            "cid": cid,
            "title": title,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chat": [
                {"role": "user" if isinstance(m, HumanMessage) else "ai", "content": m.content}
                for m in chat_history
            ]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=2)

        st.success(f"Chat saved as: {filename}")
    except Exception as e:
        st.error(f"Failed to save chat: {e}")

def load_saved_chats():
    """Load all saved chats from saved_chats/ folder with metadata."""
    saved_chats = {}

    if not os.path.exists(SAVED_CHAT_DIR):
        return {}

    try:
        for filename in os.listdir(SAVED_CHAT_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(SAVED_CHAT_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                cid = data.get("cid") or filename.replace(".json", "")
                title = data.get("title", "Untitled")
                timestamp = data.get("timestamp", "")

                saved_chats[cid] = {
                    "title": title,
                    "timestamp": timestamp,
                    "file": filepath,
                    "chat": data.get("chat", [])
                }

        # Sort by latest timestamp
        sorted_chats = dict(
            sorted(
                saved_chats.items(),
                key=lambda item: item[1].get("timestamp", ""),
                reverse=True
            )
        )
        return sorted_chats

    except Exception as e:
        st.error(f"Failed to load saved chats: {e}")
        return {}

def clear_saved_chats():
    """Delete all saved chat files from the saved_chats/ directory."""
    if not os.path.exists(SAVED_CHAT_DIR):
        st.warning("Saved chat directory does not exist.")
        return

    try:
        count = 0
        for filename in os.listdir(SAVED_CHAT_DIR):
            filepath = os.path.join(SAVED_CHAT_DIR, filename)
            if os.path.isfile(filepath) and filename.endswith(".json"):
                os.remove(filepath)
                count += 1
        st.success(f"Cleared {count} saved chat(s).")
    except Exception as e:
        st.error(f"Failed to clear saved chats: {e}")

def download_saved_chat(cid):
    """Load and prepare a saved chat for download by CID."""
    saved_chats = load_saved_chats()
    chat_data = saved_chats.get(cid)

    if not chat_data:
        st.warning("Saved chat not found.")
        return

    try:
        with open(chat_data["file"], "r", encoding="utf-8") as f:
            content = f.read()

        st.download_button(
            label="📥 Download Chat",
            file_name=os.path.basename(chat_data["file"]),
            mime="application/json",
            data=content,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Download failed: {e}")

def remove_saved_chat(cid: str):
    """Delete a specific saved chat by its CID from saved_chats/ folder."""
    saved_chats = load_saved_chats()
    chat_data = saved_chats.get(cid)

    if not chat_data:
        st.warning("Saved chat not found.")
        return

    try:
        os.remove(chat_data["file"])
        st.success(f"Removed saved chat: {chat_data['title']}")
    except Exception as e:
        st.error(f"Failed to remove saved chat: {e}")

def open_saved_chat(cid: str) -> list:
    """Load a saved chat from file and return as LangChain message objects."""
    saved_chats = load_saved_chats()
    chat_data = saved_chats.get(cid)

    if not chat_data:
        st.warning("Saved chat not found.")
        return []

    try:
        with open(chat_data["file"], "r", encoding="utf-8") as f:
            data = json.load(f)

        chat_history = []
        for msg in data.get("chat", []):
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                chat_history.append(AIMessage(content=msg["content"]))

        st.success(f"Loaded saved chat: {chat_data['title']}")
        return chat_history

    except Exception as e:
        st.error(f"Failed to load saved chat: {e}")
        return []

def handle_new_chat():
    """Reset session state to start a fresh new chat session."""
    # Clear chat history and input
    st.session_state.chat_history = []
    st.session_state.chat_input = ""

    # Clear identifiers for current chat
    st.session_state.chat_index = None
    st.session_state.opened_chat_cid = None
    st.session_state.current_chat_title = "New Chat"

    # Flags or tracking variables
    st.session_state.from_saved_chat = False
    st.session_state.from_history = False
    st.session_state.chat_loaded = False
    st.session_state.chat_hash = None
    st.session_state.cid = generate_cid()  # prepare new chat CID

    # Clear sidebar states (if you add chat selection)
    st.session_state.selected_saved_chat = None
    st.session_state.selected_history_chat = None

    # Refresh the UI
    st.rerun()

def open_chat_from_history(cid: str) -> list:
    """Load a specific chat by CID from the shared history.json file."""
    if not os.path.exists(HISTORY_FILE):
        st.warning("Chat history file not found.")
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        if cid not in history_data:
            st.warning("Chat not found in history.")
            return []

        chat_entry = history_data[cid]
        chat_history = []

        for msg in chat_entry.get("chat", []):
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                chat_history.append(AIMessage(content=msg["content"]))

        st.success(f"Loaded chat from history: {chat_entry.get('title', 'Untitled')}")
        return chat_history

    except Exception as e:
        st.error(f"Failed to open chat from history: {e}")
        return []

def handle_next_chat():
    """Navigate to the next chat (history or saved), update session and rerun."""
    all_chats = list(load_chat_history().keys())  # or load_saved_chats() if using saved
    if not all_chats:
        st.warning("No chats available.")
        return

    # Initialize index if not set
    if st.session_state.get("chat_index") is None:
        st.session_state.chat_index = 0
    else:
        st.session_state.chat_index = (st.session_state.chat_index + 1) % len(all_chats)

    # Get next chat CID
    cid = all_chats[st.session_state.chat_index]
    loaded_chat = open_chat_from_history(cid)  # or open_saved_chat(cid)

    # Update session state
    st.session_state.chat_history = loaded_chat
    st.session_state.opened_chat_cid = cid
    st.session_state.current_chat_title = generate_chat_title(loaded_chat)
    st.session_state.chat_loaded = True
    st.session_state.chat_input = ""
    st.rerun()

def handle_previous_chat():
    """Navigate to the previous chat from history."""
    history_data = load_chat_history()
    all_cids = list(history_data.keys())

    if not all_cids:
        st.warning("No chats in history.")
        return

    # Initialize or update index
    if st.session_state.get("chat_index") is None:
        st.session_state.chat_index = len(all_cids) - 1
    else:
        st.session_state.chat_index = (st.session_state.chat_index - 1) % len(all_cids)

    cid = all_cids[st.session_state.chat_index]
    loaded_chat = open_chat_from_history(cid)

    # Update session state
    st.session_state.chat_history = loaded_chat
    st.session_state.opened_chat_cid = cid
    st.session_state.current_chat_title = generate_chat_title(loaded_chat)
    st.session_state.chat_loaded = True
    st.session_state.chat_input = ""
    st.rerun()

def refresh_app():
    """Reset key session states and refresh the app UI."""
    keys_to_reset = [
        "chat_index", "chat_history", "chat_input", "opened_chat_cid",
        "current_chat_title", "chat_loaded"
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)

    st.rerun()

def clean_saved_chat_directory():
    """Remove all chat files from the saved chats directory."""
    removed_count = 0
    for filename in os.listdir(SAVED_CHAT_DIR):
        if filename.endswith(".json"):
            try:
                file_path = os.path.join(SAVED_CHAT_DIR, filename)
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                st.warning(f"Error deleting {filename}: {e}")

    if removed_count > 0:
        st.success(f"Cleaned {removed_count} saved chats.")
    else:
        st.info("No saved chat files to remove.")

def display_chat_history_sidebar():
    """Display all chat history entries in the sidebar with open and delete options."""
    st.sidebar.subheader("🕓 Chat History")
    history_data = load_chat_history()

    if not history_data:
        st.sidebar.info("No chat history found.")
        return

    for cid, chat in sorted(history_data.items(), key=lambda x: x[1].get("timestamp", ""), reverse=True):
        title = chat.get("title", "Untitled")
        with st.sidebar.expander(f"🗂️ {title}", expanded=False):
            if st.button(f"📂 Open", key=f"open_{cid}"):
                st.session_state.chat_history = open_chat_from_history(cid)
                st.session_state.opened_chat_cid = cid
                st.session_state.current_chat_title = chat.get("title", "Untitled")
                st.session_state.chat_loaded = True
                st.rerun()

            if st.button(f"🗑️ Remove", key=f"delete_history_{cid}"):
                remove_from_history(cid)
                st.rerun()

def display_saved_chats_sidebar():
    """Display all saved chats in the sidebar with open, download, and delete options."""
    st.sidebar.subheader("💾 Saved Chats")
    saved_chats = load_saved_chats()

    if not saved_chats:
        st.sidebar.info("No saved chats found.")
        return

    for cid, chat in sorted(saved_chats.items(), key=lambda x: x[1].get("timestamp", ""), reverse=True):
        title = chat.get("title", "Untitled")
        with st.sidebar.expander(f"💬 {title}", expanded=False):
            if st.button(f"📂 Open", key=f"open_saved_{cid}"):
                st.session_state.chat_history = open_saved_chat(cid)
                st.session_state.opened_chat_cid = cid
                st.session_state.current_chat_title = chat.get("title", "Untitled")
                st.session_state.chat_loaded = True
                st.rerun()

            if st.download_button("⬇️ Download", data=json.dumps(chat, indent=2), file_name=f"{cid}.json", mime="application/json", key=f"download_{cid}"):
                st.toast("Downloaded chat successfully!")

            if st.button(f"🗑️ Delete", key=f"delete_saved_{cid}"):
                remove_saved_chat(cid)
                st.rerun()

def render_sidebar_buttons():
    """Render all sidebar action buttons for chat navigation and control."""
    st.sidebar.markdown("### ⚙️ Chat Controls")

    # New Chat
    if st.sidebar.button("🆕 New Chat", use_container_width=True):
        handle_new_chat()

    # Save Chat
    if st.sidebar.button("💾 Save Chat", use_container_width=True):
        try:
            if st.session_state.get("chat_history"):
                save_chat(st.session_state.chat_history)
                st.toast("✅ Chat saved successfully!")
            else:
                st.warning("No chat history to save.")
        except Exception as e:
            st.error("Failed to save chat.")
            st.exception(e)

    # Next Chat
    if st.sidebar.button("➡️ Next Chat", use_container_width=True):
        handle_next_chat()

    # Previous Chat
    if st.sidebar.button("⬅️ Previous Chat", use_container_width=True):
        handle_previous_chat()

    st.sidebar.markdown("---")

    # Clear Chat History
    if st.sidebar.button("🧹 Clear Chat History", use_container_width=True):
        try:
            clear_chat_history()
            st.toast("🗑️ Chat history cleared.")
            refresh_app()
        except Exception as e:
            st.error("Failed to clear chat history.")
            st.exception(e)

    # Clear Saved Chats
    if st.sidebar.button("🧽 Clear Saved Chats", use_container_width=True):
        try:
            clear_saved_chats()
            st.toast("🗑️ Saved chats cleared.")
            refresh_app()
        except Exception as e:
            st.error("Failed to clear saved chats.")
            st.exception(e)

    # Clean Directory
    if st.sidebar.button("🚫 Clean Saved Chat Folder", use_container_width=True):
        try:
            clean_saved_chat_directory()
            st.toast("🧹 Cleaned empty saved chat files.")
            refresh_app()
        except Exception as e:
            st.error("Failed to clean saved chat directory.")
            st.exception(e)

    st.sidebar.markdown("---")

    # Refresh App
    if st.sidebar.button("🔄 Refresh", use_container_width=True):
        refresh_app()

def load_lottie_animation(filename: str):
    try:
        # Get the absolute path of the current file (main.py or this module)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Build absolute path to assets/lottie
        asset_path = os.path.join(base_dir, "assets", "lottie", filename)

        if not os.path.exists(asset_path):
            st.warning(f"⚠️ Lottie file not found: {asset_path}")
            return None

        with open(asset_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as e:
        st.warning(f"Error loading Lottie animation: {e}")
        return None
        
def render_main_chat_ui(chat_model=None):
    """Main UI layout with Nexa branding, chat logic, and modern styling."""
    try:
        st.set_page_config(page_title="Nexa AI", layout="wide", initial_sidebar_state="expanded")

        # Branding Header
        st.markdown("""
            <div style='text-align:center; margin-top: -30px; margin-bottom: -10px;'>
                <h1 style='color:#4B8BBE; font-size: 2.5rem; margin-bottom: 5px;'>🤖 Nexa AI</h1>
                <p style='color:#6c757d; font-size: 1.1rem;'>Ask questions, get instant answers — powered by DeepSeek AI</p>
            </div>
        """, unsafe_allow_html=True)

        # Load Lottie animation
        animation = load_lottie_animation(LOTTIE_PATH)
        if animation:
            st_lottie(animation, speed=1, loop=True, height=180, key="welcome")
        else:
            st.info("⚠️ Welcome animation not available.")

        st.markdown("<hr style='border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown("### 💬 Start Chatting")

        # Display chat history
        chat_history = st.session_state.get("chat_history", [])
        for msg in chat_history:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            elif isinstance(msg, HumanMessage):
                role, content = "user", msg.content
            elif isinstance(msg, AIMessage):
                role, content = "assistant", msg.content
            else:
                continue  # Unknown format

            # Clean tags
            content = content.replace("<think>", "").replace("</think>", "").strip()

            with st.chat_message("user" if role == "user" else "ai"):
                name = "🧑 You" if role == "user" else "🤖 Nexa"
                st.markdown(f"**{name}:** {content}")

        # Input prompt
        prompt = st.chat_input("Ask something...")

        if prompt:
            clean_prompt = prompt.strip()

            # Append user message
            st.session_state.chat_history.append(HumanMessage(content=clean_prompt))

            with st.chat_message("user"):
                st.markdown(f"**🧑 You:** {clean_prompt}")

            # Nexa AI response
            with st.chat_message("ai"):
                with st.spinner("🤖 Nexa is thinking..."):
                    try:
                        response_text = None
                        for key in CUSTOM_RESPONSES:
                            if key.lower() in clean_prompt.lower():
                                response_text = CUSTOM_RESPONSES[key].replace("<think>", "").replace("</think>", "").strip()
                                break

                        if not response_text and chat_model:
                            ai_message = chat_model.invoke(st.session_state.chat_history)
                            response_text = ai_message.content.replace("<think>", "").replace("</think>", "").strip()
                            st.session_state.chat_history.append(AIMessage(content=response_text))
                        elif not response_text:
                            response_text = "🤖 Nexa response placeholder (no model linked)."
                            st.session_state.chat_history.append(AIMessage(content=response_text))
                        else:
                            st.session_state.chat_history.append(AIMessage(content=response_text))

                        st.markdown(f"**🤖 Nexa:** {response_text}")

                        # Save cleaned version
                        save_to_history([
                            {
                                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                                "content": m.content.replace("<think>", "").replace("</think>", "").strip()
                            }
                            for m in st.session_state.chat_history
                        ])

                    except Exception as e:
                        error_msg = f"⚠️ Error while generating response: {e}"
                        st.markdown(f"**🤖 Nexa:** {error_msg}")
                        st.session_state.chat_history.append(AIMessage(content=error_msg))
                        st.toast("❌ Failed to get response", icon="⚠️")
                        st.exception(e)

    except Exception as e:
        st.error("🚨 Unexpected error occurred while rendering the main UI.")
        st.exception(e)

def render_bot(chat_model):
    """Main entry point to render Nexa AI chatbot with full UI, history, and controls."""
    try:
        # Set layout configuration (done here to ensure standalone usability)
        st.set_page_config(page_title="Nexa AI", layout="wide", initial_sidebar_state="expanded")

        # Initialize session states if not set
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "active_chat_index" not in st.session_state:
            st.session_state.active_chat_index = None

        if "page_loaded" not in st.session_state:
            st.session_state.page_loaded = True
            st.toast("👋 Welcome to Nexa AI!", icon="🤖")

        if "saved_chats" not in st.session_state:
            st.session_state.saved_chats = []

        if "history_cache" not in st.session_state:
            st.session_state.history_cache = []

        # Load all history and saved chats on first load
        if st.session_state.page_loaded:
            st.session_state.history_cache = load_chat_history()
            st.session_state.saved_chats = load_saved_chats()

        # 🔧 UI Components
        render_sidebar_buttons()
        display_chat_history_sidebar()
        display_saved_chats_sidebar()
        render_main_chat_ui(chat_model)

    except Exception as e:
        st.error("🚨 Critical error occurred while rendering Nexa AI.")
        st.exception(e)
