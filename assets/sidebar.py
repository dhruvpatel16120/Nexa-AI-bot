import streamlit as st
import pandas as pd

def load_user_data():
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["email", "username", "password"])

def logout_user():
    keys_to_clear = ["logged_in_user", "page_option", "chat_history", "input_question", "chat_input"]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    st.success("✅ You have been logged out.")
    st.rerun()

def add_sidebar_footer():
    st.markdown(
        """
        <style>
        .sidebar-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 12px 15px;
            background-color: #0e1117;
            color: #ccc;
            font-size: 0.78rem;
            text-align: center;
            border-top: 1px solid #333;
            z-index: 999;
        }
        .sidebar-footer a {
            color: #66c2ff;
            text-decoration: none;
        }
        .sidebar-footer a:hover {
            text-decoration: underline;
        }
        </style>

        <div class="sidebar-footer">
            <span>Made with ❤️ by <a href="https://github.com/dhruvpatel16120" target="_blank">Dhruv Patel</a></span>
            <span>© 2025 Nexa AI Bot. All rights reserved.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color:#6C63FF;font-size: 35px;">🤖 Nexa AI Bot</h2>
            <p style="font-size: 18px; color: gray;">Your personal AI assistant</p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    if st.session_state.get('logged_in_user'):
        username = st.session_state['logged_in_username']
        email = st.session_state['logged_in_user_email']
        st.sidebar.markdown("#### 👤 Profile")
        st.sidebar.markdown(f"**Username:** `{username}`")
        st.sidebar.markdown(f"**Email:** `{email}`")

        st.sidebar.markdown("---")

        with st.sidebar.container():
            if st.sidebar.button("🚪 Logout", key="logout-btn"):
                logout_user()

        add_sidebar_footer()
        return "Chat with Bot"

    else:
        add_sidebar_footer()
        return st.sidebar.selectbox("Choose an option:", ["Sign Up", "Login"])
   