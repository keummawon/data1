import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# =========================================
# 기본 설정
# =========================================
st.set_page_config(page_title="글로벌·한국 주식 분석기", layout="wide", page_icon="📈")

st.title("📈 글로벌·한국 주식 데이터 분석 웹앱")
st.caption("yfinance + Plotly 기반 | 초보자도 이해하기 쉬운 설명 포함")

# =========================================
# 사이드바 - 종목 입력
# =========================================
st.sidebar.header("🔍 종목 검색 설정")

st.sidebar.markdown("""
**티커 입력 예시**
- 미국 주식: `AAPL`, `TSLA`, `MSFT`, `NVDA`
- 한국 주식(코스피): `005930.KS` (삼성전자)
- 한국 주식(코스닥): `035720.KQ` (카카오)
""")

ticker_input = st.sidebar.text_input("티커(Ticker) 입력", value="AAPL")

period_option = st.sidebar.selectbox(
    "조회 기간",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3
)

interval_option = st.sidebar.selectbox(
    "봉 간격(Interval)",
    ["1d", "1wk", "1mo"],
    index=0
)

show_ma = st.sidebar.checkbox("이동평균선(MA) 표시", value=True)
ma_periods = st.sidebar.multiselect("이동평균 기간(일)", [5, 20, 60, 120, 200], default=[20, 60])

show_volume = st.sidebar.checkbox("거래량 표시", value=True)
show_rsi = st.sidebar.checkbox("RSI 표시", value=False)

# =========================================
# 데이터 불러오기
# =========================================
@st.cache_data(ttl=600)
def load_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    info = stock.info
    return df, info

if ticker_input:
    try:
        with st.spinner("데이터 불러오는 중..."):
            df, info = load_data(ticker_input, period_option, interval_option)

        if df.empty:
            st.error("❌ 데이터를 찾을 수 없습니다. 티커를 다시 확인해주세요.")
        else:
            # -----------------------------
            # 기업 개요
            # -----------------------------
            col1, col2, col3, col4 = st.columns(4)
            company_name = info.get("longName", ticker_input)
            currency = info.get("currency", "")
            current_price = info.get("currentPrice", df["Close"].iloc[-1])
            prev_close = info.get("previousClose", df["Close"].iloc[-2] if len(df) > 1 else current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0

            col1.metric("종목명", company_name)
            col2.metric("현재가", f"{current_price:,.2f} {currency}", f"{change:+.2f} ({change_pct:+.2f}%)")
            col3.metric("52주 최고", f"{info.get('fiftyTwoWeekHigh', 'N/A')}")
            col4.metric("52주 최저", f"{info.get('fiftyTwoWeekLow', 'N/A')}")

            st.divider()

            # -----------------------------
            # 이동평균 계산
            # -----------------------------
            for ma in ma_periods:
                df[f"MA{ma}"] = df["Close"].rolling(window=ma).mean()

            # RSI 계산
            if show_rsi:
                delta = df["Close"].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                df["RSI"] = 100 - (100 / (1 + rs))

            # -----------------------------
            # 차트 구성 (캔들스틱 + 거래량 + RSI)
            # -----------------------------
            rows = 1 + (1 if show_volume else 0) + (1 if show_rsi else 0)
            row_heights = [0.6] + [0.2] * (rows - 1) if rows > 1 else [1]

            fig = make_subplots(
                rows=rows, cols=1, shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=row_heights
            )

            # 캔들스틱
            fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="가격"
            ), row=1, col=1)

            # 이동평균선
            if show_ma:
                colors = ["orange", "purple", "green", "brown", "gray"]
                for i, ma in enumerate(ma_periods):
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df[f"MA{ma}"], name=f"MA{ma}",
                        line=dict(width=1.5, color=colors[i % len(colors)])
                    ), row=1, col=1)

            current_row = 2
            # 거래량
            if show_volume:
                colors_vol = ["red" if c < o else "green" for c, o in zip(df["Close"], df["Open"])]
                fig.add_trace(go.Bar(
                    x=df.index, y=df["Volume"], name="거래량", marker_color=colors_vol
                ), row=current_row, col=1)
                current_row += 1

            # RSI
            if show_rsi:
                fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="blue")), row=current_row, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)

            fig.update_layout(
                height=800,
                xaxis_rangeslider_visible=False,
                title=f"{company_name} ({ticker_input}) 주가 차트",
                template="plotly_white",
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)

            # -----------------------------
            # 원본 데이터 테이블
            # -----------------------------
            with st.expander("📋 원본 데이터 보기"):
                st.dataframe(df.tail(50).sort_index(ascending=False), use_container_width=True)

                csv = df.to_csv().encode("utf-8-sig")
                st.download_button("📥 CSV 다운로드", csv, f"{ticker_input}_data.csv", "text/csv")

    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다: {e}")

