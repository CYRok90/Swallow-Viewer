import gspread
import pandas as pd
import streamlit as st

def initSpreadSheet():
    # gc = gspread.service_account(filename='google_oauth.json')
    credentials = {
        "type": "service_account",
        "project_id": "rakkufund",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "universe_domain": "googleapis.com",
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    gc = gspread.service_account_from_dict(credentials)
    return gc.open("swallow_dividends")

def getStockEtfSet(sh, market_select):
    ws = sh.worksheet("stock_etf_list")
    stock_etf_df = pd.DataFrame(ws.get_all_records())
    print(stock_etf_df)
    return stock_etf_df