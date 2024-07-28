import streamlit as st

from modules.spreadsheets import init_spreadsheet, get_etf_with_market_select, get_stock_raw_data, get_dividend_data
from modules.auth import auth
from modules.display import display_report_header, display_etf_information, display_stock_recent_price, display_stock_recent_dividend, display_chart_table
from modules.simulate import display_simulate_header, display_simulate

REPORT_VERSION = "v1.0.0"
SIMULATE_VERSION = "v1.0.0"

# TODO: https://docs.streamlit.io/develop/concepts/architecture/session-state. 값 변할때마다 통채로 리로드하는것 방지

# TODO: 미국 ETF면 $ 표기
# TODO: 한국 ETF면 ₩ 표기

def main():
    st.set_page_config(layout="wide")
    
    sh = init_spreadsheet()
    (ok, user, api_key) = auth(sh)
    # TODO: 사용자 기록을 남긴다.
    if not ok:
        st.text("존재하지 않는 인증키입니다.")
    st.title("초이하우스 - 락구펀드")
    if ok:
        display_report_header(REPORT_VERSION)
        
        market_col, etf_col = st.columns([1,1])
        with market_col:
            market_select = st.radio("주식 시장", [":us:미국", ":kr:한국"])
        market_select = market_select[-2:]
        etf_list = get_etf_with_market_select(sh, market_select)
        with etf_col:
            etf_name = st.selectbox("종목", etf_list)
        st.divider()

        dividend_interval = display_etf_information(sh, etf_name)

        etf_raw_df = get_stock_raw_data(sh, etf_name)
        display_stock_recent_price(etf_raw_df[:2])

        dividend_df = get_dividend_data(etf_raw_df)
        display_stock_recent_dividend(dividend_df[:4])

        display_chart_table(etf_raw_df, dividend_df)

        display_simulate_header(SIMULATE_VERSION)

        display_simulate(api_key, etf_name, etf_raw_df, dividend_interval)

        # st.progress or st.status

if __name__ == "__main__":
    main()