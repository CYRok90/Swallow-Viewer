import streamlit as st
import pandas as pd

@st.experimental_fragment
def display_portfolio(user, sh):
    all_portfolio_df = pd.DataFrame(sh.worksheet("portfolio").get_all_records())
    # print(all_portfolio_df)
    user_portfolio_df = all_portfolio_df[all_portfolio_df["user"] == user][["종목명", "매입 금액", "보유 수량"]].reset_index(drop=True)

    user_portfolio_df = st.data_editor(user_portfolio_df, num_rows='dynamic', hide_index=True, use_container_width=True)
    # print(user_portfolio_df)

    index_board_df = pd.DataFrame(sh.worksheet("index_board").get_all_records())
    usd_krw = index_board_df.loc[index_board_df["name"] == "USD_KRW", "close"].values[0]

    etf_board_df = pd.DataFrame(sh.worksheet("etf_board").get_all_records())
    etf_info_df = pd.DataFrame(sh.worksheet("etf_info_list").get_all_records())

    # 전체 손익 및 매입 금액 합계를 계산하기 위한 초기값 설정
    all_total_profit = 0.0
    all_purchased_total_price = 0.0

    # 전체 손익과 매입 금액을 계산하는 첫 번째 루프
    for _, row in user_portfolio_df.iterrows():
        name = row["종목명"]
        multiple = 1 if name.startswith("TIGER") or name.startswith("KODEX") else usd_krw
        purchased_total_price = row["매입 금액"] * multiple
        num_of_shares = row["보유 수량"]

        # 현재 가격이 있는지 확인
        if name in etf_board_df["name"].values:
            current_price = etf_board_df.loc[etf_board_df["name"] == name, "close"].values[0]
        else:
            continue
        current_total_price = current_price * num_of_shares * multiple
        total_profit = current_total_price - purchased_total_price

        # 전체 합산값 갱신
        all_purchased_total_price += purchased_total_price
        all_total_profit += total_profit

    # 수익률 계산을 위한 빈 DataFrame 생성
    profit_columns = [
        "종목명", "수익률(%)", "총 손익(₩)", "손익 비중(%)", "현재 금액(₩)", 
        "매입 금액(₩)", "보유 비중(%)", "현재가", "평균 단가", "보유 수량"
    ]
    profit_df = pd.DataFrame(columns=profit_columns)

    # 각 종목별 데이터를 계산하여 새로운 DataFrame에 추가하는 두 번째 루프
    all_current_total_price = 0.0  # 현재 금액의 총합을 다시 계산하기 위한 초기값

    for _, row in user_portfolio_df.iterrows():
        name = row["종목명"]
        multiple = 1 if name.startswith("TIGER") or name.startswith("KODEX") else usd_krw

        purchased_total_price = row["매입 금액"] * multiple
        num_of_shares = row["보유 수량"]
        if name in etf_board_df["name"].values:
            current_price = etf_board_df.loc[etf_board_df["name"] == name, "close"].values[0]
        else:
            continue
        average_price = row["매입 금액"] / num_of_shares if num_of_shares != 0 else 0
        current_total_price = current_price * num_of_shares * multiple
        total_profit = current_total_price - purchased_total_price
        profit_percent = (total_profit / purchased_total_price) * 100 if purchased_total_price != 0 else 0

        # 손익 비중 및 보유 비중 계산
        profit_charge = (total_profit / all_total_profit) * 100 if all_total_profit != 0 else 0
        total_price_charge = (purchased_total_price / all_purchased_total_price) * 100 if all_purchased_total_price != 0 else 0

        # 계산 결과를 DataFrame에 추가
        new_row =  pd.DataFrame({
            "종목명": [name],
            "수익률(%)": [round(profit_percent, 3)],
            "총 손익(₩)": [round(total_profit, 3)],
            "손익 비중(%)": [round(profit_charge, 3)],
            "현재 금액(₩)": [round(current_total_price, 3)],
            "매입 금액(₩)": [round(purchased_total_price, 3)],
            "보유 비중(%)": [round(total_price_charge, 3)],
            "현재가": [round(current_price, 3)],
            "평균 단가": [round(average_price, 3)],
            "보유 수량": [num_of_shares]
        })
        profit_df = pd.concat([profit_df, new_row], ignore_index=True)
        all_current_total_price += current_total_price  # 현재 금액 총합 계산
    
    # 최종 합계 행 추가
    total_row = pd.DataFrame({
        "종목명": ["합산"],
        "수익률(%)": [round((all_total_profit / all_purchased_total_price) * 100, 3) if all_purchased_total_price != 0 else 0],
        "총 손익(₩)": [round(all_total_profit, 3)],
        "손익 비중(%)": [100],
        "현재 금액(₩)": [round(all_current_total_price, 3)],
        "매입 금액(₩)": [round(all_purchased_total_price, 3)],
        "보유 비중(%)": [100],
        "현재가": ["-"],
        "평균 단가": ["-"],
        "보유 수량": ["-"]
    })
    profit_df = pd.concat([profit_df, total_row], ignore_index=True)

    all_dividend = 0.0
    all_purchased_total_price = 0.0

    for _, row in user_portfolio_df.iterrows():
        name = row["종목명"]
        multiple = 1 if name.startswith("TIGER") or name.startswith("KODEX") else usd_krw
        purchased_total_price = row["매입 금액"] * multiple
        num_of_shares = row["보유 수량"]

        # 배당금이 있는지 확인
        if name in etf_board_df["name"].values:
            dividend_times = 12 # 월간
            if name in etf_info_df["name"].values:
                if etf_info_df.loc[etf_info_df["name"] == name, "dividend_interval"].values[0] == "분기":
                    dividend_times = 4
                elif etf_info_df.loc[etf_info_df["name"] == name, "dividend_interval"].values[0] == "연간":
                    dividend_times = 1
                elif etf_info_df.loc[etf_info_df["name"] == name, "dividend_interval"].values[0] == "반기":    
                    dividend_times = 2
            dividend = etf_board_df.loc[etf_board_df["name"] == name, "dividend"].values[0] * num_of_shares * multiple * dividend_times
        else:
            continue

        # 전체 합산값 갱신
        all_purchased_total_price += purchased_total_price
        all_dividend += dividend

    dividend_columns = [
        "종목명", "배당률(%)", "총 배당(₩)", "배당 비중(%)",
        "매입 금액(₩)", "보유 비중(%)", "주당 배당금", "현재 배당률(%)", "배당기준일", "배당지급일", "배당 주기"
    ]
    dividend_df = pd.DataFrame(columns=dividend_columns)

    for _, row in user_portfolio_df.iterrows():
        name = row["종목명"]
        multiple = 1 if name.startswith("TIGER") or name.startswith("KODEX") else usd_krw

        purchased_total_price = row["매입 금액"] * multiple
        num_of_shares = row["보유 수량"]
        if name in etf_board_df["name"].values:
            dividend = etf_board_df.loc[etf_board_df["name"] == name, "dividend"].values[0] * num_of_shares * multiple
        else:
            continue
        dividend_percent = (dividend / purchased_total_price) * 100 if purchased_total_price != 0 else 0
        dividend_charge = (dividend / all_dividend) * 100 if all_dividend != 0 else 0
        total_price_charge = (purchased_total_price / all_purchased_total_price) * 100 if all_purchased_total_price != 0 else 0

        new_row =  pd.DataFrame({
            "종목명": [name],
            "배당률(%)": [round(dividend_percent, 3)],
            "총 배당(₩)": [round(dividend, 3)],
            "배당 비중(%)": [round(dividend_charge, 3)],
            "매입 금액(₩)": [round(purchased_total_price, 3)],
            "보유 비중(%)": [round(total_price_charge, 3)],
            "주당 배당금": [round(etf_board_df.loc[etf_board_df["name"] == name, "dividend"].values[0], 4)],
            "현재 배당률(%)": [round(etf_board_df.loc[etf_board_df["name"] == name, "dividend_per_close_percent"].values[0], 3)],
            "배당기준일": [etf_board_df.loc[etf_board_df["name"] == name, "recorddate"].values[0]],
            "배당지급일": [etf_board_df.loc[etf_board_df["name"] == name, "paydate"].values[0]],
            "배당 주기": [etf_info_df.loc[etf_info_df["name"] == name, "dividend_interval"].values[0]]
        })
        dividend_df = pd.concat([dividend_df, new_row], ignore_index=True)
    total_row = pd.DataFrame({
        "종목명": ["합산"],
        "배당률(%)": [round((all_dividend / all_purchased_total_price) * 100, 3) if all_purchased_total_price != 0 else 0],
        "총 배당(₩)": [round(all_dividend, 3)],
        "배당 비중(%)": [100],
        "매입 금액(₩)": [round(all_purchased_total_price, 3)],
        "보유 비중(%)": [100],
        "주당 배당금": ["-"],
        "현재 배당률(%)": ["-"],
        "배당기준일": ["-"],
        "배당지급일": ["-"],
        "배당 주기": ["-"]
    })
    dividend_df = pd.concat([dividend_df, total_row], ignore_index=True)

    usdkrw_col, current_total_col, purchased_total_col, profit_total_col, profit_percent_col, dividend_total_col, dividend_percent_col = st.columns([1,1,1,1,1,1,1])
    with usdkrw_col:
        st.metric(label="환율 ($)", value=f"₩{usd_krw:,.2f}")
    with current_total_col:
        st.metric(label="현재 금액", value=f"₩{round(all_current_total_price, 3):,.2f}")
    with purchased_total_col:
        st.metric(label="투자 금액", value=f"₩{round(all_purchased_total_price, 3):,.2f}")
    with profit_total_col:
        st.metric(label="총 손익", value=f"₩{round(all_total_profit, 3):,.2f}")
    with profit_percent_col:
        st.metric(label="수익률", value=f"{round((all_total_profit / all_purchased_total_price) * 100, 3) if all_purchased_total_price != 0 else 0:,.2f}%")
    with dividend_total_col:
        st.metric(label="연간 배당", value=f"₩{round(all_dividend, 3):,.2f}")
    with dividend_percent_col:
        st.metric(label="배당률", value=f"{round((all_dividend / all_purchased_total_price) * 100, 3) if all_purchased_total_price != 0 else 0:,.2f}%")

    st.dataframe(profit_df, use_container_width=True, hide_index=True)
    st.dataframe(dividend_df, use_container_width=True, hide_index=True)

    return