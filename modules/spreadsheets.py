import gspread
import pandas as pd
from millify import millify
import streamlit as st

def init_spreadsheet():
    # gc = gspread.service_account(filename="google_oauth.json")
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

def get_etf_with_market_select(sh, market_select):
    ws = sh.worksheet("stock_etf_list")
    stock_etf_df = pd.DataFrame(ws.get_all_records())
    return stock_etf_df[(stock_etf_df["market"] == market_select) & (stock_etf_df["type"] == "etf")]

def get_etf_info(sh, name):
    ws = sh.worksheet("etf_info_list")
    etf_info_df = pd.DataFrame(ws.get_all_records())
    return etf_info_df[(etf_info_df["name"] == name)].iloc[0].tolist()

def get_stock_raw_data(sh, name):
    ws = sh.worksheet("raw")
    stock_raw_df = pd.DataFrame(ws.get_all_records())
    return stock_raw_df[(stock_raw_df["name"] == name)]

def get_dividend_data(stock_raw_df):
    dividend_df = stock_raw_df[["recorddate", "paydate", "dividend"]]
    return dividend_df.drop_duplicates(subset=["recorddate", "paydate"])

def get_close_table(stock_raw_df):
    current_close = stock_raw_df.iloc[0]["close"]
    first_close_row = stock_raw_df.tail(1)
    first_close = first_close_row["close"].values[0]
    min_close = stock_raw_df["close"].min()
    min_close_rows = stock_raw_df[stock_raw_df["close"] == min_close]
    min_close_row = min_close_rows[:1]
    max_close = stock_raw_df["close"].max()
    max_close_rows = stock_raw_df[stock_raw_df["close"] == max_close]
    max_close_row = max_close_rows[:1]
    avg_close = stock_raw_df["close"].mean()
    
    table_data = {
        "": ["첫 종가", "최저 종가", "최고 종가", "평균 종가"],
        "종가": [
            first_close,
            min_close_row["close"].values[0],
            max_close_row["close"].values[0],
            avg_close,
        ],
        "최근 종가와 비교 - {}".format(current_close): [
            f"{(current_close / first_close) * 100:.3f}%",
            f"{(current_close / min_close) * 100:.3f}%",
            f"{(current_close/ max_close) * 100:.3f}%",
            f"{(current_close/ avg_close) * 100:.3f}%"
        ],
        "날짜": [
            first_close_row["date"].values[0],
            min_close_row["date"].values[0],
            max_close_row["date"].values[0],
            ""
        ]
    }
    return table_data

def get_volume_table(stock_raw_df):
    current_volume = stock_raw_df.iloc[0]["volume"]
    first_volume_row = stock_raw_df.tail(1)
    first_volume = first_volume_row["volume"].values[0]
    min_volume = stock_raw_df["volume"].min()
    min_volume_rows = stock_raw_df[stock_raw_df["volume"] == min_volume]
    min_volume_row = min_volume_rows[:1]
    max_volume = stock_raw_df["volume"].max()
    max_volume_rows = stock_raw_df[stock_raw_df["volume"] == max_volume]
    max_volume_row = max_volume_rows[:1]
    avg_volume = stock_raw_df["volume"].mean()
    
    table_data = {
        "": ["첫 거래량", "최저 거래량", "최고 거래량", "평균 거래량"],
        "거래량": [
            millify(first_volume, 3),
            millify(min_volume_row["volume"].values[0], 3),
            millify(max_volume_row["volume"].values[0], 3),
            millify(avg_volume, 3),
        ],
        "최근 거래량과 비교 - {}".format(millify(current_volume, 3)): [
            f"{(current_volume / first_volume) * 100:.3f}%",
            f"{(current_volume / min_volume) * 100:.3f}%",
            f"{(current_volume/ max_volume) * 100:.3f}%",
            f"{(current_volume/ avg_volume) * 100:.3f}%"
        ],
        "날짜": [
            first_volume_row["date"].values[0],
            min_volume_row["date"].values[0],
            max_volume_row["date"].values[0],
            ""
        ]
    }
    return table_data

