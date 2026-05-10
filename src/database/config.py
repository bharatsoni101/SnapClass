import streamlit as st


def get_supabase():
    """Return a Supabase client if SUPABASE_URL and SUPABASE_KEY are set in
    Streamlit secrets. If credentials are missing, return None.

    This lazily imports the supabase client to avoid raising ImportError at
    module import time if the package isn't installed and to avoid trying to
    create the client when secrets aren't provided (useful for tests or
    non-Streamlit contexts).
    """
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        # Credentials not provided; caller can handle None.
        return None

    # Import here to avoid ImportError when the package isn't required.
    from supabase import create_client

    return create_client(url, key)


# Module-level client for convenience; will be None if creds are missing.
supabase = get_supabase()
