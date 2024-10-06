import streamlit as st
import logging

from modules.spreadsheets import init_spreadsheet
from modules.display import display_title
from modules.auth import display_auth
from modules.board import display_board_tab
from modules.stock import display_stock_tab
from modules.portfolio import display_portfolio

VERSION = "v1.0.0"

def main():
    sh = init_spreadsheet()
    display_title(VERSION)

    if 'logged_in' not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state.logged_in:
        display_auth(sh)
    else:
        st.text("{} 님이 로그인하셨습니다.".format(st.session_state.user))
        with st.spinner("{} 님 잠시만 기다려주세요...".format(st.session_state.user)):
            board_tab, etf_tab, chart_tab, portfolio_tab = st.tabs(["증시 현황", "종목 분석", "차트 분석", "투자 포트폴리오"])
            with board_tab:
                display_board_tab(sh)
            with etf_tab:
                display_stock_tab(sh)            

    #         with chart_tab:
    #             # TODO: 차트비교 탭: 2개 지표를 골라 시작일 / 끝일 입력받아서 차트 비교 및 상관관계 계산
    #             st.text("TODO: 지표와 ETF를 선택하여, 차트를 통해 비교 분석할 수 있는 기능을 제공할 예정입니다.")

    #         with portfolio_tab:
    #             display_portfolio(st.session_state.user, sh)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(asctime)s | %(message)s')
    logger = logging.getLogger(__name__)
    st.session_state["logger"] = logger
    main()