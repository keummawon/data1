import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ----------------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------------
st.set_page_config(
    page_title="서울시민 고민·스트레스 분석 대시보드",
    page_icon="😥",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"

WORRY_COLS = [
    "경제 관련 문제", "건강", "자녀양육", "노후생활", "가족간 문제", "공부",
    "진학 취업 은퇴 등 진로선택", "본인 및 가족의 결혼", "자기개발", "고민없음",
    "이성 및 우정 문제", "신체 외모", "인터넷 커뮤니티", "학교(원) 폭력", "기타",
]

PALETTE = [
    "#FF6B6B", "#4ECDC4", "#FFD93D", "#6C5CE7", "#95E1D3", "#F38181", "#3D5A80",
    "#FF8C42", "#A8DADC", "#B0B0B0", "#F72585", "#7209B7", "#4361EE", "#2A9D8F", "#E76F51",
]
COLOR_MAP = dict(zip(WORRY_COLS, PALETTE))

AGE_ORDER = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
EDU_ORDER = ["중졸 이하", "고졸 이하", "대졸 이하", "대학원 이상"]
INCOME_ORDER = ["100 만원 미만", "100-200만 미만", "200-300만 미만", "300-400만 미만", "400-500만 미만", "500만 이상"]
GENDER_ORDER = ["남자", "여자"]
REGION_BIG_ORDER = ["도심권", "동북권", "서북권", "서남권", "동남권"]

CAT_ORDER = {
    "성별": GENDER_ORDER,
    "연령별": AGE_ORDER,
    "학력별": EDU_ORDER,
    "소득별": INCOME_ORDER,
    "지역대분류": REGION_BIG_ORDER,
}
CAT_EMOJI = {"성별": "🚻", "연령별": "🎂", "학력별": "🎓", "소득별": "💰", "지역대분류": "🗺️"}

# ----------------------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------------------
@st.cache_data
def load_default_data():
    return pd.read_csv(DATA_DIR / "personal_worries_seoul_long.csv")


@st.cache_data
def parse_uploaded(file_bytes: bytes):
    import io
    raw = pd.read_csv(io.BytesIO(file_bytes))
    # 원본(wide, KOSIS 형태) 업로드인 경우
    if str(raw.iloc[0, 0]).strip() == "구분별(1)":
        cols = list(raw.iloc[0])
        raw = raw.iloc[1:].copy()
        raw.columns = cols
        raw = raw.reset_index(drop=True)
        id_cols = ["구분별(1)", "구분별(2)"]
        value_cols = [c for c in raw.columns if c not in id_cols + ["계"]]
        for c in value_cols + ["계"]:
            raw[c] = pd.to_numeric(raw[c].astype(str).replace("-", "0"), errors="coerce").fillna(0)
        long_df = raw.melt(id_vars=id_cols, value_vars=value_cols, var_name="고민유형", value_name="비율")
        long_df = long_df.rename(columns={"구분별(1)": "구분", "구분별(2)": "그룹"})
        return long_df
    # 이미 정리된(long) 형태로 올린 경우: 구분/그룹/고민유형/비율 컬럼 필요
    expected = {"구분", "그룹", "고민유형", "비율"}
    if expected.issubset(set(raw.columns)):
        return raw
    st.sidebar.error("업로드한 CSV 형식을 인식할 수 없습니다. 기본 데이터를 사용합니다.")
    return None


st.sidebar.title("⚙️ 데이터")
st.sidebar.caption(
    "기본 데이터는 **서울서베이 '개인적인 고민거리'** 통계입니다. "
    "동일 형식(원본 KOSIS wide, 또는 구분/그룹/고민유형/비율 long) CSV를 올리면 그 데이터로 교체됩니다."
)
uploaded = st.sidebar.file_uploader("CSV 업로드 (선택)", type=["csv"])

df = load_default_data()
if uploaded is not None:
    parsed = parse_uploaded(uploaded.getvalue())
    if parsed is not None:
        df = parsed
        st.sidebar.success("업로드한 데이터로 갱신했습니다 ✅")

df["비율"] = pd.to_numeric(df["비율"], errors="coerce").fillna(0)

# ----------------------------------------------------------------------------------
# 헤더
# ----------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {font-size: 2.1rem; font-weight: 800; margin-bottom: 0;}
    .sub-title {color: #6b7280; font-size: 1.02rem; margin-top: 0.2rem;}
    div[data-testid="stMetric"] {background: #fafafa; border: 1px solid #eee; border-radius: 12px; padding: 10px 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<p class="main-title">😥 서울시민 고민·스트레스 분석 대시보드</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">성별 · 연령 · 학력 · 소득 · 지역에 따라 사람들이 가장 크게 짊어지는 고민(스트레스)이 무엇인지 한눈에 살펴보고, '
    '세대 간 차이가 만들어낼 수 있는 갈등 지점을 데이터로 예측합니다.</p>',
    unsafe_allow_html=True,
)
st.divider()

# ----------------------------------------------------------------------------------
# 상단 KPI: 서울시 전체 TOP3 고민
# ----------------------------------------------------------------------------------
seoul_total = (
    df[(df["구분"] == "서울시") & (df["고민유형"] != "계")]
    .sort_values("비율", ascending=False)
    .head(3)
    .reset_index(drop=True)
)
if not seoul_total.empty:
    cols = st.columns(len(seoul_total))
    medals = ["🥇", "🥈", "🥉"]
    for i, (col, row) in enumerate(zip(cols, seoul_total.itertuples())):
        col.metric(f"{medals[i]} 서울시민 전체 고민 {i+1}위", row.고민유형, f"{row.비율:.1f}%")

st.write("")

# ====================================================================================
# 탭 구성
# ====================================================================================
tab_overview, tab_gender, tab_age, tab_edu, tab_income, tab_region, tab_deep = st.tabs(
    ["🏠 종합 개요", "🚻 성별", "🎂 연령별", "🎓 학력별", "💰 소득별", "🗺️ 지역별", "🔍 연령 심층분석 · 세대갈등 예측"]
)

# ------------------------------------------------------------------------------------
# 0) 종합 개요 - 한눈에 보는 히트맵
# ------------------------------------------------------------------------------------
with tab_overview:
    st.subheader("모든 인구통계 축을 한 번에 — 고민 유형 히트맵")
    st.caption("성별·연령·학력·소득·지역 그룹을 세로축에, 고민 유형을 가로축에 두어 어디서 어떤 고민이 두드러지는지 색으로 보여줍니다.")

    main_cats = ["성별", "연령별", "학력별", "소득별", "지역대분류"]
    sub = df[df["구분"].isin(main_cats) & (df["고민유형"] != "계")].copy()
    sub["그룹라벨"] = sub["구분"] + " · " + sub["그룹"]

    order_labels = []
    for cat in main_cats:
        groups = CAT_ORDER.get(cat, sorted(sub[sub["구분"] == cat]["그룹"].unique()))
        for g in groups:
            label = f"{cat} · {g}"
            if label in sub["그룹라벨"].values:
                order_labels.append(label)

    pivot = sub.pivot_table(index="그룹라벨", columns="고민유형", values="비율", aggfunc="mean")
    pivot = pivot.reindex(order_labels)
    existing_worry_cols = [c for c in WORRY_COLS if c in pivot.columns]
    pivot = pivot[existing_worry_cols]

    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(color="비율(%)", x="고민 유형", y=""),
    )
    fig.update_layout(height=760, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10))
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 그룹별 1위 고민 요약표 보기"):
        idx = sub.groupby("그룹라벨")["비율"].idxmax()
        top1 = sub.loc[idx, ["구분", "그룹", "고민유형", "비율"]].reset_index(drop=True)
        top1["구분"] = pd.Categorical(top1["구분"], categories=main_cats, ordered=True)
        top1 = top1.sort_values(["구분", "그룹"])
        st.dataframe(top1.rename(columns={"비율": "비율(%)"}), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------------
# 공통 렌더 함수 (성별 / 연령별 / 학력별 / 소득별)
# ------------------------------------------------------------------------------------
def render_category_tab(cat_name: str, order: list):
    emoji = CAT_EMOJI.get(cat_name, "")
    st.subheader(f"{emoji} {cat_name}로 본 고민 구성")

    sub = df[(df["구분"] == cat_name) & (df["고민유형"] != "계")].copy()
    present_order = [g for g in order if g in sub["그룹"].unique()]
    sub["그룹"] = pd.Categorical(sub["그룹"], categories=present_order, ordered=True)
    sub = sub.sort_values(["그룹"])

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("**그룹별 고민 구성비 (100% 누적)**")
        fig = px.bar(
            sub, x="비율", y="그룹", color="고민유형", orientation="h",
            color_discrete_map=COLOR_MAP,
            category_orders={"그룹": present_order, "고민유형": WORRY_COLS},
        )
        fig.update_layout(
            barmode="stack", height=440, template="plotly_white",
            legend_title="고민 유형", xaxis_title="비율(%)", yaxis_title=None,
            legend=dict(orientation="v"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**그룹별 고민 TOP 3**")
        rows = []
        for g in present_order:
            gdf = sub[sub["그룹"] == g].nlargest(3, "비율")
            for rank, r in enumerate(gdf.itertuples(), 1):
                rows.append({"그룹": g, "순위": rank, "고민유형": r.고민유형, "비율(%)": r.비율})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=440)

    st.markdown("**그룹별 고민 프로필 비교 (레이더 차트)**")
    top_types = sub.groupby("고민유형")["비율"].mean().nlargest(7).index.tolist()
    fig2 = go.Figure()
    for g in present_order:
        gdf = sub[(sub["그룹"] == g) & (sub["고민유형"].isin(top_types))].set_index("고민유형").reindex(top_types)
        fig2.add_trace(go.Scatterpolar(r=gdf["비율"].fillna(0), theta=top_types, fill="toself", name=str(g)))
    fig2.update_layout(
        template="plotly_white", height=460,
        polar=dict(radialaxis=dict(visible=True, ticksuffix="%")),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    st.plotly_chart(fig2, use_container_width=True)


with tab_gender:
    render_category_tab("성별", GENDER_ORDER)

with tab_age:
    render_category_tab("연령별", AGE_ORDER)

with tab_edu:
    render_category_tab("학력별", EDU_ORDER)

with tab_income:
    render_category_tab("소득별", INCOME_ORDER)

# ------------------------------------------------------------------------------------
# 지역별 (대분류 / 소분류 토글)
# ------------------------------------------------------------------------------------
with tab_region:
    st.subheader("🗺️ 지역별 고민 구성")
    region_level = st.radio("지역 단위 선택", ["대분류 (권역)", "소분류 (자치구)"], horizontal=True)

    if region_level.startswith("대분류"):
        render_category_tab("지역대분류", REGION_BIG_ORDER)
    else:
        sub = df[(df["구분"] == "지역소분류") & (df["고민유형"] != "계")].copy()
        gu_order = sorted(sub["그룹"].unique())
        worry_pick = st.selectbox("자치구별로 비교할 고민 유형 선택", WORRY_COLS, index=0)
        pick_df = sub[sub["고민유형"] == worry_pick].sort_values("비율", ascending=True)
        fig = px.bar(
            pick_df, x="비율", y="그룹", orientation="h",
            color="비율", color_continuous_scale="YlOrRd",
            labels={"비율": "비율(%)", "그룹": "자치구"},
        )
        fig.update_layout(height=680, template="plotly_white", coloraxis_showscale=False,
                           title=f"자치구별 '{worry_pick}' 응답 비율")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**자치구 × 고민유형 히트맵**")
        pivot = sub.pivot_table(index="그룹", columns="고민유형", values="비율", aggfunc="mean").reindex(gu_order)
        existing_cols = [c for c in WORRY_COLS if c in pivot.columns]
        fig2 = px.imshow(pivot[existing_cols], text_auto=".1f", color_continuous_scale="YlOrRd", aspect="auto")
        fig2.update_layout(height=700, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------------------------------
# 연령 심층분석 & 세대갈등 예측
# ------------------------------------------------------------------------------------
with tab_deep:
    st.subheader("🔍 연령대별 고민 심층분석")

    age_sub = df[(df["구분"] == "연령별") & (df["고민유형"] != "계")].copy()
    age_pivot = age_sub.pivot_table(index="그룹", columns="고민유형", values="비율", aggfunc="mean").reindex(AGE_ORDER)
    existing_worry = [c for c in WORRY_COLS if c in age_pivot.columns]
    age_pivot = age_pivot[existing_worry]

    default_types = [w for w in ["경제 관련 문제", "건강", "자녀양육", "노후생활", "진학 취업 은퇴 등 진로선택", "공부"] if w in existing_worry]
    picked = st.multiselect("추이를 살펴볼 고민 유형", existing_worry, default=default_types)

    if picked:
        fig = go.Figure()
        for w in picked:
            fig.add_trace(go.Scatter(
                x=AGE_ORDER, y=age_pivot[w], mode="lines+markers", name=w,
                line=dict(width=3, color=COLOR_MAP.get(w)), marker=dict(size=8),
            ))
        fig.update_layout(
            template="plotly_white", height=460, hovermode="x unified",
            xaxis_title="연령대", yaxis_title="비율(%)", legend_title="고민 유형",
            title="연령대별 고민 유형 추이",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 세대 간 격차(Gap) — 두 연령대를 골라 차이가 큰 고민을 확인하세요")
    gc1, gc2 = st.columns(2)
    with gc1:
        young = st.selectbox("연령대 A", AGE_ORDER, index=1)  # 기본 20대
    with gc2:
        old = st.selectbox("연령대 B", AGE_ORDER, index=len(AGE_ORDER) - 1)  # 기본 60대 이상

    gap = (age_pivot.loc[old] - age_pivot.loc[young]).sort_values()
    gap_df = gap.reset_index()
    gap_df.columns = ["고민유형", "격차"]
    gap_df["방향"] = np.where(gap_df["격차"] >= 0, f"{old}가 더 큼", f"{young}가 더 큼")
    fig_gap = px.bar(
        gap_df, x="격차", y="고민유형", orientation="h", color="방향",
        color_discrete_map={f"{old}가 더 큼": "#3D5A80", f"{young}가 더 큼": "#FF6B6B"},
    )
    fig_gap.update_layout(template="plotly_white", height=480, xaxis_title=f"비율차(%p) = {old} − {young}",
                           yaxis_title=None, title=f"{young} vs {old} 고민 격차")
    st.plotly_chart(fig_gap, use_container_width=True)

    st.divider()

    # ---------------- 자동 분석: 공통점 / 차이점 ----------------
    stats = pd.DataFrame({
        "평균": age_pivot.mean(),
        "표준편차": age_pivot.std(),
        "최솟값": age_pivot.min(),
        "최댓값": age_pivot.max(),
    })
    stats["변동폭"] = stats["최댓값"] - stats["최솟값"]
    stats["변동계수(CV)"] = (stats["표준편차"] / stats["평균"].replace(0, np.nan) * 100).round(1)

    commonality = stats[stats["평균"] >= 3].sort_values("변동계수(CV)").head(5)
    differences = stats.sort_values("변동폭", ascending=False).head(5)

    top_by_age = {g: age_pivot.loc[g].idxmax() for g in AGE_ORDER}
    val_by_age = {g: age_pivot.loc[g].max() for g in AGE_ORDER}

    eco = age_pivot["경제 관련 문제"] if "경제 관련 문제" in age_pivot else None
    health = age_pivot["건강"] if "건강" in age_pivot else None
    family = age_pivot["가족간 문제"] if "가족간 문제" in age_pivot else None
    study = age_pivot["공부"] if "공부" in age_pivot else None
    job = age_pivot["진학 취업 은퇴 등 진로선택"] if "진학 취업 은퇴 등 진로선택" in age_pivot else None
    childcare = age_pivot["자녀양육"] if "자녀양육" in age_pivot else None
    retire = age_pivot["노후생활"] if "노후생활" in age_pivot else None

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### ✅ 세대 공통 스트레스 요인")
        st.caption("전 연령대에서 고르게 비중이 높거나 변동성이 낮은 고민 유형")
        st.dataframe(commonality[["평균", "변동계수(CV)"]].round(1), use_container_width=True)
    with c2:
        st.markdown("##### ⚡ 세대별 차이가 가장 큰 요인")
        st.caption("연령대 간 응답 비율의 격차(최댓값-최솟값)가 큰 고민 유형")
        st.dataframe(differences[["최솟값", "최댓값", "변동폭"]].round(1), use_container_width=True)

    st.markdown("### 📝 분석 요약: 공통점과 차이점")

    common_text = "".join([f"- **{name}**: 전 연령대 평균 {row['평균']:.1f}%, 변동계수 {row['변동계수(CV)']:.0f}%로 특정 세대에 치우치지 않고 널리 나타납니다.\n"
                            for name, row in commonality.head(3).iterrows()])
    diff_text = "".join([f"- **{name}**: 최저 {row['최솟값']:.1f}% ↔ 최고 {row['최댓값']:.1f}% (격차 {row['변동폭']:.1f}%p)로 연령대별 편차가 매우 큽니다.\n"
                          for name, row in differences.head(4).iterrows()])

    st.markdown(f"""
**🟢 공통점 — 세대를 관통하는 고민**

{common_text if common_text else "- (데이터 부족)"}
특히 '경제 관련 문제'와 '가족간 문제'는 10대를 제외한 거의 모든 연령대에서 상위권에 들며,
세대와 무관하게 **경제적 안정과 가족 관계**가 한국 사회 전반의 근원적인 스트레스원임을 보여줍니다.

**🔴 차이점 — 연령대마다 확연히 다른 고민**

{diff_text if diff_text else "- (데이터 부족)"}

연령대별 1위 고민을 정리하면 뚜렷한 생애주기 패턴이 드러납니다:
""")

    life_stage_rows = []
    for g in AGE_ORDER:
        life_stage_rows.append({"연령대": g, "1위 고민": top_by_age[g], "비율(%)": round(val_by_age[g], 1)})
    st.dataframe(pd.DataFrame(life_stage_rows), use_container_width=True, hide_index=True)

    st.markdown("""
- **10대**: 학업 스트레스가 압도적 (진학·입시 중심)
- **20대**: 진로·취업 스트레스가 최상위 — 사회 진입 관문에서의 불안
- **30대**: 자녀양육·결혼이 급부상하며 경제 문제와 결합 — 가정 형성기
- **40대**: 경제 문제가 정점을 찍고, 자녀양육 부담과 노후 불안이 동시에 시작 — 이중·삼중 부담의 "낀 세대"
- **50대**: 건강과 노후생활 불안이 급격히 증가하며 경제 문제와 맞물림 — 은퇴 전환기
- **60대 이상**: 건강이 압도적 1위, 노후생활 불안이 그 뒤를 잇는 — 생존·안정 중심 단계
    """)

    st.divider()
    st.markdown("### ⚔️ 데이터로 예측하는 세대갈등 시나리오")

    st.markdown(f"""
연령대별 고민의 구조적 차이는 실제 정책·자원 배분 국면에서 세대 간 이해관계 충돌로 이어질 가능성이 있습니다.
아래는 위 데이터에서 관찰되는 패턴을 근거로 한 예측입니다.

**1. 복지 재원 배분을 둘러싼 갈등 — "청년 취업 지원 vs 노인 연금·의료"**
60대 이상은 건강({age_pivot.loc['60대 이상','건강']:.1f}%)과 노후생활({age_pivot.loc['60대 이상','노후생활']:.1f}%)이 고민의 대부분을 차지하는 반면,
20대는 진로·취업 문제({age_pivot.loc['20대','진학 취업 은퇴 등 진로선택']:.1f}%)와 경제 문제({age_pivot.loc['20대','경제 관련 문제']:.1f}%)가 최우선 과제입니다.
한정된 복지·재정 자원을 두고 "청년 일자리 예산"과 "노인 연금·의료 예산"이 경쟁 관계에 놓이면서,
세대별로 "내 세대의 문제가 더 시급하다"는 인식 차이가 갈등의 씨앗이 될 수 있습니다.

**2. 노동시장 경쟁 — 정년연장 vs 청년 신규채용**
경제 관련 문제는 30~50대에서 특히 두드러지는데(30대 {age_pivot.loc['30대','경제 관련 문제']:.1f}%, 40대 {age_pivot.loc['40대','경제 관련 문제']:.1f}%, 50대 {age_pivot.loc['50대','경제 관련 문제']:.1f}%),
정년연장·고령자 고용 연장 정책이 신규 채용 축소로 이어진다는 인식이 확산되면
청년층의 취업난 스트레스와 중장년층의 고용안정 요구가 정면으로 부딪힐 수 있습니다.

**3. '낀 세대'(3040)의 이중부담과 형평성 문제 제기**
30~40대는 자녀양육 부담(30대 {age_pivot.loc['30대','자녀양육']:.1f}%, 40대 {age_pivot.loc['40대','자녀양육']:.1f}%)과 경제 문제를 동시에 짊어지면서도
노후 불안까지 서서히 시작되는({age_pivot.loc['40대','노후생활']:.1f}%) 구간입니다.
자녀 교육비와 부모 부양, 본인 노후 준비를 동시에 감당해야 하는 이 세대는
청년 지원과 노인 복지 확대 요구 양쪽에 대해 "정작 우리는 누가 챙겨주나"라는 피로감·형평성 문제를 제기할 가능성이 큽니다.

**4. 결혼·출산을 둘러싼 가치관 격차**
20대의 취업·경제 불안({age_pivot.loc['20대','경제 관련 문제']:.1f}%)은 만혼·비혼으로 이어질 수 있는 반면,
기성세대는 가족 형성을 당연한 생애과정으로 여기는 경향이 있어, "왜 결혼·출산을 미루는가"에 대한 세대 간 인식 차이가
가족 정책과 저출산 대응 방향을 둘러싼 논쟁으로 확대될 수 있습니다.

**5. 소통·공감의 구조적 어려움**
연령대별 1순위 고민 자체가 서로 다르기 때문에(10대는 학업, 20대는 취업, 30~40대는 경제·양육, 50~60대는 건강·노후),
각 세대는 서로 다른 정책 우선순위를 요구하게 됩니다. 이는 자연스러운 생애주기의 결과이지만,
공론장에서 "왜 저 세대는 저것만 요구하나"라는 오해로 이어지면 세대 간 갈등을 심화시킬 수 있습니다.

> 💡 **시사점**: 세대 갈등을 완화하려면 각 세대의 고민이 '이기심'이 아니라 '생애주기에 따른 합리적 반응'이라는 점을 서로 이해하는 것이 출발점입니다.
> 정책적으로는 청년 고용과 고령자 고용을 제로섬으로 만들지 않는 노동시장 설계, 3040 세대의 이중부담을 완화하는 지원,
> 세대 간 자원배분에 대한 투명한 사회적 합의 과정이 필요합니다.
    """)

    st.caption("※ 위 해석은 현재 로드된 데이터(기본값: 서울서베이 '개인적인 고민거리' 통계)를 기준으로 자동 생성되었으며, 참고용 인사이트입니다.")

st.divider()
st.caption("데이터 출처: 서울서베이 도시정책지표조사 – 개인적인 고민거리(업로드 데이터 기준) · 제작: Streamlit + Plotly")
