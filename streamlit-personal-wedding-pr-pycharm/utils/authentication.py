import streamlit as st


def authenticate_user(username, password):
    """Authenticates user against credentials stored in secrets."""

    # Verifică dacă 'auth' este în secrete
    if "auth" not in st.secrets:
        st.error("Secrets not configured properly.")
        return False

    st.write("Secrets available:", st.secrets)  # Adaugă această linie pentru debugging

    users = st.secrets["auth"]["users"]
    passwords = st.secrets["auth"]["passwords"]

    if username in users:
        idx = users.index(username)
        if passwords[idx] == password:
            return True
    return False
