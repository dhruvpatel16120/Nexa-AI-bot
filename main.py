import streamlit as st
from assets.auth import load_user_data, render_login, render_signup
from assets.sidebar import render_sidebar
from assets.bot import render_bot
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
key = os.getenv("API_KEY")

# Load Chat model
chat_model = ChatGroq(api_key=key, model_name="deepseek-r1-distill-llama-70b")

# Set Streamlit page configuration
st.set_page_config(page_title="Nexa AI", page_icon="🤖", layout="wide")

# Initialize session state variables
if "page_option" not in st.session_state:
    st.session_state.page_option = "Login"
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# Load users
user_data = load_user_data()

# Render sidebar and update navigation state
sidebar_option = render_sidebar()
if sidebar_option and sidebar_option != st.session_state.page_option:
    st.session_state.page_option = sidebar_option

# If logged in, always route to chat
if st.session_state.logged_in_user:
    st.session_state.page_option = "Chat with Bot"

# Routing Logic
match st.session_state.page_option:
    case "Sign Up":
        render_signup(user_data)

    case "Login":
        render_login(user_data)

    case "Chat with Bot":
        if not st.session_state.logged_in_user:
            st.warning("⚠️ Please log in first.")
            st.session_state.page_option = "Login"
            st.experimental_rerun()
        else:
            render_bot(chat_model)

    case _:
        st.warning("🔁 Resetting invalid state...")
        st.session_state.page_option = "Login"
        st.experimental_rerun()
