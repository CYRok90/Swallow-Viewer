import streamlit as st
import logging
from datetime import datetime
import locale
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Category20

from modules.portfolio import display_portfolio
from modules.spreadsheets import init_spreadsheet, get_etf_with_market_select, get_etf_info, get_stock_raw_data, get_dividend_data
from modules.auth import auth
from modules.display import display_report_header, display_etf_information, display_stock_recent_price, display_stock_recent_dividend, display_chart_table
from modules.simulate import display_simulate_header, display_simulate

VERSION = "v1.0.0"
REPORT_VERSION = "v1.0.0"
SIMULATE_VERSION = "v1.0.0"

def rsi_color(val):
    """RSI 값을 기준으로 색상을 지정하는 함수"""
    if val >= 75:
        color = '#8B0000'  # 찐한 빨간색 (빨간색 강조)
    elif val >= 65:
        color = '#FF0000'  # 빨간색
    elif val >= 55:
        color = '#FFA07A'  # 연한 빨간색 (빨간색이지만 덜 강조)
    elif val >= 45:
        color = '#808080'  # 중립 (회색)
    elif val >= 35:
        color = '#87CEFA'  # 연한 파란색 (파란색이지만 덜 강조)
    elif val >= 25:
        color = '#0000FF'  # 파란색
    else:
        color = '#000080'  # 찐한 파란색 (파란색 강조)
    return f'color: {color}'

# def sma_color(close, sma):
#     """SMA 값을 종가와 비교하여 글자 색을 지정하는 함수"""
#     ratio = (close / sma - 1) * 100  # 백분율 계산
#     if ratio < -10:
#         return 'color: #800020'  # 버건디
#     elif ratio < -5:
#         return 'color: #FF0000'  # 빨간색
#     elif ratio < 0:
#         return 'color: #FFC0CB'  # 분홍색
#     elif ratio == 0:
#         return 'color: #000000'
#     elif ratio < 5:
#         return 'color: #90EE90'  # 연두색
#     elif ratio < 10:
#         return 'color: #008000'  # 초록색
#     else:
#         return 'color: #004000'  # 찐초록

# def apply_sma_colors(row):
#     """SMA 컬럼에 색상을 적용하는 함수"""
#     return [sma_color(row['종가'], row[col]) for col in ['종가', 'SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)']]

# TODO: fragment
#@st.fragment

# TODO: cache, session 다시 확인해서 적용

# TODO: form 이용해서 시뮬레이션
# https://docs.streamlit.io/develop/api-reference/execution-flow/st.form