def get_dividend_rate_table(stock_raw_df):
    current_dividend_rate = stock_raw_df.iloc[0]["dividend_per_close_percent"]
    first_dividend_rate_row = stock_raw_df.tail(1)
    first_dividend_rate = first_dividend_rate_row["dividend_per_close_percent"].values[0]
    min_dividend_rate = stock_raw_df["dividend_per_close_percent"].min()
    min_dividend_rate_rows = stock_raw_df[stock_raw_df["dividend_per_close_percent"] == min_dividend_rate]
    min_dividend_rate_row = min_dividend_rate_rows[:1]
    max_dividend_rate = stock_raw_df["dividend_per_close_percent"].max()
    max_dividend_rate_rows = stock_raw_df[stock_raw_df["dividend_per_close_percent"] == max_dividend_rate]
    max_dividend_rate_row = max_dividend_rate_rows[:1]
    avg_dividend_rate = stock_raw_df["dividend_per_close_percent"].mean()
    
    table_data = {
        "": ["첫 배당률", "최저 배당률", "최고 배당률", "평균 배당률"],
        "배당률": [
            f"{first_dividend_rate:.3f}%",
            f"{min_dividend_rate:.3f}%",
            f"{max_dividend_rate:.3f}%",
            f"{avg_dividend_rate:.3f}%",
        ],
        "최근 배당률과 비교 - {:.3f}%".format(current_dividend_rate): [
            f"{(current_dividend_rate / first_dividend_rate) * 100:.3f}%",
            f"{(current_dividend_rate / min_dividend_rate) * 100:.3f}%",
            f"{(current_dividend_rate/ max_dividend_rate) * 100:.3f}%",
            f"{(current_dividend_rate/ avg_dividend_rate) * 100:.3f}%"
        ],
        "배당기준일": [
            first_dividend_rate_row["recorddate"].values[0],
            min_dividend_rate_row["recorddate"].values[0],
            max_dividend_rate_row["recorddate"].values[0],
            ""
        ],
        "배당지급일": [
            first_dividend_rate_row["paydate"].values[0],
            min_dividend_rate_row["paydate"].values[0],
            max_dividend_rate_row["paydate"].values[0],
            ""
        ]
    }
    return table_data

def get_dividend_table(dividend_df):
    current_dividend = dividend_df.iloc[0]["dividend"]
    first_dividend_row = dividend_df.tail(1)
    first_dividend = first_dividend_row["dividend"].values[0]
    min_dividend = dividend_df["dividend"].min()
    min_dividend_rows = dividend_df[dividend_df["dividend"] == min_dividend]
    min_dividend_row = min_dividend_rows[:1]
    max_dividend = dividend_df["dividend"].max()
    max_dividend_rows = dividend_df[dividend_df["dividend"] == max_dividend]
    max_dividend_row = max_dividend_rows[:1]
    avg_dividend = dividend_df["dividend"].mean()

    table_data = {
        "": ["첫 배당금", "최저 배당금", "최고 배당금", "평균 배당금"],
        "배당금": [
            first_dividend,
            min_dividend_row["dividend"].values[0],
            max_dividend_row["dividend"].values[0],
            avg_dividend
        ],
        "최근 배당금과 비교 - {}".format(current_dividend): [
            f"{(current_dividend / first_dividend) * 100:.3f}%",
            f"{(current_dividend / min_dividend) * 100:.3f}%",
            f"{(current_dividend/ max_dividend) * 100:.3f}%",
            f"{(current_dividend/ avg_dividend) * 100:.3f}%",
        ],
        "배당기준일": [
            first_dividend_row["recorddate"].values[0],
            min_dividend_row["recorddate"].values[0],
            max_dividend_row["recorddate"].values[0],
            ""
        ],
        "배당지급일": [
            first_dividend_row["paydate"].values[0],
            min_dividend_row["paydate"].values[0],
            max_dividend_row["paydate"].values[0],
            ""
        ]
    }
    return table_data