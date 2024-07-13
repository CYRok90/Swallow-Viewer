import streamlit as st

from modules.spreadsheets import initSpreadSheet, getStockEtfSet
from modules.auth import auth
from modules.display import displayReportHeader, displayTradeHeader

from bokeh.plotting import figure, show

REPORT_VERSION = "v1.0.0"
TRADE_VERSION = "v1.0.0"

def main():
    st.set_page_config(layout="wide")
    
    sh = initSpreadSheet()
    (ok, user) = auth(sh)
    # TODO: 사용자 기록을 남긴다.
    if not ok:
        st.text('존재하지 않는 인증키입니다.')
    st.title('초이하우스 - 락구펀드')
    if ok:
        displayReportHeader(REPORT_VERSION)
        
        market_col, stock_col = st.columns([1,1])
        with market_col:
            market_select = st.radio('주식 시장', [':us:미국', ':kr:한국'])
        market_select = market_select[:-2]
        stock_etf_set = getStockEtfSet(sh, market_select)
        with stock_col:
            stock_etf_select = st.selectbox('종목', stock_etf_set)
        st.divider()

        stock_title, info_col = st.columns([2,1])
        with stock_title:
            st.header(stock_etf_select)
        with info_col:
            # Stock / ETF 
            st.text('ETF / 개별종목')
            st.text('운용자산 / 시가총액: ')
            st.text('상장일: 2024-01-01')
            st.text('배당주기: 연 / 분기 / 월')
        st.divider()

        with st.container(border=True):
            st.subheader("2024-07-11 목요일")
            close_col, diff_col, open_col, high_col, low_col, volume_col = st.columns(6)

            with close_col:
                st.metric(label="종가", value="11,000 원", delta="1,000 원")
            with diff_col:
                st.metric(label="전일 대비", value="+ 10%")
            with open_col:
                st.metric(label="시가", value="9,000 원")
            with high_col:
                st.metric(label="고가", value="11,000 원")
            with low_col:
                st.metric(label="저가", value="8,500 원")
            with volume_col:
                st.metric(label="거래량", value="100,0000", delta="50,000")

        # 배당기준일 배당지급일 배당금 row 3개
        with st.container(border=True):
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value="2024-07-10")
            with pay_col:
                st.metric(label="배당지급일", value="2024-07-15")
            with dividend_col:
                st.metric(label="배당금", value="1,000 원")
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value="2024-06-10", label_visibility="hidden")
            with pay_col:
                st.metric(label="배당지급일", value="2024-06-15", label_visibility="hidden")
            with dividend_col:
                st.metric(label="배당금", value="900 원", label_visibility="hidden")
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value="2024-05-10", label_visibility="hidden")
            with pay_col:
                st.metric(label="배당지급일", value="2024-05-15", label_visibility="hidden")
            with dividend_col:
                st.metric(label="배당금", value="800 원", label_visibility="hidden")
        st.divider()

        # chart
        x = [1, 2, 3, 4, 5]
        y1 = [6, 7, 2, 4, 5]
        y2 = [2, 3, 4, 5, 6]

        # create a new plot with a title and axis labels
        p = figure(title="Multiple glyphs example", x_axis_label="x", y_axis_label="y")

        # add multiple renderers
        p.line(x, y1, legend_label="Temp.", color="blue", line_width=2)
        p.vbar(x=x, top=y2, legend_label="Rate", width=0.5, bottom=0, color="red")

        close_volume_col, dividend_col = st.columns(2)
        with close_volume_col:
            with st.container(border=True):
                st.bokeh_chart(p, use_container_width=True)
                # https://github.com/freyastreamlit/streamlit-lightweight-charts
                st.divider()
                st.text("종가 기준")
                st.text("거래량 기준")
        with dividend_col:
            with st.container(border=True):
                st.bokeh_chart(p, use_container_width=True)
                # https://github.com/freyastreamlit/streamlit-lightweight-charts
                st.divider()
                st.text("배당률 기준")
                st.text("배당금 기준")
        st.divider()

        displayTradeHeader(TRADE_VERSION)

        start_col, end_col = st.columns([1,1])
        with start_col:
            start_date = st.text_input(label="시작일(예시: 1980-01-01)", value="1980-01-01")
        with end_col:
            end_date = st.text_input(label="종료일(예시: 2024-07-21}", value="2024-07-21")
        interval_col, day_col = st.columns([1,1])
        with interval_col:
            investment_interval = st.radio('투자 주기', ['월간', '격주', '매주'])
        with day_col:
            investment_day = st.radio('투자 시점', ['첫날', '중간날', '마지막날'], help="월간 첫날 - 매월 첫 영업일(1일) / 격주 첫날 - 격주 첫 영업일(월요일) / ...")
        init_col, per_col = st.columns([1,1])
        with init_col:
            init_investment_amount = st.number_input(label="초기 투자금($)", min_value=0, value=1000, step=None, on_change=None)
        with per_col:
            per_investment_amount = st.number_input(label="주기별 투자금($)", min_value=0, value=100, step=None, on_change=None)
        buy_col, dividend_col = st.columns([1,1])
        with buy_col:
            buy_price = st.radio('매수 가격', ['종가', '고가'])
        with dividend_col:
            dividend_investment = st.radio('배당금 전부 재투자', ['예', '아니오'])



        # st.progress or st.status


if __name__ == "__main__":
    main()