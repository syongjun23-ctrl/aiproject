
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path

# =====================================================
# 기본 설정
# =====================================================

st.set_page_config(
    page_title="서울 인구 분석 대시보드",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "202012_202512_연령별인구현황_연간.csv"

PINK = "#FF3F9B"
GREEN = "#35C995"
DARK = "#33263D"
LIGHT_PINK = "#FFF0F7"

# =====================================================
# 디자인 CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 5% 5%, #ffe0f1 0, transparent 25%),
        radial-gradient(circle at 95% 10%, #dffbf1 0, transparent 23%),
        linear-gradient(135deg, #fff7fb, #fffaff 55%, #f0fff9);
    color: #33263D;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    color: #39283F !important;
    font-weight: 900 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFE1F1, #FFF2F9 60%, #E7FFF5);
    border-right: 1px solid #FFD0E8;
}

[data-testid="stSidebar"] * {
    color: #432C43;
}

.stSelectbox label {
    font-weight: 800 !important;
    color: #49334B !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 15px;
    border: 1px solid #FFC4E0;
    background: white;
}

.stButton button {
    border: none;
    border-radius: 15px;
    background: linear-gradient(100deg, #FF3195, #FF79B9);
    color: white;
    font-weight: 900;
    box-shadow: 0 5px 15px #FF9BCB66;
    transition: 0.2s;
}

.stButton button:hover {
    transform: translateY(-2px);
    color: white;
    box-shadow: 0 8px 20px #FF80BB88;
}

.hero {
    padding: 35px 38px;
    border-radius: 27px;
    background: linear-gradient(110deg, #FF75B8, #FF3F9B 55%, #C98BFF);
    color: white;
    box-shadow: 0 10px 30px #FF83BD55;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.hero h1 {
    color: white !important;
    font-size: 36px !important;
    margin-bottom: 8px;
}

.hero p {
    color: #FFF5FA;
    font-size: 15px;
    margin-bottom: 0;
}

.hero-deco {
    position: absolute;
    right: 35px;
    top: 15px;
    font-size: 75px;
    opacity: 0.35;
}

.section-title {
    font-size: 23px;
    font-weight: 900;
    margin: 20px 0 15px 0;
    color: #49334B;
}

.info-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid #FFD6E9;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 6px 20px #ECA9CC22;
    margin-bottom: 15px;
}

.metric-label {
    color: #98738C;
    font-size: 14px;
    font-weight: 700;
}

.metric-value {
    color: #FF3F9B;
    font-size: 30px;
    font-weight: 900;
    margin-top: 5px;
}

.winner-card {
    background: linear-gradient(135deg, #FFF0F8, #FFFFFF);
    border: 1px solid #FFC3E0;
    border-radius: 22px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 6px 20px #F5B6D522;
}

.winner-name {
    color: #FF3195;
    font-size: 32px;
    font-weight: 900;
}

.winner-sub {
    color: #98738C;
    font-size: 14px;
    font-weight: 700;
}

.footer {
    text-align: center;
    color: #B18CA5;
    font-size: 12px;
    margin-top: 40px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CSV 불러오기
# =====================================================

@st.cache_data
def load_data():
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(CSV_PATH, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일 인코딩을 읽을 수 없습니다.")


if not CSV_PATH.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        "프로젝트 최상위 폴더에 "
        "202012_202512_연령별인구현황_연간.csv 파일이 있는지 확인해 주세요."
    )
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# =====================================================
# 행정구역 이름 정리
# =====================================================

region_col = next(
    (c for c in df.columns if "행정구역" in str(c)),
    None
)

if region_col is None:
    st.error("CSV에서 행정구역 열을 찾을 수 없습니다.")
    st.stop()


def clean_region(value):
    value = str(value).strip()
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


df["_지역원본"] = df[region_col].apply(clean_region)


def extract_gu(value):
    match = re.search(r"([가-힣]+구)", value)
    return match.group(1) if match else None


df["_구"] = df["_지역원본"].apply(extract_gu)

# 구 이름만 정확하게 끝나는 행을 우선 사용한다.
# 구 단위 행이 없다면 해당 구에 속한 하위 행을 사용한다.
exact_gu = df[
    df["_지역원본"].str.match(r"^서울특별시\s*[가-힣]+구$", na=False)
].copy()

if len(exact_gu) > 0:
    df = exact_gu
else:
    df = df[df["_구"].notna()].copy()

if df.empty:
    st.error("서울시 행정구역 데이터를 찾지 못했습니다.")
    st.stop()

df["_구"] = df["_구"].astype(str)


# =====================================================
# 연도 / 성별 / 연령 열 자동 분석
# =====================================================

def get_sex(column):
    name = str(column)

    if "남" in name:
        return "남성"

    if "여" in name:
        return "여성"

    return None


def get_age_group(column):
    name = str(column)

    # 100세 이상
    if re.search(r"100\s*세\s*이상", name):
        return "100세 이상"

    # 10살 단위 연령 구간
    match = re.search(r"(\d{1,3})\s*[~∼\-]\s*(\d{1,3})\s*세", name)

    if match:
        start = int(match.group(1))
        end = int(match.group(2))

        if start % 10 == 0 and end == start + 9:
            return f"{start}~{end}세"

    # 0세, 1세처럼 한 살 단위로 나뉜 자료도 처리
    match = re.search(r"(\d{1,3})\s*세", name)

    if match:
        age = int(match.group(1))

        if age >= 100:
            return "100세 이상"

        start = (age // 10) * 10
        return f"{start}~{start + 9}세"

    return None


column_info = []

for column in df.columns:
    name = str(column)

    year_match = re.search(r"(20\d{2})\s*년?", name)

    if not year_match:
        continue

    year = int(year_match.group(1))
    sex = get_sex(name)
    age_group = get_age_group(name)

    if sex and age_group:
        column_info.append({
            "column": column,
            "year": year,
            "sex": sex,
            "age": age_group
        })


if not column_info:
    st.error(
        "연도별 성별 및 연령별 열을 찾지 못했습니다. "
        "CSV의 실제 열 이름을 확인해야 합니다."
    )
    st.stop()


# =====================================================
# 데이터 숫자 변환
# =====================================================

for info in column_info:
    col = info["column"]
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    ).fillna(0)


years = sorted(set(info["year"] for info in column_info))

age_order = [
    "0~9세", "10~19세", "20~29세", "30~39세",
    "40~49세", "50~59세", "60~69세", "70~79세",
    "80~89세", "90~99세", "100세 이상"
]

available_ages = [
    age for age in age_order
    if any(info["age"] == age for info in column_info)
]

districts = sorted(df["_구"].unique())


# =====================================================
# 집계 함수
# =====================================================

def get_population(year, sex, age=None):
    selected = [
        info for info in column_info
        if info["year"] == year
        and info["sex"] == sex
        and (age is None or info["age"] == age)
    ]

    if not selected:
        return pd.DataFrame(columns=["행정구", "인구"])

    columns = [info["column"] for info in selected]

    temp = df[["_구"] + columns].copy()

    temp["인구"] = temp[columns].sum(axis=1)

    result = (
        temp.groupby("_구", as_index=False)["인구"]
        .sum()
        .rename(columns={"_구": "행정구"})
    )

    return result


def get_total_population(year, sex):
    # 연령별 열을 합산해서 전체 인구 계산
    return get_population(year, sex, age=None)


def format_number(number):
    return f"{int(number):,}명"


# =====================================================
# 메인 화면
# =====================================================

st.markdown("""
<div class="hero">
    <div class="hero-deco">💗 ✨</div>
    <h1>서울 인구 분석 대시보드</h1>
    <p>서울의 연령별 인구와 성별 인구 분포를 한눈에 확인해 보세요.</p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# 사이드바
# =====================================================

with st.sidebar:
    st.markdown("## 💗 분석 설정")
    st.caption("원하는 조건을 선택해 주세요.")

    selected_age = st.selectbox(
        "🎂 분석할 연령대",
        available_ages,
        index=3 if "30~39세" in available_ages else 0
    )

    selected_year = st.selectbox(
        "📅 분석할 연도",
        years,
        index=len(years) - 1
    )

    st.markdown("---")
    st.markdown("### 🌷 서울 인구 데이터")
    st.caption(f"분석 가능 연도: {min(years)}년 ~ {max(years)}년")
    st.caption(f"분석 행정구 수: {len(districts)}개")

    st.markdown("---")
    st.markdown("💡 **분석 방법**")
    st.caption("연령대별 인구 순위와 연도별 남녀 인구를 비교합니다.")


# =====================================================
# 1. 연령대별 인구가 가장 많은 행정구
# =====================================================

st.markdown(
    f'<div class="section-title">🎂 {selected_age} 인구가 가장 많은 행정구</div>',
    unsafe_allow_html=True
)

male_age = get_population(selected_year, "남성", selected_age)
female_age = get_population(selected_year, "여성", selected_age)

age_result = pd.merge(
    male_age,
    female_age,
    on="행정구",
    how="outer",
    suffixes=("_남성", "_여성")
).fillna(0)

if age_result.empty:
    st.warning("선택한 연령대의 인구 데이터가 없습니다.")
else:
    age_result["전체인구"] = (
        age_result["인구_남성"] + age_result["인구_여성"]
    )

    age_result = age_result.sort_values(
        "전체인구",
        ascending=False
    ).reset_index(drop=True)

    winner = age_result.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">🏆 가장 인구가 많은 행정구</div>
            <div class="metric-value">{winner['행정구']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">👥 해당 연령대 전체 인구</div>
            <div class="metric-value">{int(winner['전체인구']):,}명</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">📅 분석 기준 연도</div>
            <div class="metric-value">{selected_year}년</div>
        </div>
        """, unsafe_allow_html=True)

    # 상위 25개 행정구
    chart_data = age_result.head(25).sort_values(
        "전체인구",
        ascending=True
    )

    fig_age = go.Figure()

    fig_age.add_trace(go.Bar(
        x=chart_data["전체인구"],
        y=chart_data["행정구"],
        orientation="h",
        marker=dict(
            color=chart_data["전체인구"],
            colorscale=[
                [0, "#FFD6EA"],
                [0.5, "#FF91C6"],
                [1, "#FF2993"]
            ],
            line=dict(color="#FFFFFF", width=1)
        ),
        text=chart_data["전체인구"].apply(
            lambda x: f"{int(x):,}명"
        ),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>인구: %{x:,.0f}명<extra></extra>"
    ))

    fig_age.update_layout(
        height=650,
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.75)",
        title=dict(
            text=f"💗 {selected_age} 행정구별 인구 순위",
            font=dict(size=21, color=DARK)
        ),
        xaxis_title="인구 수",
        yaxis_title="행정구",
        font=dict(family="Noto Sans KR", color=DARK),
        margin=dict(l=20, r=65, t=75, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F6DCEB",
            tickformat=","
        ),
        yaxis=dict(
            showgrid=False
        ),
        showlegend=False
    )

    st.plotly_chart(fig_age, use_container_width=True)

    with st.expander("📋 전체 행정구 인구 순위 보기"):
        display_age = age_result.copy()
        display_age.index = range(1, len(display_age) + 1)
        display_age.index.name = "순위"
        display_age = display_age.rename(columns={
            "행정구": "행정구",
            "인구_남성": "남성 인구",
            "인구_여성": "여성 인구",
            "전체인구": "전체 인구"
        })
        st.dataframe(
            display_age.style.format({
                "남성 인구": "{:,.0f}명",
                "여성 인구": "{:,.0f}명",
                "전체 인구": "{:,.0f}명"
            }),
            use_container_width=True
        )


# =====================================================
# 2. 연도별 남성 / 여성 인구 비교
# =====================================================

st.markdown("---")

st.markdown(
    f'<div class="section-title">👫 {selected_year}년 남녀 인구 비교</div>',
    unsafe_allow_html=True
)

male_total = get_total_population(selected_year, "남성")
female_total = get_total_population(selected_year, "여성")

gender_result = pd.merge(
    male_total,
    female_total,
    on="행정구",
    how="outer",
    suffixes=("_남성", "_여성")
).fillna(0)

if gender_result.empty:
    st.warning("선택한 연도의 성별 인구 데이터가 없습니다.")
else:
    gender_result["전체인구"] = (
        gender_result["인구_남성"] +
        gender_result["인구_여성"]
    )

    gender_result = gender_result.sort_values(
        "전체인구",
        ascending=False
    )

    male_sum = gender_result["인구_남성"].sum()
    female_sum = gender_result["인구_여성"].sum()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">👨 서울 남성 인구</div>
            <div class="metric-value" style="color:{PINK}">
                {int(male_sum):,}명
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">👩 서울 여성 인구</div>
            <div class="metric-value" style="color:{GREEN}">
                {int(female_sum):,}명
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        difference = abs(int(male_sum - female_sum))
        more = "남성" if male_sum > female_sum else "여성"

        st.markdown(f"""
        <div class="info-card">
            <div class="metric-label">✨ 인구 차이</div>
            <div class="metric-value" style="color:#9B78D4">
                {difference:,}명
            </div>
            <div class="metric-label">{more} 인구가 더 많습니다.</div>
        </div>
        """, unsafe_allow_html=True)

    # 남녀 인구 비교 그래프
    fig_gender = go.Figure()

    fig_gender.add_trace(go.Bar(
        name="남성",
        x=gender_result["행정구"],
        y=gender_result["인구_남성"],
        marker=dict(
            color=PINK,
            line=dict(color="#FFFFFF", width=1)
        ),
        hovertemplate="<b>%{x}</b><br>남성: %{y:,.0f}명<extra></extra>"
    ))

    fig_gender.add_trace(go.Bar(
        name="여성",
        x=gender_result["행정구"],
        y=gender_result["인구_여성"],
        marker=dict(
            color=GREEN,
            line=dict(color="#FFFFFF", width=1)
        ),
        hovertemplate="<b>%{x}</b><br>여성: %{y:,.0f}명<extra></extra>"
    ))

    fig_gender.update_layout(
        barmode="group",
        height=550,
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.75)",
        title=dict(
            text=f"🌸 {selected_year}년 행정구별 남녀 인구 비교",
            font=dict(size=21, color=DARK)
        ),
        xaxis_title="행정구",
        yaxis_title="인구 수",
        font=dict(family="Noto Sans KR", color=DARK),
        margin=dict(l=30, r=30, t=75, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=-35
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F2E2EC",
            tickformat=","
        ),
        bargap=0.25
    )

    st.plotly_chart(fig_gender, use_container_width=True)

    with st.expander("📊 남녀 인구 상세 데이터"):
        display_gender = gender_result[
            ["행정구", "인구_남성", "인구_여성", "전체인구"]
        ].rename(columns={
            "인구_남성": "남성 인구",
            "인구_여성": "여성 인구",
            "전체인구": "전체 인구"
        })

        st.dataframe(
            display_gender.style.format({
                "남성 인구": "{:,.0f}명",
                "여성 인구": "{:,.0f}명",
                "전체 인구": "{:,.0f}명"
            }),
            use_container_width=True
        )


# =====================================================
# 하단
# =====================================================

st.markdown("""
<div class="footer">
    💗 SEOUL POPULATION DATA DASHBOARD 💗<br>
    서울의 인구 데이터를 쉽고 아름답게 살펴보세요.
</div>
""", unsafe_allow_html=True)
