
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="WORLD MBTI ATLAS",
    page_icon="🌎",
    layout="wide"
)

# ==========================================
# 2. 디자인 CSS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Noto Sans KR', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 8% 5%, rgba(45, 91, 160, .20), transparent 30%),
        radial-gradient(circle at 92% 15%, rgba(100, 70, 170, .13), transparent 28%),
        #080D18;
    color: #F5F7FB;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.hero {
    padding: 38px 36px;
    border-radius: 25px;
    background: linear-gradient(
        120deg,
        #172944 0%,
        #111B2D 60%,
        #25213B 100%
    );
    border: 1px solid rgba(255,255,255,.09);
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.eyebrow {
    color: #9DBCFB;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 4px;
    margin-bottom: 13px;
}

.hero h1 {
    color: white;
    font-size: clamp(36px, 6vw, 62px);
    line-height: 1.05;
    letter-spacing: -2.5px;
    font-weight: 900;
    margin: 0;
}

.hero h1 span {
    color: #8DB5FF;
}

.hero p {
    color: #B8C5D8;
    line-height: 1.8;
    margin: 15px 0 0;
    font-size: 14px;
}

.panel {
    background: linear-gradient(145deg, #172337, #101827);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    padding: 20px 22px;
}

.section-title {
    color: #F5F7FB;
    font-size: 23px;
    font-weight: 900;
    letter-spacing: -.7px;
    margin: 28px 0 5px;
}

.section-sub {
    color: #91A0B6;
    font-size: 13px;
    margin-bottom: 17px;
}

.stat-label {
    color: #93A4BC;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.stat-value {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 900;
    margin-top: 5px;
}

div[data-baseweb="select"] > div {
    background: #172337;
    border-color: #34445E;
    border-radius: 10px;
}

label {
    color: #D8E0EC !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.footer {
    text-align: center;
    color: #65758C;
    font-size: 11px;
    margin-top: 42px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,.08);
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. CSV 파일 경로 설정
# ==========================================

# 현재 파일은 pages 폴더 안에 있음
# parent.parent를 사용하면 프로젝트 최상위 폴더로 이동

CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "countriesMBTI_16types.csv"
)


# ==========================================
# 4. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

    data = pd.read_csv(file_path)

    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 Country 열이 없습니다.")

    data["Country"] = data["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in data.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 유형 열이 16개여야 합니다. "
            f"현재 {len(mbti_columns)}개입니다."
        )

    for col in mbti_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(subset=["Country"])
    data = data.dropna(subset=mbti_columns, how="all")

    return data, mbti_columns


try:

    df, mbti_types = load_data(CSV_PATH)

except FileNotFoundError:

    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        "프로젝트 최상위 폴더에 "
        "'countriesMBTI_16types.csv' 파일이 있는지 확인해 주세요."
    )

    st.stop()

except Exception as error:

    st.error(f"데이터를 읽는 중 문제가 발생했습니다: {error}")

    st.stop()


# ==========================================
# 5. 메인 화면
# ==========================================

st.markdown("""
<div class="hero">

    <div class="eyebrow">
        EXPLORE PERSONALITY AROUND THE WORLD
    </div>

    <h1>
        WORLD<br>
        <span>MBTI ATLAS.</span>
    </h1>

    <p>
        Discover personality around the world.<br>
        국가를 선택하고 그 나라의 MBTI 분포를 한눈에 확인해 보세요.
    </p>

</div>
""", unsafe_allow_html=True)


# ==========================================
# 6. 국가 선택
# ==========================================

st.markdown(
    '<div class="section-title">🌎 국가 선택</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-sub">'
    '분석하고 싶은 국가를 선택하면 MBTI 비율 그래프가 나타납니다.'
    '</div>',
    unsafe_allow_html=True
)

countries = sorted(
    df["Country"].dropna().unique().tolist()
)

preferred = "South Korea"

default_index = (
    countries.index(preferred)
    if preferred in countries
    else 0
)

left, right = st.columns([2, 1])

with left:

    selected_country = st.selectbox(
        "국가를 선택하세요",
        countries,
        index=default_index
    )

