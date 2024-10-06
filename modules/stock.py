import streamlit as st
import pandas as pd

from modules.spreadsheets import get_stock_etf_list_table, get_etf_info_table, get_raw_table
from modules.simulate import display_simulate
from modules.display import display_etf_information, display_stock_recent_price, display_stock_recent_dividend, display_chart_table

def get_etf_list_with_market_select(sh, market_select):
    stock_etf_df = pd.DataFrame(get_stock_etf_list_table(sh))
    return stock_etf_df[(stock_etf_df["market"] == market_select) & (stock_etf_df["type"] == "etf")]

def get_etf_info_with_name(sh, etf_name):
    etf_info_df = pd.DataFrame(get_etf_info_table(sh))
    return etf_info_df[(etf_info_df["name"] == etf_name)].iloc[0].tolist()

def get_etf_raw_with_name(sh, etf_name):
    etf_raw_df = pd.DataFrame(get_raw_table(sh))
    return etf_raw_df[(etf_raw_df["name"] == etf_name)]

def get_dividend_data(etf_raw_df):
    dividend_df = etf_raw_df[["recorddate", "paydate", "dividend"]]
    return dividend_df.drop_duplicates(subset=["recorddate", "paydate"])

def display_stock_tab(sh):
    if "market" not in st.session_state:
        st.session_state["market"] = ""
    if "etf_name" not in st.session_state:
        st.session_state["etf_name"] = ""

    market_col, etf_col = st.columns([1,1])
    with market_col:
        market_select = st.radio("주식 시장", [":us:미국", ":kr:한국"], key="market_radio")
        selected_market = market_select[-2:]
        if selected_market != st.session_state.market:
            st.session_state["market"] = selected_market
            st.session_state["etf_list"] = get_etf_list_with_market_select(sh, st.session_state.market)
    with etf_col:
        selected_etf = st.selectbox("종목", st.session_state["etf_list"])
    st.divider()

    info_tab, simulation_tab = st.tabs(["정보", "시뮬레이션"])
    with info_tab:
        if selected_etf != st.session_state.etf_name:
            st.session_state["etf_name"] = selected_etf
            st.session_state["etf_info"] = get_etf_info_with_name(sh, st.session_state.etf_name)
            st.session_state["dividend_interval"] = st.session_state.etf_info[5]
            st.session_state["etf_raw_df"] = get_etf_raw_with_name(sh, st.session_state.etf_name)
            st.session_state["etf_dividend_df"] = get_dividend_data(st.session_state.etf_raw_df)
        display_etf_information(st.session_state.etf_info)
        display_stock_recent_price(st.session_state.etf_raw_df[:2], st.session_state.market)
        display_stock_recent_dividend(st.session_state.etf_dividend_df[:7], st.session_state.market)
        display_chart_table(st.session_state.etf_raw_df, st.session_state.etf_dividend_df)
    
    with simulation_tab:
        display_simulate(st.session_state.etf_name, st.session_state.etf_raw_df, st.session_state.dividend_interval)
