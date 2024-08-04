import streamlit as st
import pandas as pd

def auth(sh):
    ws = sh.worksheet("auth")
    auth_df = pd.DataFrame(ws.get_all_records())

    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    st.session_state.api_key = st.text_input("인증키", type="password")
    ok = auth_df["auth_key"].isin([st.session_state.api_key]).any()
    if "user" not in st.session_state:
        st.session_state.user = ""    
    if ok:
        st.session_state.user = auth_df[auth_df["auth_key"] == st.session_state.api_key]["name"].values[0]
        return True
    else:
        return False