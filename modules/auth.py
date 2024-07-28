import streamlit as st
import pandas as pd

def auth(sh):
    ws = sh.worksheet("auth")
    auth_df = pd.DataFrame(ws.get_all_records())
    
    api_key = st.text_input("인증키")
    ok = auth_df['auth_key'].isin([api_key]).any()
    if ok:
        return (True, auth_df[auth_df['auth_key'] == api_key]['name'].values[0], api_key)
    else:
        return (False, "", "")