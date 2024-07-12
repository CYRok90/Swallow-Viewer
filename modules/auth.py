import streamlit as st
import pandas as pd

def auth(sh):
    ws = sh.worksheet("auth")
    auth_df = pd.DataFrame(ws.get_all_records())
    
    inputUserApiKey = st.text_input("인증키")
    ok = auth_df['auth_key'].isin([inputUserApiKey]).any()
    if ok:
        return (True, auth_df[auth_df['auth_key'] == inputUserApiKey]['name'].values[0])
    else:
        return (False, "")