import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================
# 기본 설정
# =========================================
st.set_page_config(page_title="한국 인기 주식 분석 & 추천", layout="wide", page_icon="🇰🇷")

st.title("🇰🇷 한국 인기 주식 분석 & 추천 웹앱")
st.caption("yfinance + Plotly 기반 | 기술적 지표로 인기 종목을 자동 분석해드려요")

st.warning("⚠️ 본 서비스는 기술적 지표를 기반으로 한 참고 정보이며, 투자 자문이 아닙니다. 모든 투자 판단과 책임은 투자자 본인에게 있습니다.")

# =========================================
# 인기 한국 종목 리스트 (티커: 종목명)
# =========================================
KOREAN_STOCKS = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "207940.KS": "삼성바이오로직스",
    "005380.KS": "현대차",
    "000270.KS": "기아",
    "005490.KS": "POSCO홀딩스",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
    "051910.KS": "LG화학",
    "006400.KS": "삼성SDI",
    "068270.KS": "셀트리온",
    "105560.KS": "KB금융",
    "055550.KS": "신한지주",
    "012330.KS": "현대모비스",
    "012450.KS": "한화에어로스페이스",
    "329180.KS": "HD현대중공업",
    "034020.KS": "두산에너빌리티",
    "028260.KS": "삼성물산",
    "066570.KS": "LG전자",
}

# =========================================
# 사이드바
# =========================================
st.sidebar.header("⚙️ 분석 설정")

period_option = st.sidebar.selectbox("분석 기간", ["3mo", "6mo", "1y"], index=1)
top_n = st.sidebar.slider("추천 종목 수", 3, 20, 5)

st.sidebar.divider()
st.sidebar.markdown("""
**📌 추천 점수 산정 기준**
- 이동평균 골든크로스 여부
- RSI (과매도/과매수 상태)
- 최근 모멘텀(가격 상승률)
- 거래량 증가 추세

각 항목을 0~25점씩 합산해 100점 만점으로 점수화합니다.
""")

# =========================================
# 데이터 불러오기 & 지표 계산 함수
# =========================================
@st.cache_data(ttl=600)
def load_stock(ticker, period):
    df = yf.Ticker(ticker).history(period=period)
    return df

def calc_indicators(df):
    df = df.copy()
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

def calc_score(df):
    """0~100점 추천 점수 계산"""
    if len(df) < 60:
        return None

    latest = df.iloc[-1]
    score = 0
    detail = {}

    # 1. 골든크로스 여부 (25점): MA5 > MA20 > MA60이면 만점
    ma_score = 0
    if latest["MA5"] > latest["MA20"]:
        ma_score += 12.5
    if latest["MA20"] > latest["MA60"]:
        ma_score += 12.5
    score += ma_score
    detail["이동평균 배열"] = round(ma_score, 1)

    # 2. RSI (25점): 30~55 구간(저평가에서 반등 초입)일 때 높은 점수
    rsi = latest["RSI"]
    if pd.isna(rsi):
        rsi_score = 0
    elif 30 <= rsi <= 55:
        rsi_score = 25
    elif 55 < rsi <= 65:
        rsi_score = 15
    elif rsi < 30:
        rsi_score = 18  # 과매도 반등 기대
    else:
        rsi_score = max(0, 25 - (rsi - 65) * 1.2)  # 과매수는 감점
    score += rsi_score
    detail["RSI 상태"] = round(rsi_score, 1)

    # 3. 최근 모멘텀 (25점): 최근 20일 수익률
    momentum = (df["Close"].iloc[-1] / df["Close"].iloc[-20] - 1) * 100 if len(df) >= 20 else 0
    momentum_score = np.clip(momentum * 2.5 + 12.5, 0, 25)
    score += momentum_score
    detail["최근 모멘텀"] = round(momentum_score, 1)

    # 4. 거래량 추세 (25점): 최근 5일 평균 거래량 vs 이전 20일 평균
    recent_vol = df["Volume"].tail(5).mean()
    past_vol = df["Volume"].tail(25).head(20).mean()
    vol_ratio = recent_vol / past_vol if past_vol > 0 else 1
    vol_score = np.clip((vol_ratio - 1) * 50 + 12.5, 0, 25)
    score += vol_score
    detail["거래량 추세"] = round(vol_score, 1)

    return {
        "score": round(score, 1),
        "detail": detail,
        "momentum_pct": round(momentum, 2),
        "rsi": round(rsi, 1) if not pd.isna(rsi) else None,
        "price": round(latest["Close"], 0),
    }

