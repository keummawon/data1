"""
import streamlit as st
st.title("나의 첫 웹앱")
st.write("환영합니다.🤩")

import streamlit as st

# ----------------------------------------------------
# 기본 설정
# ----------------------------------------------------
st.set_page_config(
    page_title="MBTI 포켓몬 직업 추천소 🔮",
    page_icon="🧬",
    layout="centered",
)

# ----------------------------------------------------
# 데이터: MBTI별 포켓몬 & 추천 직업
# (포켓몬 이미지는 PokeAPI 공식 아트워크 CDN 사용)
# ----------------------------------------------------
def poke_img(pid: int) -> str:
    # jsDelivr 미러 CDN (raw.githubusercontent.com보다 접속이 안정적)
    return f"https://cdn.jsdelivr.net/gh/PokeAPI/sprites@master/sprites/pokemon/other/official-artwork/{pid}.png"


def poke_img_fallback(pid: int) -> str:
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"

MBTI_DATA = {
    "INTJ": {"name": "뮤투", "id": 150, "emoji": "🧠", "desc": "냉철한 전략가",
              "jobs": [("전략 컨설턴트", "🧩"), ("데이터 사이언티스트", "📊"), ("스타트업 창업가", "🚀")]},
    "INTP": {"name": "폴리곤", "id": 137, "emoji": "🔬", "desc": "논리적인 탐구자",
              "jobs": [("소프트웨어 엔지니어", "💻"), ("연구원·과학자", "🧪"), ("시스템 아키텍트", "🏗️")]},
    "ENTJ": {"name": "리자몽", "id": 6, "emoji": "🔥", "desc": "카리스마 넘치는 리더",
              "jobs": [("경영자·CEO", "👔"), ("프로젝트 매니저", "📈"), ("변호사", "⚖️")]},
    "ENTP": {"name": "뮤", "id": 151, "emoji": "✨", "desc": "재기발랄한 혁신가",
              "jobs": [("광고 기획자", "💡"), ("스타트업 창업가", "🚀"), ("발명가", "🛠️")]},
    "INFJ": {"name": "세레비", "id": 251, "emoji": "🌿", "desc": "신비로운 통찰가",
              "jobs": [("상담심리사", "🌱"), ("작가", "✍️"), ("사회운동가", "🕊️")]},
    "INFP": {"name": "라프라스", "id": 131, "emoji": "🌊", "desc": "따뜻한 몽상가",
              "jobs": [("소설가", "📖"), ("예술치료사", "🎨"), ("환경운동가", "🌍")]},
    "ENFJ": {"name": "루카리오", "id": 448, "emoji": "🌟", "desc": "카리스마 있는 멘토",
              "jobs": [("교사·강사", "👩‍🏫"), ("HR 매니저", "🤝"), ("코치·멘토", "🌟")]},
    "ENFP": {"name": "피카츄", "id": 25, "emoji": "⚡", "desc": "에너지 넘치는 인싸",
              "jobs": [("마케터", "🎉"), ("이벤트 기획자", "🎪"), ("크리에이터", "🎥")]},
    "ISTJ": {"name": "메탕그로스", "id": 376, "emoji": "⚙️", "desc": "철두철미 원칙주의자",
              "jobs": [("회계사", "📑"), ("공무원", "🏛️"), ("품질관리 엔지니어", "🔩")]},
    "ISTP": {"name": "로토무", "id": 479, "emoji": "🔧", "desc": "손재주 좋은 장인",
              "jobs": [("정비사·엔지니어", "🔧"), ("파일럿", "✈️"), ("응급구조사", "🚑")]},
    "ISFJ": {"name": "이브이", "id": 133, "emoji": "🤎", "desc": "다정한 수호자",
              "jobs": [("간호사", "👩‍⚕️"), ("사회복지사", "🤲"), ("초등교사", "🍎")]},
    "ISFP": {"name": "비비용", "id": 666, "emoji": "🦋", "desc": "감성 가득한 예술가",
              "jobs": [("플로리스트", "💐"), ("사진작가", "📸"), ("패션 디자이너", "👗")]},
    "ESTJ": {"name": "갸라도스", "id": 130, "emoji": "🌊", "desc": "강력한 지휘관",
              "jobs": [("경찰·군인", "🚓"), ("운영 관리자", "📋"), ("은행원", "🏦")]},
    "ESTP": {"name": "윈디", "id": 59, "emoji": "🔥", "desc": "대담한 모험가",
              "jobs": [("세일즈 매니저", "💼"), ("소방관", "🚒"), ("프로 운동선수", "🏅")]},
    "ESFJ": {"name": "픽시", "id": 36, "emoji": "💞", "desc": "사교적인 분위기 메이커",
              "jobs": [("이벤트 플래너", "🎊"), ("홍보(PR) 담당자", "📢"), ("웨딩플래너", "💒")]},
    "ESFP": {"name": "푸린", "id": 39, "emoji": "🎤", "desc": "무대를 사랑하는 엔터테이너",
              "jobs": [("배우", "🎭"), ("가수", "🎤"), ("방송인", "📺")]},
}

MBTI_GROUP_COLOR = {
    "NT": "#8b5cf6", "NF": "#22c55e", "SJ": "#3b82f6", "SP": "#f59e0b",
}

def group_of(mbti: str) -> str:
    if mbti[1] == "N" and mbti[2] == "T":
        return "NT"
    if mbti[1] == "N" and mbti[2] == "F":
        return "NF"
    if mbti[1] == "S" and mbti[3] == "J":
        return "SJ"
    return "SP"

# ----------------------------------------------------
# 커스텀 CSS (그라데이션 배경, 애니메이션, 카드 효과)
# ----------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(236, 72, 153, 0.35) 0%, transparent 40%),
            radial-gradient(circle at 85% 15%, rgba(56, 189, 248, 0.30) 0%, transparent 45%),
            radial-gradient(circle at 50% 90%, rgba(251, 191, 36, 0.22) 0%, transparent 45%),
            linear-gradient(160deg, #0b0f2b 0%, #1a1040 35%, #2b0f4a 65%, #170a2e 100%);
        background-size: 200% 200%, 200% 200%, 200% 200%, 400% 400%;
        animation: gradientShift 18s ease infinite;
    }
    @keyframes gradientShift {
        0% {background-position: 0% 50%, 100% 0%, 50% 100%, 0% 50%;}
        50% {background-position: 100% 50%, 0% 100%, 50% 0%, 100% 50%;}
        100% {background-position: 0% 50%, 100% 0%, 50% 100%, 0% 50%;}
    }
    .big-title {
        text-align: center;
        font-size: 2.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fb7185, #fbbf24, #38bdf8, #c084fc);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(251, 113, 133, 0.35);
        filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.25));
    }
    @keyframes shine {
        to { background-position: 300% center; }
    }
    .subtitle {
        text-align: center;
        color: #d8cdfa;
        font-size: 1.05rem;
        margin-top: 0.2rem;
        margin-bottom: 1.6rem;
        text-shadow: 0 0 12px rgba(192, 132, 252, 0.3);
    }
    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1.5px solid rgba(192, 132, 252, 0.35);
        background: linear-gradient(160deg, rgba(45, 27, 78, 0.75), rgba(20, 14, 45, 0.75));
        color: #f3e8ff;
        font-weight: 700;
        padding: 0.6rem 0.2rem;
        transition: all 0.25s ease;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    div.stButton > button:hover {
        transform: translateY(-4px) scale(1.04);
        border-color: #fbbf24;
        background: linear-gradient(160deg, rgba(236, 72, 153, 0.35), rgba(56, 189, 248, 0.25));
        box-shadow: 0 0 22px rgba(251, 191, 36, 0.45), 0 8px 20px rgba(0,0,0,0.45);
        color: #fff;
    }
    .result-card {
        background: linear-gradient(160deg, rgba(45, 27, 78, 0.55), rgba(15, 10, 35, 0.65));
        border: 1px solid rgba(192, 132, 252, 0.35);
        border-radius: 22px;
        padding: 1.6rem;
        text-align: center;
        backdrop-filter: blur(14px);
        animation: popIn 0.5s ease;
        margin-top: 1rem;
        box-shadow: 0 0 40px rgba(236, 72, 153, 0.15), 0 8px 32px rgba(0,0,0,0.4);
    }
    @keyframes popIn {
        0% { transform: scale(0.85); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    .poke-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        margin-top: 0.4rem;
        text-shadow: 0 0 18px rgba(56, 189, 248, 0.5);
    }
    .poke-desc {
        color: #fbbf24;
        font-size: 1.1rem;
        margin-bottom: 0.6rem;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.35);
    }
    .job-card {
        background: linear-gradient(160deg, rgba(56, 189, 248, 0.16), rgba(236, 72, 153, 0.14));
        border-radius: 16px;
        padding: 1rem 0.5rem;
        text-align: center;
        color: #fff;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.22);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: floatUp 0.6s ease;
    }
    .job-card:hover {
        transform: translateY(-6px) scale(1.05);
        border-color: #fbbf24;
        box-shadow: 0 0 24px rgba(251, 191, 36, 0.4), 0 10px 24px rgba(0,0,0,0.4);
    }
    @keyframes floatUp {
        0% { transform: translateY(15px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .job-emoji { font-size: 2rem; display:block; margin-bottom: 0.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# 헤더
# ----------------------------------------------------
st.markdown('<p class="big-title">🔮 MBTI 포켓몬 직업 추천소 🧬</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">✨ 당신의 MBTI를 고르면, 꼭 닮은 포켓몬과 찰떡궁합 직업 3가지를 알려드려요! ⚡</p>', unsafe_allow_html=True)

if "selected_mbti" not in st.session_state:
    st.session_state.selected_mbti = None

# ----------------------------------------------------
# MBTI 선택 버튼 (4x4 그리드)
# ----------------------------------------------------
mbti_list = list(MBTI_DATA.keys())
rows = [mbti_list[i:i + 4] for i in range(0, len(mbti_list), 4)]

for row in rows:
    cols = st.columns(4)
    for col, mbti in zip(cols, row):
        with col:
            emoji = MBTI_DATA[mbti]["emoji"]
            if st.button(f"{emoji} {mbti}", key=f"btn_{mbti}"):
                st.session_state.selected_mbti = mbti

# ----------------------------------------------------
# 결과 출력
# ----------------------------------------------------
if st.session_state.selected_mbti:
    mbti = st.session_state.selected_mbti
    data = MBTI_DATA[mbti]

    st.balloons()

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### {data['emoji']} {mbti} 유형의 포켓몬은...")

    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
    with img_col2:
        st.image(poke_img(data["id"]), width=280)
        st.caption(f"이미지가 안 보이면 [여기 클릭]({poke_img_fallback(data['id'])})해서 확인해 보세요 🔗")

    st.markdown(f'<p class="poke-name">🐾 {data["name"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="poke-desc">"{data["desc"]}"</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 💼 이 유형에게 찰떡인 추천 직업 3가지")
    job_cols = st.columns(3)
    for jcol, (job, jemoji) in zip(job_cols, data["jobs"]):
        with jcol:
            st.markdown(
                f"""
                <div class="job-card">
                    <span class="job-emoji">{jemoji}</span>
                    {job}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"<p style='text-align:center; color:#e9d5ff; margin-top:1.4rem;'>"
        f"🎉 {mbti}는 <b>{data['name']}</b>처럼 매력적인 존재군요! 자신에게 딱 맞는 커리어를 찾아보세요 🚀</p>",
        unsafe_allow_html=True,
    )
else:
    st.info("👆 위에서 자신의 MBTI 버튼을 눌러보세요!")

st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.2);'>"
    "<p style='text-align:center; color:#c4b5fd; font-size:0.85rem;'>"
    "Made with 💜 Streamlit | 포켓몬 이미지 출처: PokeAPI</p>",
    unsafe_allow_html=True,
)
"""

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