st.divider()

# =========================================
# 📚 주식 용어 사전 (초보자용)
# =========================================
st.header("📚 주식 용어 쉽게 알아보기")

terms = {
    "캔들스틱(Candlestick)": "하루(또는 특정 기간) 동안의 시가·고가·저가·종가를 하나의 막대로 표현한 차트예요. "
                          "몸통이 빨간색(또는 채워짐)이면 시가보다 종가가 낮아진 것(하락), 초록색(비어있음)이면 종가가 시가보다 높아진 것(상승)을 의미해요.",
    "이동평균선(MA, Moving Average)": "최근 N일 동안의 평균 가격을 선으로 이어 그린 거예요. 예를 들어 'MA20'은 최근 20일간의 평균 종가를 뜻하며, "
                                  "주가의 큰 흐름(추세)을 파악할 때 사용해요. 단기 이평선이 장기 이평선을 위로 뚫고 올라가면 '골든크로스'(상승 신호로 해석), "
                                  "반대는 '데드크로스'(하락 신호로 해석)라고 불러요.",
    "거래량(Volume)": "해당 기간 동안 사고팔린 주식의 수량이에요. 거래량이 급증하면서 가격이 오르면 매수세가 강하다는 신호로, "
                    "거래량이 적은데 가격만 움직이면 신뢰도가 낮은 움직임일 수 있어요.",
    "RSI(상대강도지수, Relative Strength Index)": "최근 가격 움직임을 바탕으로 '과매수(너무 많이 올랐다)' 또는 '과매도(너무 많이 떨어졌다)' 상태를 0~100 사이 숫자로 나타내는 지표예요. "
                                              "보통 70 이상이면 과매수(조정 가능성), 30 이하면 과매도(반등 가능성)로 해석해요. 다만 절대적인 신호는 아니고 참고 지표로만 활용해야 해요.",
    "52주 최고/최저가": "최근 1년(52주) 동안 기록한 가장 높은 가격과 가장 낮은 가격이에요. 현재가가 52주 최고가에 가까우면 '신고가 경신' 흐름, "
                     "52주 최저가에 가까우면 저평가 구간일 수 있다는 신호로 참고돼요.",
    "티커(Ticker)": "주식 종목을 구분하는 고유 코드예요. 미국 주식은 알파벳(예: AAPL=애플), 한국 주식은 야후 파이낸스 기준으로 종목코드 뒤에 "
                 "코스피는 '.KS', 코스닥은 '.KQ'를 붙여요. (예: 삼성전자=005930.KS)",
    "시가/고가/저가/종가 (OHLC)": "시가(Open)는 그날 처음 거래된 가격, 고가(High)는 가장 높았던 가격, 저가(Low)는 가장 낮았던 가격, "
                              "종가(Close)는 그날 마지막으로 거래된 가격이에요. 캔들차트의 기본 재료가 되는 4가지 값이에요.",
    "시가총액(Market Cap)": "현재 주가 × 발행주식수로 계산되는, 그 회사 전체의 시장 가치예요. 기업의 규모를 비교할 때 가장 흔히 쓰이는 지표예요.",
}

for term, desc in terms.items():
    with st.expander(f"🔹 {term}"):
        st.write(desc)

st.divider()
st.caption("💡 본 앱은 투자 참고용 정보 제공을 목적으로 하며, 투자 판단의 책임은 투자자 본인에게 있습니다.")