with right:

    st.markdown(
        f"""
        <div class="panel" style="margin-top: 28px;">

            <div class="stat-label">
                COUNTRIES IN DATA
            </div>

            <div class="stat-value">
                {len(countries)}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# 7. 선택 국가의 MBTI 비율 계산
# ==========================================

country_row = df.loc[
    df["Country"] == selected_country
].iloc[0]

values = country_row[mbti_types].astype(float)

# 원본 값이 0~1 사이 소수라면 퍼센트로 변환
if values.max() <= 1.5:
    values = values * 100

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": values.values
})

chart_data = chart_data.dropna()

chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 가장 높은 비율의 MBTI
winner = chart_data.iloc[0]

winner_type = winner["MBTI"]
winner_rate = winner["비율"]


# ==========================================
# 8. 그라데이션 색상 함수
# ==========================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(*rgb)


def interpolate_color(start_hex, end_hex, ratio):

    start = hex_to_rgb(start_hex)
    end = hex_to_rgb(end_hex)

    rgb = tuple(
        round(
            start[i] + (end[i] - start[i]) * ratio
        )
        for i in range(3)
    )

    return rgb_to_hex(rgb)


# 1위는 빨간색
bar_colors = ["#F04452"]

# 나머지는 파란색에서 연한 파란색으로
number_of_blue_bars = max(len(chart_data) - 1, 1)

for i in range(1, len(chart_data)):

    ratio = (
        (i - 1) /
        max(number_of_blue_bars - 1, 1)
    )

    color = interpolate_color(
        "#2563EB",
        "#C7DCFF",
        ratio
    )

    bar_colors.append(color)


# ==========================================
# 9. 결과 요약 카드
# ==========================================

st.markdown(
    '<div class="section-title">📊 MBTI DISTRIBUTION</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="section-sub">'
    f'{selected_country}의 MBTI 유형별 비율을 높은 순서대로 보여줍니다.'
    f'</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="panel">

            <div class="stat-label">
                SELECTED COUNTRY
            </div>

            <div class="stat-value" style="font-size:23px;">
                {selected_country}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="panel">

            <div class="stat-label">
                TOP MBTI
            </div>

            <div class="stat-value" style="color:#F04452;">
                {winner_type}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="panel">

            <div class="stat-label">
                TOP TYPE RATIO
            </div>

            <div class="stat-value">
                {winner_rate:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# 10. 막대그래프 생성
# ==========================================

fig = go.Figure()

fig.add_trace(
    go.Bar(

        x=chart_data["비율"],

        y=chart_data["MBTI"],

        orientation="h",

        marker=dict(
            color=bar_colors,
            line=dict(
                color="rgba(255,255,255,0.10)",
                width=1
            )
        ),

        text=[
            f"{v:.2f}%"
            for v in chart_data["비율"]
        ],

        textposition="outside",

        textfont=dict(
            color="#EAF0FA",
            size=12
        ),

        hovertemplate=
        "<b>%{y}</b><br>"
        "비율: %{x:.2f}%"
        "<extra></extra>"
    )
)


# 그래프 디자인
fig.update_layout(

    height=650,

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    margin=dict(
        l=25,
        r=65,
        t=20,
        b=45
    ),

    xaxis=dict(
        title=dict(
            text="비율 (%)",
            font=dict(color="#AAB8CC")
        ),

        showgrid=True,

        gridcolor="rgba(255,255,255,0.09)",

        zeroline=False,

        tickfont=dict(
            color="#AAB8CC"
        ),

        rangemode="tozero"
    ),

    yaxis=dict(
        title="",

        autorange="reversed",

        tickfont=dict(
            color="#F0F4FA",
            size=13
        ),

        showgrid=False
    ),

    showlegend=False,

    bargap=0.28,

    font=dict(
        family="DM Sans, Noto Sans KR, sans-serif",
        color="#F5F7FB"
    )
)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# ==========================================
# 11. 정확한 수치 확인
# ==========================================

with st.expander("📋 정확한 수치 확인하기"):

    display_data = chart_data.copy()

    display_data["비율"] = display_data["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 12. 안내 문구
# ==========================================

st.caption(
    "그래프 색상: 1위 유형은 빨간색, "
    "나머지 유형은 진한 파란색에서 연한 파란색으로 표시됩니다."
)

st.info(
    "참고: 이 그래프는 제공된 CSV 데이터의 국가별 비율을 "
    "시각화한 것입니다. 조사 대상과 표본에 따라 "
    "실제 인구 전체의 MBTI 분포와 다를 수 있습니다."
)


# ==========================================
# 13. 하단
# ==========================================

st.markdown("""
<div class="footer">

    WORLD MBTI ATLAS<br>
    EXPLORE THE WORLD THROUGH PERSONALITY 🌎

</div>
""", unsafe_allow_html=True)
