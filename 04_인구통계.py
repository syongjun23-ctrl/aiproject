
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path

# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="서울 연령별 인구 분석",
    page_icon="💗",
    layout="wide"
)

# ==================================================
# 2. 디자인 설정
# ==================================================

st.markdown("""
<style>
    .stApp {
        background-color: #FFF8FC;
    }

    h1, h2, h3 {
        color: #C21870;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #F5C5DF;
        padding: 20px;
        border-radius: 15px;
    }

    div[data-testid="stSelectbox"] label {
        color: #C21870;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("💗 서울 연령별 인구 분석")
st.markdown(
    "행정구역과 성별, 연도를 선택하여 연령별 인구를 분석해 보세요."
)

st.divider()

# ==================================================
# 3. 프로젝트 폴더 경로 설정
# ==================================================

# 현재 파일은 pages 폴더 안에 있음
# parent = pages
# parent.parent = 프로젝트 최상위 폴더

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = (
    BASE_DIR /
    "202012_202512_연령별인구현황_연간.csv"
)

# ==================================================
# 4. CSV 한글 인코딩 처리
# ==================================================

def load_csv(uploaded_file=None):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    errors = []

    for encoding in encodings:

        try:

            if uploaded_file is not None:

                uploaded_file.seek(0)

                data = pd.read_csv(
                    uploaded_file,
                    encoding=encoding,
                    thousands=","
                )

            else:

                data = pd.read_csv(
                    CSV_PATH,
                    encoding=encoding,
                    thousands=","
                )

            return data, encoding

        except (UnicodeDecodeError, UnicodeError) as e:

            errors.append(f"{encoding}: {e}")

    raise ValueError(
        "CSV 파일을 읽을 수 없습니다.\n"
        + "\n".join(errors)
    )


# ==================================================
# 5. CSV 파일 불러오기
# ==================================================

uploaded_file = st.file_uploader(
    "📂 인구 통계 CSV 파일 업로드",
    type=["csv"]
)

try:

    if uploaded_file is not None:

        df, encoding_used = load_csv(uploaded_file)

    else:

        if not CSV_PATH.exists():

            st.error(
                "CSV 파일을 찾을 수 없습니다.\n\n"
                f"파일 경로: {CSV_PATH}"
            )

            st.stop()

        df, encoding_used = load_csv()

except Exception as e:

    st.error(f"파일을 불러오지 못했습니다: {e}")
    st.stop()


st.success(
    f"데이터 불러오기 성공! (인코딩: {encoding_used})"
)

# ==================================================
# 6. 데이터 정리
# ==================================================

df.columns = df.columns.astype(str).str.strip()

if "행정구역" not in df.columns:

    st.error("'행정구역' 열이 없습니다.")
    st.stop()


# 행정구역 코드 제거
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(
        r"\s*\(\s*\d+\s*\)\s*$",
        "",
        regex=True
    )
    .str.strip()
)


# 숫자 데이터 변환
for column in df.columns:

    if column not in ["행정구역", "행정구역명"]:

        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(
                ",",
                "",
                regex=False
            ),
            errors="coerce"
        )


# ==================================================
# 7. 연도 자동 추출
# ==================================================

years = sorted({

    int(match.group(1))

    for column in df.columns

    if (match := re.match(
        r"^(20\d{2})년_",
        column
    ))

})

if not years:

    st.error("연도 데이터를 찾을 수 없습니다.")
    st.stop()


# ==================================================
# 8. 연령대 설정
# ==================================================

age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


sex_prefix = {

    "전체": "거주자",
    "남성": "남_거주자",
    "여성": "여_거주자"

}


# ==================================================
# 9. 행정구역 목록
# ==================================================

regions = (
    df["행정구역명"]
    .dropna()
    .unique()
    .tolist()
)

regions = sorted(
    regions,
    key=lambda x: (
        0 if x == "서울특별시" else 1,
        x
    )
)


# ==================================================
# 10. 선택 메뉴
# ==================================================

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:

    selected_region = st.selectbox(
        "🏙️ 행정구역 선택",
        regions
    )

with col2:

    selected_sex = st.selectbox(
        "🚻 성별 선택",
        ["전체", "남성", "여성"]
    )

with col3:

    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1
    )


# ==================================================
# 11. 선택한 데이터 가져오기
# ==================================================

selected_data = df[
    df["행정구역명"] == selected_region
]

if selected_data.empty:

    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()


row = selected_data.iloc[0]

prefix = (
    f"{selected_year}년_"
    f"{sex_prefix[selected_sex]}_"
)


chart_values = []

for age in age_groups:

    column_name = prefix + age

    if column_name not in df.columns:

        st.error(
            f"데이터 열을 찾을 수 없습니다: {column_name}"
        )

        st.stop()

    value = row[column_name]

    if pd.isna(value):
        value = 0

    chart_values.append(int(value))


chart_df = pd.DataFrame({

    "나이": age_groups,
    "인구수": chart_values

})


# ==================================================
# 12. 주요 통계
# ==================================================

total_population = sum(chart_values)

max_index = chart_df["인구수"].idxmax()

max_age = chart_df.loc[max_index, "나이"]

max_population = chart_df.loc[
    max_index,
    "인구수"
]


st.divider()

st.subheader(
    f"📊 {selected_region} 인구 통계"
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "연령별 인구 합계",
    f"{total_population:,}명"
)

m2.metric(
    "인구가 가장 많은 연령대",
    max_age
)

m3.metric(
    "해당 연령대 인구",
    f"{max_population:,}명"
)


# ==================================================
# 13. 핫핑크 꺾은선 그래프
# ==================================================

st.divider()

st.subheader("📈 연령별 인구 꺾은선 그래프")


# 세로축 1,000만 명 단위
INTERVAL = 10_000_000

maximum = max(chart_values)

y_max = max(
    INTERVAL,
    ((maximum // INTERVAL) + 1) * INTERVAL
)


fig = go.Figure()


fig.add_trace(

    go.Scatter(

        x=chart_df["나이"],

        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color="#FF1493",
            width=4
        ),

        marker=dict(
            color="#FF1493",
            size=11,
            line=dict(
                color="white",
                width=2
            )
        ),

        hovertemplate=
        "<b>%{x}</b><br>"
        "인구수: %{y:,.0f}명"
        "<extra></extra>"

    )

)


fig.update_layout(

    height=600,

    plot_bgcolor="#FFFFFF",

    paper_bgcolor="#FFFFFF",

    font=dict(
        family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif",
        size=13,
        color="#49313F"
    ),

    margin=dict(
        l=50,
        r=30,
        t=40,
        b=80
    ),

    hovermode="x unified",

    showlegend=False,

    # 가로축
    xaxis=dict(

        title="나이",

        type="category",

        categoryorder="array",

        categoryarray=age_groups,

        tickmode="array",

        tickvals=age_groups,

        ticktext=age_groups,

        tickangle=0,

        showgrid=True,

        gridcolor="#F4C9DF",

        gridwidth=1.2,

        linecolor="#E8A4C5"

    ),

    # 세로축
    yaxis=dict(

        title="인구수 (명)",

        range=[0, y_max],

        tickmode="linear",

        tick0=0,

        dtick=INTERVAL,

        tickformat=",",

        showgrid=True,

        gridcolor="#E5DCE3",

        gridwidth=1.2,

        zeroline=True,

        zerolinecolor="#C9A9BC"

    )

)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "💗 핫핑크 선으로 연령별 인구를 표시합니다. "
    "가로축은 10살 단위이며 세로축 격자선은 "
    "1,000만 명 간격입니다."
)


# ==================================================
# 14. 상세 인구 데이터
# ==================================================

st.divider()

with st.expander("📋 연령별 상세 인구 데이터 확인"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].apply(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 15. 원본 데이터 확인
# ==================================================

with st.expander("📁 원본 CSV 데이터 확인"):

    st.dataframe(
        df,
        use_container_width=True
    )


# ==================================================
# 16. 데이터 다운로드
# ==================================================

csv_output = df.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(

    label="📥 정리된 CSV 다운로드",

    data=csv_output,

    file_name="서울_연령별_인구통계.csv",

    mime="text/csv"

)


# ==================================================
# 17. 하단 안내
# ==================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#C21870;">
        💗 서울 연령별 인구 분석 시스템
        <br>
        데이터 기준: 2020년 ~ 2025년
    </div>
    """,
    unsafe_allow_html=True
)