def main():
    st.set_page_config(layout="wide")
    # TODO: page_title, page_icon
    #    st.set_page_config(page_title=None, page_icon=None, initial_sidebar_state="auto", menu_items=None)
    # TODO: https://docs.streamlit.io/develop/api-reference/configuration/config.toml

    
    sh = init_spreadsheet()
    ok = False
    # TODO: Hide when logged in.
    # if "api_key" not in st.session_state:
    ok = auth(sh) # api_key, user
    if not ok:
        st.text("존재하지 않는 인증키입니다.")
    st.session_state["logger"].info("USER: %s has logged in.", st.session_state.user)

    
    locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")
    today = datetime.now()
    st.markdown(
            """
            <div style='display: flex; align-items: baseline; height: 100%;'>
                <h1>초이하우스 - 락구펀드</h1>
                <h5>{version}</h5>
                <h4>{date}</h4>
            </div>
            """.format(date=today.strftime("%Y-%m-%d %A"), version= VERSION),
            unsafe_allow_html=True
    )
    if ok:
        with st.spinner("잠시만 기다려주세요..."):
            board_tab, etf_tab, chart_tab, portfolio_tab = st.tabs(["ETF 현황판", "ETF 분석", "지표 & ETF 차트 비교", "ETF 포트폴리오"])
            with board_tab:
                st.subheader("지수 현황판", divider="rainbow", anchor="market_board")
                index_board_df = pd.DataFrame(sh.worksheet("index_board").get_all_records())

                index_chart_df = pd.DataFrame(sh.worksheet("index_board").get_all_records())
                for col in ['sma5', 'sma10', 'sma20', 'sma60', 'sma120', 'sma200']:
                    index_chart_df[col] = (index_chart_df[col] / index_chart_df['close'] - 1) * 100
                x = ['SMA200', 'SMA120', 'SMA60', 'SMA20', 'SMA10', 'SMA5', '종가']
                p = figure(x_range=x, tools="pan,wheel_zoom,box_zoom,reset,hover,save")
                colors = Category20[len(index_chart_df['name'])]

                for idx, row in index_chart_df.iterrows():
                    y = [
                        row['sma200'],
                        row['sma120'],
                        row['sma60'],
                        row['sma20'],
                        row['sma10'],
                        row['sma5'],
                        0
                    ]
                    source = ColumnDataSource(data=dict(x=x, y=y, name=[row['name']] * len(x)))
                    p.line('x', 'y', source=source, line_width=2, legend_label=row['name'], color=colors[idx])
                    p.circle('x', 'y', source=source, size=8, color=colors[idx], legend_label=row['name'])
                hover = p.select(dict(type=HoverTool))
                hover.tooltips = [("지수", "@name"), ("종가 대비(%)", "@y")]
                p.legend.location = "bottom_right"
                p.legend.click_policy = "hide"
                st.bokeh_chart(p, use_container_width=True)

                index_board_df.rename(columns={
                    "date": "날짜",
                    "name": "지수명",
                    "close": "종가",
                    "rsi14": "RSI(14)",
                    "sma5": "SMA(5)",
                    "sma10": "SMA(10)",
                    "sma20": "SMA(20)",
                    "sma60": "SMA(60)",
                    "sma120": "SMA(120)",
                    "sma200": "SMA(200)"
                }, inplace=True)
                index_board_df['RSI(14)'] = index_board_df['RSI(14)'].round(2)
                index_board_df[['SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)']] = index_board_df[['SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)']].round(2)

                styled_index_df = index_board_df.style.map(rsi_color, subset=['RSI(14)'])
                # styled_df = styled_df.apply(lambda row: apply_sma_colors(row), axis=1, subset=['종가', 'SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)'])
                styled_index_df = index_board_df.style.format({
                    '종가': "{:.2f}",
                    'RSI(14)': "{:.2f}",
                    'SMA(5)': "{:.2f}",
                    'SMA(10)': "{:.2f}",
                    'SMA(20)': "{:.2f}",
                    'SMA(60)': "{:.2f}",
                    'SMA(120)': "{:.2f}",
                    'SMA(200)': "{:.2f}"
                }).map(rsi_color, subset=['RSI(14)'])
                st.dataframe(styled_index_df, hide_index=True, use_container_width=True)


                st.subheader("ETF 현황판", divider="rainbow", anchor="etf_board")
                etf_board_df = pd.DataFrame(sh.worksheet("etf_board").get_all_records())

                etf_chart_df = pd.DataFrame(sh.worksheet("etf_board").get_all_records())
                for col in ['sma5', 'sma10', 'sma20', 'sma60', 'sma120', 'sma200']:
                    etf_chart_df[col] = (etf_chart_df[col] / etf_chart_df['close'] - 1) * 100
                x = ['SMA200', 'SMA120', 'SMA60', 'SMA20', 'SMA10', 'SMA5', '종가']
                p = figure(x_range=x, tools="pan,wheel_zoom,box_zoom,reset,hover,save")
                colors = Category20[len(etf_chart_df['name'])]

                for idx, row in etf_chart_df.iterrows():
                    y = [
                        row['sma200'],
                        row['sma120'],
                        row['sma60'],
                        row['sma20'],
                        row['sma10'],
                        row['sma5'],
                        0
                    ]
                    source = ColumnDataSource(data=dict(x=x, y=y, name=[row['name']] * len(x)))
                    p.line('x', 'y', source=source, line_width=2, legend_label=row['name'], color=colors[idx])
                    p.circle('x', 'y', source=source, size=8, color=colors[idx], legend_label=row['name'])
                hover = p.select(dict(type=HoverTool))
                hover.tooltips = [("종목", "@name"), ("종가 대비(%)", "@y")]
                p.legend.location = "bottom_right"
                p.legend.click_policy = "hide"
                st.bokeh_chart(p, use_container_width=True)

                etf_board_df.rename(columns={
                    "date": "날짜",
                    "name": "종목명",
                    "close": "종가",
                    "rsi14": "RSI(14)",
                    "sma5": "SMA(5)",
                    "sma10": "SMA(10)",
                    "sma20": "SMA(20)",
                    "sma60": "SMA(60)",
                    "sma120": "SMA(120)",
                    "sma200": "SMA(200)",
                    "dividend": "배당금",
                    "dividend_per_close_percent": "배당률",
                    "recorddate": "배당기준일",
                    "paydate": "배당지급일"
                }, inplace=True)
                etf_board_df['RSI(14)'] = etf_board_df['RSI(14)'].round(2)
                etf_board_df[['SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)']] = etf_board_df[['SMA(5)', 'SMA(10)', 'SMA(20)', 'SMA(60)', 'SMA(120)', 'SMA(200)']].round(2)
                styled_etf_df = etf_board_df.style.format({
                    '종가': "{:.2f}",
                    'RSI(14)': "{:.2f}",
                    'SMA(5)': "{:.2f}",
                    'SMA(10)': "{:.2f}",
                    'SMA(20)': "{:.2f}",
                    'SMA(60)': "{:.2f}",
                    'SMA(120)': "{:.2f}",
                    'SMA(200)': "{:.2f}",
                    '배당금': "{:.4f}",
                    '배당률': "{:.3f}"
                }).map(rsi_color, subset=['RSI(14)'])
                st.dataframe(styled_etf_df, hide_index=True, use_container_width=True)

            with etf_tab:                
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
                    st.session_state["logger"].info("USER: %s called ETF LIST API(market:%s).", st.session_state.user, st.session_state.market)
                # DISPLAY ETF LIST with selectbox for etf_name
                with etf_col:
                    if "etf_name" not in st.session_state:
                        st.session_state.etf_name = "BDJ"
                        if "prev_etf_name" not in st.session_state:
                            st.session_state.prev_etf_name = ""
                    st.session_state.etf_name = st.selectbox("종목", st.session_state["etf_list"])
                st.divider()

                info_tab, simulation_tab = st.tabs(["정보", "시뮬레이션"])
                with info_tab:
                    display_report_header(REPORT_VERSION)
                    # GET ETF INFORMATION when etf_name changed
                    if st.session_state.etf_name != st.session_state.prev_etf_name:
                        if "etf_info" not in st.session_state:
                            st.session_state["etf_info"] = list()
                        if "dividend_interval" not in st.session_state:
                            st.session_state["dividend_interval"] = ""
                        st.session_state["etf_info"] = get_etf_info(sh, st.session_state.etf_name)
                        st.session_state.logger.info("USER: %s called ETF INFO API(etf:%s).", st.session_state.user, st.session_state.etf_name)
                        st.session_state["dividend_interval"] = st.session_state.etf_info[5]
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
                        st.session_state.logger.info("USER: %s called ETF RAW DF API(etf:%s).", st.session_state.user, st.session_state.etf_name)
                        st.session_state["prev_etf_name"] = st.session_state.etf_name
                    # DISPLAY ETF RECENT PRICE & DIVIDEND
                    display_stock_recent_price(st.session_state.etf_raw_df[:2], st.session_state.market)
                    display_stock_recent_dividend(st.session_state.etf_dividend_df[:4], st.session_state.market)
                    display_chart_table(st.session_state.etf_raw_df, st.session_state.etf_dividend_df)
                
                with simulation_tab:
                    display_simulate_header(SIMULATE_VERSION)
                    display_simulate(st.session_state.etf_name, st.session_state.etf_raw_df, st.session_state.dividend_interval)

            with chart_tab:
                # TODO: 차트비교 탭: 2개 지표를 골라 시작일 / 끝일 입력받아서 차트 비교 및 상관관계 계산
                st.text("TODO: 지표와 ETF를 선택하여, 차트를 통해 비교 분석할 수 있는 기능을 제공할 예정입니다.")

            with portfolio_tab:
                display_portfolio(st.session_state.user, sh)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(asctime)s | %(message)s')
    logger = logging.getLogger(__name__)
    st.session_state["logger"] = logger
    main()