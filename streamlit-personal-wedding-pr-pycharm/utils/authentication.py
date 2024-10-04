import streamlit as st


def authenticate_user(username, password):
    """Authenticates user against credentials stored in secrets."""
    users = st.secrets["auth"]["users"]
    passwords = st.secrets["auth"]["passwords"]

    if username in users:
        idx = users.index(username)
        if passwords[idx] == password:
            return True
    return False
