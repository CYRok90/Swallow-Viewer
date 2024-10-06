import streamlit as st
import pandas as pd
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource

from modules.spreadsheets import get_index_board_table, get_etf_board_table

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

def fade_unselected(row, selected_names):
    """선택되지 않은 지수의 행을 흐리게 표시하는 함수"""
    if ('지수명' in row.keys() and row['지수명'] not in selected_names) or ('종목명' in row.keys() and row['종목명'] not in selected_names):
        return ['color: lightgray'] * len(row)
    else:
        return [''] * len(row)

def display_board_tab(sh):
    st.subheader("지수", divider="rainbow", anchor="market_board")
    index_board_df = pd.DataFrame(get_index_board_table(sh))
    index_chart_df = index_board_df.copy(deep=True)

    index_names = index_chart_df['name'].tolist()
    selected_indices = st.multiselect("지수", index_names, default=index_names, label_visibility="collapsed")
    
    index_chart_df = index_chart_df[index_chart_df['name'].isin(selected_indices)]
    for col in ['sma5', 'sma10', 'sma20', 'sma60', 'sma120', 'sma200']:
        index_chart_df[col] = (index_chart_df[col] / index_chart_df['close'] - 1) * 100
    x = ['SMA200', 'SMA120', 'SMA60', 'SMA20', 'SMA10', 'SMA5', '종가']
    p = figure(x_range=x, tools="pan,wheel_zoom,box_zoom,reset,hover,save")
    colors = Category20[20]
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
    styled_index_df = index_board_df.style.format({
        '종가': "{:.2f}",
        'RSI(14)': "{:.2f}",
        'SMA(5)': "{:.2f}",
        'SMA(10)': "{:.2f}",
        'SMA(20)': "{:.2f}",
        'SMA(60)': "{:.2f}",
        'SMA(120)': "{:.2f}",
        'SMA(200)': "{:.2f}"
    }).map(rsi_color, subset=['RSI(14)']).apply(fade_unselected, axis=1, selected_names=selected_indices)
    st.dataframe(styled_index_df, hide_index=True, use_container_width=True)


    st.subheader("종목", divider="rainbow", anchor="etf_board")
    etf_board_df = pd.DataFrame(get_etf_board_table(sh))
    etf_chart_df = etf_board_df.copy(deep=True)

    etf_names = etf_chart_df['name'].tolist()
    selected_etfs = st.multiselect("종목", etf_names, default=etf_names, label_visibility="collapsed")

    etf_chart_df = etf_chart_df[etf_chart_df['name'].isin(selected_etfs)]
    for col in ['sma5', 'sma10', 'sma20', 'sma60', 'sma120', 'sma200']:
        etf_chart_df[col] = (etf_chart_df[col] / etf_chart_df['close'] - 1) * 100
    x = ['SMA200', 'SMA120', 'SMA60', 'SMA20', 'SMA10', 'SMA5', '종가']
    p = figure(x_range=x, tools="pan,wheel_zoom,box_zoom,reset,hover,save")
    colors = Category20[20]
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
    }).map(rsi_color, subset=['RSI(14)']).apply(
        fade_unselected, axis=1, selected_names=selected_etfs)
    st.dataframe(styled_etf_df, hide_index=True, use_container_width=True)
