
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------------------------
# 기본 설정
# app.py에서 set_page_config를 실행하므로 여기서는 실행하지 않음
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080D1B 0%, #11152B 55%, #17132D 100%);
    color: #F5F7FF;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 38px 35px;
    border-radius: 24px;
    background: linear-gradient(115deg, #172554, #312E81, #581C87);
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 15px 45px rgba(0,0,0,0.25);
    margin-bottom: 28px;
}

.hero h1 {
    color: white;
    font-size: 39px;
    font-weight: 900;
    letter-spacing: -1.5px;
    margin: 0;
}

.hero p {
    color: #D8DBFF;
    font-size: 15px;
    margin-top: 10px;
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 15px;
    color: #F5F7FF;
}

.metric-card {
    background: rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 20px;
    min-height: 115px;
}

.metric-label {
    color: #A5B4FC;
    font-size: 13px;
    font-weight: 700;
}

.metric-value {
    color: white;
    font-size: 27px;
    font-weight: 900;
    margin-top: 9px;
}

.metric-sub {
    color: #A5AFCB;
    font-size: 12px;
    margin-top: 4px;
}

div[data-testid="stSelectbox"] label {
    color: #DCE3FF;
    font-weight: 700;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 15px;
}

.footer {
    text-align: center;
    color: #7F8AAE;
    font-size: 12px;
    margin-top: 45px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CSV 파일 자동 찾기
# 현재 파일: 프로젝트/pages/01_mbti.py
# CSV 파일: 프로젝트/countriesMBTI_16types.csv
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def find_csv():

    possible_names = [
        "countriesMBTI_16types.csv",
        "countriesMBTI_16types (1).csv",
        "countriesMBTI_16types (2).csv"
    ]

    # 1. 예상 파일명으로 먼저 검색
    for name in possible_names:
        path = PROJECT_ROOT / name

        if path.is_file():
            return path

    # 2. 비슷한 이름의 CSV 자동 검색
    try:
        matches = list(
            PROJECT_ROOT.glob("countriesMBTI_16types*.csv")
        )

        if matches:
            return matches[0]

    except Exception:
        pass

    # 3. 프로젝트 내부의 다른 폴더까지 검색
    try:
        matches = list(
            PROJECT_ROOT.rglob("countriesMBTI_16types*.csv")
        )

        if matches:
            return matches[0]

    except Exception:
        pass

    return None


# --------------------------------------------------
# CSV 불러오기
# --------------------------------------------------

@st.cache_data
def load_data(file_path, modified_time):

    encodings = ["utf-8-sig", "utf-8", "cp949", "latin1"]
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )

            data.columns = [
                str(column).strip()
                for column in data.columns
            ]

            return data

        except Exception as error:
            last_error = error

    raise RuntimeError(
        f"CSV 파일을 읽을 수 없습니다: {last_error}"
    )


# --------------------------------------------------
# 데이터 로딩 및 오류 처리
# --------------------------------------------------

try:

    csv_path = find_csv()

    if csv_path is None:

        st.error("CSV 파일을 찾을 수 없습니다.")

        st.write("현재 페이지 위치:")
        st.code(str(Path(__file__).resolve()))

        st.write("검색한 프로젝트 최상위 폴더:")
        st.code(str(PROJECT_ROOT))

        st.write("최상위 폴더의 파일 목록:")

        try:
            st.write([
                item.name
                for item in PROJECT_ROOT.iterdir()
            ])
        except Exception as error:
            st.write(str(error))

        st.info(
            "CSV 파일 이름이 countriesMBTI_16types로 시작하는지 "
            "확인해 주세요."
        )

        st.stop()

    df = load_data(
        str(csv_path),
        csv_path.stat().st_mtime
    )

except Exception as error:

    st.error("데이터를 불러오는 과정에서 오류가 발생했습니다.")
    st.exception(error)
    st.stop()


# --------------------------------------------------
# 데이터 정리
# --------------------------------------------------

# 국가 이름 열 찾기
country_candidates = [
    "Country",
    "country",
    "COUNTRY",
    "국가",
    "나라"
]

country_column = None

for candidate in country_candidates:

    if candidate in df.columns:
        country_column = candidate
        break

if country_column is None:

    st.error("국가 이름을 나타내는 열을 찾을 수 없습니다.")

    st.write("현재 CSV의 열 이름:")
    st.write(list(df.columns))

    st.stop()


# MBTI 16가지 유형
mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

# 대소문자에 관계없이 MBTI 열 찾기
column_lookup = {
    str(column).strip().upper(): column
    for column in df.columns
}

available_types = [
    mbti
    for mbti in mbti_types
    if mbti in column_lookup
]

if len(available_types) != 16:

    st.error("MBTI 데이터 열이 16개 모두 존재하지 않습니다.")

    st.write("찾은 MBTI 열:")
    st.write(available_types)

    st.write("CSV 전체 열:")
    st.write(list(df.columns))

    st.stop()


# MBTI 열 이름 통일
rename_columns = {
    column_lookup[mbti]: mbti
    for mbti in available_types
}

df = df.rename(columns=rename_columns)


# 국가 이름 정리
df[country_column] = (
    df[country_column]
    .astype(str)
    .str.strip()
)

