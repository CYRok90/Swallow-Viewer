import streamlit as st
import pandas as pd

from modules.spreadsheets import get_auth_table

def display_auth(sh):
    auth_df = pd.DataFrame(get_auth_table(sh))
    api_key = st.text_input("인증키", type="password")
    if api_key:
        ok = auth_df["auth_key"].isin([api_key]).any()
        if ok:
            st.session_state["user"] = auth_df[auth_df["auth_key"] == api_key]["name"].values[0]
            st.session_state["api_key"] = api_key
            st.session_state["logged_in"] = True
            st.session_state["logger"].info("USER: %s has logged in.", st.session_state.user)
            st.rerun()
        else:
            st.error("존재하지 않는 인증키입니다.")