# =========================================
# 전체 종목 분석 실행
# =========================================
st.header("🏆 오늘의 추천 순위")

with st.spinner("인기 종목 20개를 분석하는 중입니다... (최초 1회, 이후 캐시됨)"):
    results = []
    for ticker, name in KOREAN_STOCKS.items():
        try:
            df = load_stock(ticker, period_option)
            if df.empty:
                continue
            df = calc_indicators(df)
            result = calc_score(df)
            if result:
                results.append({
                    "티커": ticker,
                    "종목명": name,
                    "현재가": result["price"],
                    "추천점수": result["score"],
                    "20일 수익률(%)": result["momentum_pct"],
                    "RSI": result["rsi"],
                    "상세점수": result["detail"],
                })
        except Exception:
            continue

if not results:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
else:
    result_df = pd.DataFrame(results).sort_values("추천점수", ascending=False).reset_index(drop=True)
    result_df.index += 1

    def get_signal(score):
        if score >= 70:
            return "🟢 매수 관심"
        elif score >= 50:
            return "🟡 관망"
        else:
            return "🔴 신중"

    result_df["신호"] = result_df["추천점수"].apply(get_signal)

    top_df = result_df.head(top_n)

    display_df = top_df[["종목명", "티커", "현재가", "추천점수", "신호", "20일 수익률(%)", "RSI"]]
    st.dataframe(
        display_df.style.background_gradient(subset=["추천점수"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True,
        height=(len(display_df) + 1) * 35 + 5
    )

    # 점수 막대 그래프
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=top_df["종목명"], y=top_df["추천점수"],
        marker_color=top_df["추천점수"],
        marker_colorscale="RdYlGn",
        text=top_df["추천점수"],
        textposition="outside"
    ))
    fig_bar.update_layout(
        title=f"추천 점수 TOP {top_n}",
        yaxis_title="점수 (100점 만점)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# =========================================
# 개별 종목 상세 분석
# =========================================
st.header("🔍 종목별 상세 차트")

selected_name = st.selectbox("종목 선택", list(KOREAN_STOCKS.values()))
selected_ticker = [k for k, v in KOREAN_STOCKS.items() if v == selected_name][0]

df_detail = load_stock(selected_ticker, period_option)

if not df_detail.empty:
    df_detail = calc_indicators(df_detail)
    score_result = calc_score(df_detail)

    if score_result:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{score_result['price']:,.0f} 원")
        c2.metric("추천 점수", f"{score_result['score']} / 100")
        c3.metric("20일 수익률", f"{score_result['momentum_pct']:+.2f}%")
        c4.metric("RSI", f"{score_result['rsi']}")

        with st.expander("📊 점수 세부 내역 보기"):
            for k, v in score_result["detail"].items():
                st.write(f"- **{k}**: {v} / 25점")

    # 캔들스틱 + 이동평균 + 거래량 + RSI 차트
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.55, 0.2, 0.25]
    )

    fig.add_trace(go.Candlestick(
        x=df_detail.index, open=df_detail["Open"], high=df_detail["High"],
        low=df_detail["Low"], close=df_detail["Close"], name="가격"
    ), row=1, col=1)

    for ma, color in [("MA5", "orange"), ("MA20", "purple"), ("MA60", "green")]:
        fig.add_trace(go.Scatter(
            x=df_detail.index, y=df_detail[ma], name=ma,
            line=dict(width=1.5, color=color)
        ), row=1, col=1)

    colors_vol = ["red" if c < o else "green" for c, o in zip(df_detail["Close"], df_detail["Open"])]
    fig.add_trace(go.Bar(
        x=df_detail.index, y=df_detail["Volume"], name="거래량", marker_color=colors_vol
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df_detail.index, y=df_detail["RSI"], name="RSI", line=dict(color="blue")
    ), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        title=f"{selected_name} ({selected_ticker}) 상세 차트",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 원본 데이터 보기"):
        st.dataframe(df_detail.tail(50).sort_index(ascending=False), use_container_width=True)
        csv = df_detail.to_csv().encode("utf-8-sig")
        st.download_button("📥 CSV 다운로드", csv, f"{selected_ticker}_data.csv", "text/csv")

st.divider()

# =========================================
# 📚 주식 용어 사전
# =========================================
st.header("📚 주식 용어 쉽게 알아보기")

terms = {
    "추천 점수란?": "이 앱이 자체적으로 계산한 기술적 지표 기반 점수예요(100점 만점). 이동평균 배열, RSI, 최근 상승률(모멘텀), 거래량 증가 추세 4가지를 "
                "각 25점씩 합산했어요. **투자 추천이 아니라 '현재 기술적으로 어떤 흐름인지'를 숫자로 보여주는 참고 지표**라고 이해해주세요.",
    "골든크로스 / 데드크로스": "단기 이동평균선(예: MA5)이 장기 이동평균선(예: MA20)을 아래에서 위로 뚫고 올라가는 것을 '골든크로스'라고 하며 "
                          "보통 상승 전환 신호로 해석돼요. 반대로 위에서 아래로 내려가면 '데드크로스'라고 하며 하락 전환 신호로 해석돼요.",
    "RSI(상대강도지수)": "최근 가격 움직임을 0~100 사이 숫자로 나타낸 지표예요. 70 이상이면 '과매수'(너무 많이 올라서 조정 가능성), "
                     "30 이하면 '과매도'(너무 많이 떨어져서 반등 가능성)로 해석하는 게 일반적이에요. 다만 강한 상승장에서는 RSI가 70을 넘어도 "
                     "계속 오르는 경우가 많으니 절대적인 매매 신호로 쓰기보다는 참고용으로만 활용하세요.",
    "모멘텀(Momentum)": "최근 일정 기간(이 앱에서는 20거래일) 동안 주가가 얼마나 올랐는지를 나타내는 지표예요. 모멘텀이 강할수록 최근 추세가 "
                     "긍정적이라는 뜻이지만, 이미 많이 오른 종목일수록 단기 조정 위험도 커질 수 있어요.",
    "거래량(Volume)": "그 기간 동안 사고팔린 주식 수량이에요. 주가가 오르면서 거래량도 함께 늘어나면 '진짜 매수세가 들어온다'는 신뢰도 높은 신호로 "
                    "해석되는 경우가 많아요.",
    "이동평균선(MA, Moving Average)": "최근 N일간의 종가를 평균 낸 값을 선으로 이은 거예요. MA5(5일), MA20(20일), MA60(60일)처럼 기간이 짧을수록 "
                                  "단기 흐름에 민감하고, 길수록 장기 추세를 보여줘요.",
    "캔들스틱(Candlestick)": "하루 동안의 시가·고가·저가·종가를 하나의 막대로 표현한 차트예요. 빨간색(음봉)은 종가가 시가보다 낮을 때, "
                          "초록색(양봉)은 종가가 시가보다 높을 때를 나타내요. (국내 관행상 상승은 빨강, 하락은 파랑으로 표시하는 경우도 있으니 앱마다 색상 기준을 확인하세요)",
    "코스피(KOSPI) / 코스닥(KOSDAQ)": "코스피는 삼성전자, 현대차 같은 대형 우량주 위주의 한국 대표 증시이고, 코스닥은 상대적으로 중소형·기술주 중심의 시장이에요. "
                                  "야후 파이낸스 티커 기준으로 코스피는 종목코드 뒤에 '.KS', 코스닥은 '.KQ'를 붙여 조회해요.",
    "시가총액(Market Cap)": "현재 주가 × 발행주식수로 계산되는 기업의 전체 시장 가치예요. 기업 규모를 비교할 때 가장 흔히 사용돼요.",
}

for term, desc in terms.items():
    with st.expander(f"🔹 {term}"):
        st.write(desc)

st.divider()
st.caption("💡 본 앱의 추천 점수는 과거 가격·거래량 데이터를 기반으로 한 기술적 분석 결과이며, 미래 수익을 보장하지 않습니다. 투자 전 반드시 본인의 판단과 추가 조사를 거치시기 바랍니다.")