df = df[
    df[country_column].notna()
    & (df[country_column] != "")
    & (df[country_column] != "nan")
].copy()


# 숫자 데이터 정리
for mbti in mbti_types:

    df[mbti] = (
        df[mbti]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df[mbti] = pd.to_numeric(
        df[mbti],
        errors="coerce"
    )

df = df.dropna(subset=mbti_types, how="all")

if df.empty:
    st.error("표시할 MBTI 데이터가 없습니다.")
    st.stop()


# --------------------------------------------------
# 화면 상단
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🌍 WORLD MBTI ATLAS</h1>
    <p>COUNTRY PERSONALITY ANALYSIS · 세계 국가별 MBTI 분석</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 국가 선택
# --------------------------------------------------

countries = sorted(
    df[country_column].unique().tolist()
)

default_index = 0

for i, country in enumerate(countries):

    if country.lower() in [
        "south korea",
        "korea",
        "korea, republic of",
        "대한민국",
        "한국"
    ]:
        default_index = i
        break

st.markdown(
    '<div class="section-title">🗺️ 국가 선택</div>',
    unsafe_allow_html=True
)

selected_country = st.selectbox(
    "분석하고 싶은 국가를 선택하세요.",
    countries,
    index=default_index
)


# --------------------------------------------------
# 선택한 국가 데이터 추출
# --------------------------------------------------

country_data = df[
    df[country_column] == selected_country
]

if country_data.empty:

    st.error("선택한 국가의 데이터를 찾을 수 없습니다.")
    st.stop()


values = country_data.iloc[0][mbti_types].copy()

values = pd.to_numeric(
    values,
    errors="coerce"
).fillna(0)


# 데이터가 소수 비율이면 퍼센트로 변환
if values.max() <= 1.5:
    values = values * 100


# 정렬
result = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": values.values
})

result = result.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)


# --------------------------------------------------
# 주요 결과
# --------------------------------------------------

top_mbti = result.iloc[0]["MBTI"]
top_percentage = result.iloc[0]["비율"]

average_percentage = result["비율"].mean()

st.markdown(
    '<div class="section-title">📊 분석 결과</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌎 SELECTED COUNTRY</div>
        <div class="metric-value">{selected_country}</div>
        <div class="metric-sub">선택한 국가</div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🏆 TOP MBTI</div>
        <div class="metric-value">{top_mbti}</div>
        <div class="metric-sub">가장 높은 비율의 유형</div>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 TOP PERCENTAGE</div>
        <div class="metric-value">{top_percentage:.2f}%</div>
        <div class="metric-sub">1위 MBTI 비율</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# MBTI 그래프
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🧬 MBTI DISTRIBUTION</div>',
    unsafe_allow_html=True
)

# 1위는 빨간색
# 나머지는 순위에 따라 파란색에서 연한 파란색으로
blue_colors = [
    "#2563EB",
    "#3475E8",
    "#4386EC",
    "#5295EF",
    "#62A3F2",
    "#71AFF4",
    "#80BBF6",
    "#8FC6F8",
    "#9ED0FA",
    "#ADD9FB",
    "#BCE2FC",
    "#CBEAFF",
    "#D6EEFF",
    "#E0F3FF",
    "#EAF7FF"
]

bar_colors = ["#F04452"] + blue_colors[:15]

chart = go.Figure()

chart.add_trace(
    go.Bar(
        x=result["비율"],
        y=result["MBTI"],
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(
                color="rgba(255,255,255,0.12)",
                width=1
            ),
            cornerradius=7
        ),
        text=[
            f"{value:.2f}%"
            for value in result["비율"]
        ],
        textposition="outside",
        textfont=dict(
            color="#FFFFFF",
            size=12
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)

chart.update_layout(
    height=650,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#E5E7EB",
        family="Arial"
    ),
    margin=dict(
        l=30,
        r=80,
        t=20,
        b=35
    ),
    xaxis=dict(
        title="MBTI 비율 (%)",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.09)",
        zeroline=False,
        ticksuffix="%"
    ),
    yaxis=dict(
        title="",
        autorange="reversed",
        showgrid=False
    ),
    showlegend=False,
    bargap=0.28
)

st.plotly_chart(
    chart,
    use_container_width=True
)


# --------------------------------------------------
# 상세 데이터
# --------------------------------------------------

with st.expander("📋 MBTI 16가지 유형 상세 비율 확인"):

    display_df = result.copy()

    display_df["순위"] = range(1, len(display_df) + 1)

    display_df["비율"] = display_df["비율"].map(
        lambda value: f"{value:.2f}%"
    )

    display_df = display_df[
        ["순위", "MBTI", "비율"]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 데이터 정보
# --------------------------------------------------

st.markdown("---")

st.caption(
    f"📁 데이터 파일: {csv_path.name}  |  "
    f"🌍 등록 국가 수: {len(countries)}개  |  "
    f"🧬 MBTI 유형: 16개"
)

st.caption(
    "※ 데이터의 비율은 제공된 CSV 원본을 기준으로 표시합니다. "
    "실제 국가 전체 인구의 성격 분포를 의미하지 않을 수 있습니다."
)

st.markdown("""
<div class="footer">
    WORLD MBTI ATLAS · DISCOVER YOUR WORLD
</div>
""", unsafe_allow_html=True)
