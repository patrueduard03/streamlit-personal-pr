import streamlit as st


def authenticate_user(username, password):
    """Authenticates user against credentials stored in secrets."""
    # Check if the secrets are set correctly
    if "auth" not in st.secrets:
        st.error("Secrets not configured properly.")
        return False

    users = st.secrets["auth"]["users"]
    passwords = st.secrets["auth"]["passwords"]

    if username in users:
        idx = users.index(username)
        if passwords[idx] == password:
            return True
    return False