import streamlit as st 
import json
import os
import pandas as pd
import assets.sidebar

# ---------------------- CONFIG ----------------------
USER_DATA_FILE = 'user/users.csv'

# Ensure the folder exists
os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)

# ---------------------- USER DATA ----------------------
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        return pd.read_csv(USER_DATA_FILE)
    else:
        return pd.DataFrame(columns=["email", "password", "username"])

# ---------------------- LOTTIE ----------------------
def load_lottiefile(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

# ---------------------- COMMON STYLES ----------------------
def render_background_style():
    st.markdown("""
        <style>
        body, .main, .block-container {
            width: 100%;
            height: 100%;
            margin: 0;
            background: linear-gradient(-45deg, #ffecd2, #fcb69f, #a1c4fd, #c2e9fb);
            background-size: 400% 400%;
            animation: gradientAnimation 12s ease infinite;
            color: #333333;
            font-family: 'Segoe UI', sans-serif;
        }

        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        h2 { font-weight: 700; font-size: 2rem; margin-bottom: 1rem; color: #ffffff; }

        .stButton>button {
            background: linear-gradient(90deg, #4A90E2, #9013FE);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            color: #fff;
            box-shadow: 0 0 10px rgba(74,144,226,0.6);
        }

        .stTextInput>div>div>input {
            background: rgba(255,255,255,0.8);
            border: 2px solid #4A90E2;
            border-radius: 6px;
            padding: 0.4rem;
            font-size: 1rem;
            color: #333;
            transition: border-color 0.3s ease;
        }

        .footer {
            position: relative;
            bottom: 0;
            margin-top: 2rem;
            font-size: 20px;
            color: #fff;
        }

        a { color: #4A90E2; text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

# ---------------------- SIGN UP ----------------------
def render_signup(user_data):
    user_data = load_user_data()
    render_background_style()
    st.markdown("<h1 style='text-align:center;color:white;font-size:2.5rem;'>🤖 Welcome to Nexa AI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:white;'>🔐 Create Your Nexa Account</h2>", unsafe_allow_html=True)
    st.markdown("<div class='description' style='text-align:center;font-size:1.2rem;'>⚠️ Please fill in the details below to create your account.</div>", unsafe_allow_html=True)

    username = st.text_input("Username", key="signup_username", label_visibility="collapsed")
    email = st.text_input("Email", key="signup_email", label_visibility="collapsed")
    password = st.text_input("Password", type="password", key="signup_password", label_visibility="collapsed")

    if st.button("Sign Up"):
        if not username.strip() or not email.strip() or not password.strip():
            st.error("🚫 All fields are required!")
        elif username in user_data["username"].values:
            st.error("🚫 Username already taken. Please choose another.")
        else:
            # Append new user
            new_user = pd.DataFrame({
                "username": [username],
                "email": [email],
                "password": [password]  # Use hashing for production!
            })
            user_data = pd.concat([user_data, new_user], ignore_index=True)

            # Ensure folder exists and save
            os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
            user_data.to_csv(USER_DATA_FILE, index=False)

            st.success("✅ Account created! You can now log in.")
            st.session_state.page_option = "Login"
            st.experimental_rerun()

    st.markdown("<div class='footer'>© 2025 Nexa AI</div>", unsafe_allow_html=True)

# ---------------------- LOGIN ----------------------
def render_login(user_data):
    user_data = load_user_data()
    render_background_style()
    st.markdown("<h1 style='text-align:center;color:white;font-size:2.5rem;'>🤖 Welcome to Nexa AI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:white;'>🔑 Login to Nexa</h2>", unsafe_allow_html=True)
    st.markdown("<div class='description' style='font-size:1.2rem;text-align:center;'>⚠️ Please enter your username/email and password to continue.</div>", unsafe_allow_html=True)

    login_input = st.text_input("Username or Email", key="login_user_input", label_visibility="collapsed")
    password = st.text_input("Password", type="password", key="login_password", label_visibility="collapsed")

    if st.button("Log In"):
        if not login_input.strip() or not password.strip():
            st.error("All fields are required!")
        else:
            user_row = user_data[(user_data['email'] == login_input) | (user_data['username'] == login_input)]
            if user_row.empty:
                st.error("Username or Email not found. Please sign up first.")
            elif user_row['password'].values[0] != password:
                st.error("Incorrect password.")
            else:
                st.session_state.logged_in_user = user_row['email'].values[0]
                st.session_state.logged_in_user_email = user_row['email'].values[0]
                st.session_state.logged_in_username = user_row['username'].values[0]
                st.success(f"✅ Welcome To Nexa AI!")
                st.session_state.page_option = "Chat with Bot"
                st.experimental_rerun()

    if st.session_state.get("logged_in_user") not in [None, "", "null"]:
        st.success(f"Welcome back, {st.session_state.logged_in_user}!")

    st.markdown("<div class='footer'>© 2025 Nexa AI </div>", unsafe_allow_html=True)
