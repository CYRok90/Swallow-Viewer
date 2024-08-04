import streamlit as st
import logging

from modules.spreadsheets import init_spreadsheet, get_etf_with_market_select, get_etf_info, get_stock_raw_data, get_dividend_data
from modules.auth import auth
from modules.display import display_report_header, display_etf_information, display_stock_recent_price, display_stock_recent_dividend, display_chart_table
from modules.simulate import display_simulate_header, display_simulate

REPORT_VERSION = "v1.0.0"
SIMULATE_VERSION = "v1.0.0"

def main():
    st.set_page_config(layout="wide")
    
    sh = init_spreadsheet()
    ok = auth(sh) # api_key, user
    if not ok:
        st.text("존재하지 않는 인증키입니다.")
    logger.info("USER: %s has logged in.", st.session_state.user)

    st.title("초이하우스 - 락구펀드")
    if ok:
        display_report_header(REPORT_VERSION)
        
        market_col, etf_col = st.columns([1,1])
        with market_col:
            if "market" not in st.session_state:
                st.session_state.market = "미국"
                if "prev_market" not in st.session_state:
                    st.session_state.prev_market = ""
            market_select = st.radio("주식 시장", [":us:미국", ":kr:한국"])
            st.session_state.market = market_select[-2:]

        # GET ETF LIST when market changed
        if st.session_state.market != st.session_state.prev_market:
            if "etf_list" not in st.session_state:
                st.session_state["etf_list"] = list()
            st.session_state["etf_list"] = get_etf_with_market_select(sh, st.session_state.market)
            st.session_state.prev_market = st.session_state.market
            logger.info("USER: %s called ETF LIST API(market:%s).", st.session_state.user, st.session_state.market)
        # DISPLAY ETF LIST with selectbox for etf_name
        with etf_col:
            if "etf_name" not in st.session_state:
                st.session_state.etf_name = "BDJ"
                if "prev_etf_name" not in st.session_state:
                    st.session_state.prev_etf_name = ""
            st.session_state.etf_name = st.selectbox("종목", st.session_state["etf_list"])
        st.divider()

        # GET ETF INFORMATION when etf_name changed
        if st.session_state.etf_name != st.session_state.prev_etf_name:
            if "etf_info" not in st.session_state:
                st.session_state["etf_info"] = list()
            if "dividend_interval" not in st.session_state:
                st.session_state["dividend_interval"] = ""
            st.session_state["etf_info"] = get_etf_info(sh, st.session_state.etf_name)
            logger.info("USER: %s called ETF INFO API(etf:%s).", st.session_state.user, st.session_state.etf_name)
            st.session_state["dividend_interval"] = st.session_state["etf_info"][5]
        # DISPLAY ETF INFO
        display_etf_information(st.session_state["etf_info"])

        # GET ETF RAW DATA when etf_name changed
        if st.session_state.etf_name != st.session_state.prev_etf_name:
            if "etf_raw_df" not in st.session_state:
                st.session_state["etf_raw_df"] = list()
            if "etf_dividend_df" not in st.session_state:
                st.session_state["etf_dividend_df"] = list()
            st.session_state["etf_raw_df"] = get_stock_raw_data(sh, st.session_state.etf_name)
            st.session_state["etf_dividend_df"] = get_dividend_data(st.session_state["etf_raw_df"])
            logger.info("USER: %s called ETF RAW DF API(etf:%s).", st.session_state.user, st.session_state.etf_name)
            st.session_state.prev_etf_name = st.session_state.etf_name
        # DISPLAY ETF RECENT PRICE & DIVIDEND
        display_stock_recent_price(st.session_state["etf_raw_df"][:2], st.session_state.market)
        display_stock_recent_dividend(st.session_state["etf_dividend_df"][:4], st.session_state.market)

        display_chart_table(st.session_state["etf_raw_df"], st.session_state["etf_dividend_df"])

        display_simulate_header(SIMULATE_VERSION)

        display_simulate(st.session_state.etf_name, st.session_state["etf_raw_df"], st.session_state["dividend_interval"])

        # TODO: st.progress or st.status

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(asctime)s | %(message)s')
    logger = logging.getLogger(__name__)
    main()