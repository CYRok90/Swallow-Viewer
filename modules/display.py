import streamlit as st
from datetime import datetime
import locale

def displayReportHeader(VERSION):
    col1, col2 = st.columns([1,1], vertical_alignment='bottom')
    with col1:
        st.header('투자 분석 {version}'.format(version=VERSION), divider='rainbow', anchor="report")
    with col2:
        locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
        today = datetime.now()
        st.markdown('**{date}**'.format(date=today.strftime("%Y-%m-%d %A")))

def displayTradeHeader(VERSION):
    st.header('투자 시뮬레이션 {version}'.format(version=VERSION), divider='rainbow', anchor="trade")