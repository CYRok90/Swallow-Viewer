import streamlit as st
import logging
import requests
import pandas as pd

SIMULATE_API_URL = st.secrets["simulate_api_url"]

def display_simulate_header(VERSION):
    st.header("ETF 투자 시뮬레이션 {version}".format(version=VERSION), divider="rainbow", anchor="trade")

def display_simulate(etf_name, etf_raw_df, dividend_interval):
    start_col, end_col = st.columns([1,1])
    with start_col:
        start_date = st.text_input(label="시작일(예시: 1980-01-01)", value="1980-01-01")
    with end_col:
        end_date = st.text_input(label="종료일(예시: 2024-07-21}", value="2024-07-21")
    interval_col, day_col = st.columns([1,1])
    with interval_col:
        investment_interval = st.radio("투자 주기", ["월간", "격주", "매주"], key="investment_interval")
        if investment_interval == "월간":
            investment_interval = "monthly"
        elif investment_interval == "격주":
            investment_interval = "biweekly"
        elif investment_interval == "매주":
            investment_interval = "weekly"
    with day_col:
        investment_day = st.radio("투자 시점", ["첫날", "중간날", "마지막날"], help="월간 첫날 - 매월 첫 영업일(1일) / 격주 첫날 - 격주 첫 영업일(월요일) / ...")
        if investment_day == "첫날":
            investment_day = "first"
        elif investment_day == "중간날":
            investment_day = "middle"
        elif investment_day == "마지막날":
            investment_day = "last"
    init_col, per_col = st.columns([1,1])
    with init_col:
        init_investment_amount = st.number_input(label="초기 투자금($)", min_value=0, value=1000, step=None, on_change=None)
    with per_col:
        per_investment_amount = st.number_input(label="주기별 투자금($)", min_value=0, value=100, step=None, on_change=None)
    buy_col, dividend_col = st.columns([1,1])
    with buy_col:
        buy_price = st.radio("매수 가격", ["종가", "고가"])
        if buy_price == "종가":
            buy_price = "close"
        elif buy_price == "고가":
            buy_price = "high"
    with dividend_col:
        dividend_investment = st.radio("배당금 전부 재투자", ["예", "아니오"])
        if dividend_investment == "예":
            dividend_investment = "true"
        elif dividend_investment == "아니오":
            dividend_investment = "false"
    trade_fee_col, dividends_fee_col = st.columns([1,1])
    with trade_fee_col:
        trade_fee = st.number_input(label="거래 수수료 및 세금(%)", min_value=0.0, value=1.0, step=0.01, on_change=None)
        trade_fee *= 0.01
    with dividends_fee_col:
        dividends_fee = st.number_input(label="배당 수수료 및 세금(%)", min_value=0.0, value=16.0, step=0.01, on_change=None)
        dividends_fee *= 0.01

    params = {
        "api_key": st.session_state.api_key,
        "start_date": start_date,
        "end_date": end_date,
        "init_investment_amount": init_investment_amount,
        "investment_interval": investment_interval,
        "investment_day": investment_day,
        "per_investment_amount": per_investment_amount,
        "buy_price": buy_price,
        "dividends_investment": str(dividend_investment).lower(),
        "trade_fee": trade_fee,
        "dividends_fee": dividends_fee,
        "name": etf_name
    }
    if st.button("시뮬레이션!", type="primary"):
        st.session_state["logger"].info("USER: %s called SIMULATE API(etf:%s).", st.session_state.user, st.session_state.etf_name)
        with st.spinner("시뮬레이션 중입니다..."):
            response = requests.get(SIMULATE_API_URL, params=params)
            if response.status_code == 200:
                result = response.json()["result"]
                df1 = pd.DataFrame(result["매매 일지"])
                df2 = pd.DataFrame(result["배당 일지"])
                df3 = pd.DataFrame(result["예수금"])
                df4 = pd.DataFrame(result["주식 잔고"])
                
                st.write("매매 일지")
                st.dataframe(df1)
                st.write("배당 일지")
                st.dataframe(df2)
                st.write("예수금")
                st.dataframe(df3)
                st.write("주식 잔고")
                st.dataframe(df4)

                recent_dividend_balance_row = df2.tail(1).iloc[0]
                recent_deposit_balance_row = df3.tail(1).iloc[0]
                recent_stock_balance_row = df4.tail(1).iloc[0]
                recent_stock_row = etf_raw_df[etf_raw_df["date"] <= end_date].head(1).iloc[0]

                # TODO: 결과 차트
                # TODO: 주식 잔고 - X축:날짜 / Y축: 매입금액, 평가금액, 평가손익= 평가금액 - 매입금액, 수익률= 평가손익 / 매입금액
                # TODO: 주식 잔고 - X축:날짜 / Y축: 누적투자금, 평가금액, 평가손익= 평가금액 - 누적투자금, 수익률= 평가손익 / 누적투자금
                # TODO: 배당 일지 - X축:날짜 / Y축: 보유수량, 총배당금(세후), 배당률=총배당금(세후) / 누적투자금, 배당률=총배당금(세후) / 매입금액
                # TODO: 결과 테이블
                st.text("현재 주식 평균단가 {} - {}주, 최근 배당 기준 {}마다 세후 배당금 {}". \
                        format(recent_stock_balance_row["평균 단가"], recent_stock_balance_row["보유 수량"], dividend_interval, recent_dividend_balance_row["총 배당금(세후)"]))
                st.text("누적 투자금: {}, 누적 배당금: {}, 누적 매입금액: {}, 남은 예수금: {}". \
                        format(recent_deposit_balance_row["누적 투자금"], recent_deposit_balance_row["누적 배당금"], recent_stock_balance_row["매입 금액"], recent_deposit_balance_row["예수금"]))
                st.text("배당률 = 총 배당금(세후) / 누적투자금 = {} / {} = {}". \
                        format(recent_dividend_balance_row["총 배당금(세후)"], recent_deposit_balance_row["누적 투자금"], recent_dividend_balance_row["총 배당금(세후)"] / recent_deposit_balance_row["누적 투자금"]))
                st.text("배당률 = 총 배당금(세후) / 매입금액 = {} / {} = {}". \
                        format(recent_dividend_balance_row["총 배당금(세후)"], recent_stock_balance_row["매입 금액"], recent_dividend_balance_row["총 배당금(세후)"] / recent_stock_balance_row["매입 금액"]))
                st.text("날짜 기준: {}".format(recent_stock_row["date"]))
                st.text("평가 손익 = 평가금액 - 누적 투자금 = {} - {} = {}". \
                        format(recent_stock_row["close"] * recent_stock_balance_row["보유 수량"], recent_deposit_balance_row["누적 투자금"], recent_stock_row["close"] * recent_stock_balance_row["보유 수량"] - recent_deposit_balance_row["누적 투자금"]))
                st.text("평가 손익 = 평가금액 - 누적 매입금액 = {} - {} = {}". \
                        format(recent_stock_row["close"] * recent_stock_balance_row["보유 수량"], recent_stock_balance_row["매입 금액"], recent_stock_row["close"] * recent_stock_balance_row["보유 수량"] - recent_stock_balance_row["매입 금액"]))
                
                # TODO: 수익률= 평가손익 / 누적투자금, 수익률= 평가손익 / 매입금액, 
            else:
                st.error("Error: " + response.json().get("error", "Unknown error"))