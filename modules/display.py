import streamlit as st
from datetime import datetime
import locale
from millify import millify

from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data

from modules.spreadsheets import get_etf_info, get_close_table, get_volume_table, get_dividend_rate_table, get_dividend_table

def display_report_header(VERSION):
    col1, col2 = st.columns([1,1], vertical_alignment="bottom")
    with col1:
        st.header("ETF 투자 분석 {version}".format(version=VERSION), divider="rainbow", anchor="report")
    with col2:
        locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")
        today = datetime.now()
        st.markdown("**{date}**".format(date=today.strftime("%Y-%m-%d %A")))

def display_etf_information(sh, etf_name):
    etf_title, info_col = st.columns([2,1])
    info = get_etf_info(sh, etf_name)
    with etf_title:
        st.header(etf_name)
        st.caption(info[7]) # link
        st.markdown(info[6]) # information
    with info_col:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        with st.container(border=True):
            head_col, data_col = st.columns([1,2], vertical_alignment="center")
            with head_col:
                st.markdown("**운 용 사**")
                st.markdown("**총보수료**")
                st.markdown("**운용자산**")
                st.markdown("**상 장 일**")
                st.markdown("**배당주기**")
            with data_col:
                st.markdown("**{}**".format(info[1])) # Company
                st.markdown("**{}**".format(info[2])) # Total Expense Rate
                st.markdown("**{}**".format(info[3])) # aum
                st.markdown("**{}**".format(info[4])) # inception date
                st.markdown("**{}**".format(info[5])) # dividend interval
    st.divider()
    return info[5]

def display_stock_recent_price(stock_data_df):
    with st.container(border=True):
        recent_stock_data_date = datetime.strptime(stock_data_df.iloc[0]["date"], "%Y-%m-%d").strftime("%Y-%m-%d %A")
        st.subheader(recent_stock_data_date)
        close_col, diff_col, open_col, high_col, low_col, volume_col, dividend_col = st.columns(7)
        with close_col:
            recent_stock_data_close = stock_data_df.iloc[0]["close"]
            recent_stock_data_close_diff = round(stock_data_df.iloc[0]["close"] - stock_data_df.iloc[1]["close"], 2)
            st.metric(label="종가", value=recent_stock_data_close, delta=recent_stock_data_close_diff)
        with diff_col:
            recent_stock_data_close_diff_percent = round((recent_stock_data_close_diff / recent_stock_data_close) * 100, 2)
            plus_minus_sign = ""
            if recent_stock_data_close_diff_percent >= 0:
                plus_minus_sign = "+"
            st.metric(label="전일 대비", value= plus_minus_sign + str(recent_stock_data_close_diff_percent) + "%")
        with open_col:
            recent_stock_data_open = stock_data_df.iloc[0]["open"]
            st.metric(label="시가", value=recent_stock_data_open)
        with high_col:
            recent_stock_data_high = stock_data_df.iloc[0]["high"]
            st.metric(label="고가", value=recent_stock_data_high)
        with low_col:
            recent_stock_data_low = stock_data_df.iloc[0]["low"]
            st.metric(label="저가", value=recent_stock_data_low)
        with volume_col:
            recent_stock_data_volume = stock_data_df.iloc[0]["volume"]
            recent_stock_data_volume_diff = int(stock_data_df.iloc[0]["volume"] - stock_data_df.iloc[1]["volume"])
            st.metric(label="거래량", value=millify(recent_stock_data_volume, 3), delta=millify(recent_stock_data_volume_diff, 3))
        with dividend_col:
            recent_stock_data_dividend = stock_data_df.iloc[0]["dividend"]
            recent_stock_data_dividend_rate = stock_data_df.iloc[0]["dividend_per_close_percent"]
            st.metric(label="배당률 - 배당금 {} 기준".format(recent_stock_data_dividend), value="{}%".format(round(recent_stock_data_dividend_rate, 3)))

