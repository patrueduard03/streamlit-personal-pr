import streamlit as st


def authenticate_user(username, password):
    """Authenticates user against hardcoded credentials for testing."""
    test_users = ["admin", "familia"]
    test_passwords = ["admin", "familia"]

    if username in test_users:
        idx = test_users.index(username)
        if test_passwords[idx] == password:
            return True
    return False

