"""
import streamlit as st
st.title("나의 첫 웹앱")
st.write("환영합니다.🤩")
"""

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
        background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 40%, #7c3aed 70%, #db2777 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .big-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fde68a, #fca5a5, #a78bfa, #6ee7b7);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
        margin-bottom: 0;
    }
    @keyframes shine {
        to { background-position: 300% center; }
    }
    .subtitle {
        text-align: center;
        color: #e9d5ff;
        font-size: 1.05rem;
        margin-top: 0.2rem;
        margin-bottom: 1.6rem;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 2px solid rgba(255,255,255,0.25);
        background: rgba(255,255,255,0.08);
        color: #fff;
        font-weight: 700;
        padding: 0.6rem 0.2rem;
        transition: all 0.25s ease;
        backdrop-filter: blur(6px);
    }
    div.stButton > button:hover {
        transform: translateY(-4px) scale(1.04);
        border-color: #fde68a;
        background: rgba(255,255,255,0.2);
        box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    }
    .result-card {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 22px;
        padding: 1.6rem;
        text-align: center;
        backdrop-filter: blur(10px);
        animation: popIn 0.5s ease;
        margin-top: 1rem;
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
    }
    .poke-desc {
        color: #fde68a;
        font-size: 1.1rem;
        margin-bottom: 0.6rem;
    }
    .job-card {
        background: rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 1rem 0.5rem;
        text-align: center;
        color: #fff;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: floatUp 0.6s ease;
    }
    .job-card:hover {
        transform: translateY(-6px) scale(1.05);
        box-shadow: 0 10px 24px rgba(0,0,0,0.4);
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