def display_stock_recent_dividend(dividend_df):
        with st.container(border=True):
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value=dividend_df.iloc[0]["recorddate"])
            with pay_col:
                st.metric(label="배당지급일", value=dividend_df.iloc[0]["paydate"])
            with dividend_col:
                st.metric(label="배당금", value=dividend_df.iloc[0]["dividend"], delta= dividend_df.iloc[0]["dividend"] - dividend_df.iloc[1]["dividend"])
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value=dividend_df.iloc[1]["recorddate"], label_visibility="hidden")
            with pay_col:
                st.metric(label="배당지급일", value=dividend_df.iloc[1]["paydate"], label_visibility="hidden")
            with dividend_col:
                st.metric(label="배당금", value=dividend_df.iloc[1]["dividend"], label_visibility="hidden", delta= dividend_df.iloc[1]["dividend"] - dividend_df.iloc[2]["dividend"])
            record_col, pay_col, dividend_col = st.columns(3)
            with record_col:
                st.metric(label="배당기준일", value=dividend_df.iloc[2]["recorddate"], label_visibility="hidden")
            with pay_col:
                st.metric(label="배당지급일", value=dividend_df.iloc[2]["paydate"], label_visibility="hidden")
            with dividend_col:
                st.metric(label="배당금", value=dividend_df.iloc[2]["dividend"], label_visibility="hidden", delta= dividend_df.iloc[2]["dividend"] - dividend_df.iloc[3]["dividend"])
        st.divider()

# TODO: 종가 그래프에 고점, 저점 포인트 표시
# TODO: 종가 그래프에서 시작점 -> 끝점까지에 대한 점선 추세선을 그리자.
# TODO: 거래량 그래프에서 평균값 점선 그래프 그리자.

# TODO: 배당금 그래프에서 시작점 -> 끝쩜까지에 대한 점선 추세선을 그리자.
# TODO: 배당금 그래프에서 배당락일에 포인트를 표시
# TODO: 배당률 그래프에서 평균값 점선 그래프 그리자.

def display_chart_table(stock_raw_df, dividend_df):
    close_volume_col, dividend_col = st.columns(2)
    with close_volume_col:
        with st.container(border=True):
            display_stock_close_volume_chart(stock_raw_df)
            st.divider()
            st.markdown("##### 종가 비교")
            st.dataframe(data=get_close_table(stock_raw_df), use_container_width=True)
            st.markdown("##### 거래량 비교")
            st.dataframe(data=get_volume_table(stock_raw_df), use_container_width=True)
    with dividend_col:
        with st.container(border=True):
            display_stock_dividend_chart(stock_raw_df, dividend_df)
            st.divider()
            st.markdown("##### 배당률 비교")
            st.dataframe(data=get_dividend_rate_table(stock_raw_df), use_container_width=True)
            st.markdown("##### 배당금 비교")
            st.dataframe(data=get_dividend_table(dividend_df), use_container_width=True)
    st.divider()

def get_color(current, previous):
    if current >= previous:
        return "rgba(0, 150, 136, 0.8)"
    else:
        return "rgba(255, 82, 82, 0.8)"


# TODO: 디자인을 조금더 바꿔야할수도. RSI도 넣어볼까...?
def display_stock_close_volume_chart(stock_raw_df):
    stock_raw_df = stock_raw_df.sort_values(by="date", ascending=True)
    close_series = stock_raw_df.apply(lambda row: {"time": row["date"], "value": row["close"]}, axis=1).tolist()
    
    volume_series = []
    previous_close = None
    for _, row in stock_raw_df.iterrows():
        if previous_close is None:
            color = "rgba(0, 150, 136, 0.8)"  # 첫날은 색상 고정
        else:
            color = get_color(row["close"], previous_close)
        volume_series.append({
            "time": row["date"],
            "value": row["volume"],
            "color": color
        })
        previous_close = row["close"]

    chart_options = {
        "height": 600,
        "rightPriceScale": {
            "scaleMargins": {
                "top": 0.2,
                "bottom": 0.25,
            },
            "borderVisible": False,
        },
        "overlayPriceScales": {
            "scaleMargins": {
                "top": 0.7,
                "bottom": 0,
            }
        },
        "layout": {
            "background": {
                "type": 'solid',
                "color": '#131722'
            },
            "textColor": '#d1d4dc',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(42, 46, 57, 0)',
            },
            "horzLines": {
                "color": 'rgba(42, 46, 57, 0.6)',
            }
        }
    }

    price_volume_series = [
        {
            "type": 'Area',
            "data": close_series,
            "options": {
                "topColor": 'rgba(38,198,218, 0.56)',
                "bottomColor": 'rgba(38,198,218, 0.04)',
                "lineColor": 'rgba(38,198,218, 1)',
                "lineWidth": 2,
                "priceFormat": {
                    "type": 'price',
                },
            }
        },
        {
            "type": 'Histogram',
            "data": volume_series,
            "options": {
                "color": '#26a69a',
                "priceFormat": {
                    "type": 'volume',
                },
                "priceScaleId": "" # set as an overlay setting,
            },
            "priceScale": {
                "scaleMargins": {
                    "top": 0.7,
                    "bottom": 0,
                }
            }
        }
    ]

    return renderLightweightCharts([
        {
            "chart": chart_options,
            "series": price_volume_series
        }
    ], 'priceAndVolume')

def display_stock_dividend_chart(stock_raw_df, dividend_df):
    dividend_rows = []
    dividend_df = dividend_df.sort_values(by="recorddate", ascending=True)
    for _, dividend_row in dividend_df.iterrows():
        record_date = dividend_row["recorddate"]
        row_on_ex_date = stock_raw_df[(stock_raw_df["date"] < record_date) & (stock_raw_df["recorddate"] == record_date)].iloc[1]
        dividend_rows.append(row_on_ex_date)
    recent_stock_data = stock_raw_df[:1].iloc[0]
    if recent_stock_data["date"] >= recent_stock_data["recorddate"]:
        dividend_rows.append(recent_stock_data)

    

    # dividend_rate_series = stock_raw_df.apply(lambda row: {"time": row["date"], "value": row["dividend_per_close_percent"]}, axis=1).tolist()

    dividend_series = []
    dividend_rate_series = []

    previous_dividend = None
    for row in dividend_rows:
        if previous_dividend is None:
            color = "rgba(0, 150, 136, 0.8)"  # 첫날은 색상 고정
        else:
            color = get_color(row["dividend"], previous_dividend)
        dividend_series.append({
            "time": row["date"],
            "value": row["dividend"],
            "color": color
        })
        dividend_rate_series.append({
            "time": row["date"],
            "value": row["dividend_per_close_percent"]
        })
        previous_dividend = row["dividend"]

    chart_options = {
        "height": 600,
        "rightPriceScale": {
            # "autoScale": True,
            "scaleMargins": {
                "top": 0.2,
                "bottom": 0.25,
            },
            "borderVisible": False,
        },
        "overlayPriceScales": {
            # "autoScale": True,
            "scaleMargins": {
                "top": 0.7,
                "bottom": 0,
            }
        },
        "layout": {
            "background": {
                "type": 'solid',
                "color": '#131722'
            },
            "textColor": '#d1d4dc',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(42, 46, 57, 0)',
            },
            "horzLines": {
                "color": 'rgba(42, 46, 57, 0.6)',
            }
        }
    }

    rate_dividend_series = [
        {
            "type": 'Line',
            "data": dividend_rate_series,
            "options": {
                "topColor": 'rgba(38,198,218, 0.56)',
                "bottomColor": 'rgba(38,198,218, 0.04)',
                "lineColor": 'rgba(38,198,218, 1)',
                "lineWidth": 2,
                "priceFormat": {
                    "type": 'price',
                    "minMove": 0.00001,
                    "precision": 5,
                },
                "priceScaleId": "", # set as an overlay setting,
                "priceScale": {
                    "scaleMargins": {
                        "top": 0.7,
                        "bottom": 0,
                    }
                }
            }
        },
        {
            "type": 'Histogram',
            "data": dividend_series,
            "options": {
                "color": '#26a69a',
                "priceFormat": {
                    "type": 'price',
                    "minMove": 0.0001,
                    "precision": 4,
                },
            },
        }
    ]

    return renderLightweightCharts([
        {
            "chart": chart_options,
            "series": rate_dividend_series
        }
    ], 'dividendAndrate')

