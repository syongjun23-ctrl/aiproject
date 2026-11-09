
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

# ==========================================
# 2. 디자인 CSS
# ==========================================
st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #263445;
    padding: 20px 0 5px 0;
}
.sub-title {
    text-align: center;
    color: #7B8794;
    font-size: 16px;
    margin-bottom: 30px;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #E8EDF3;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    possible_paths = [
        base_dir / "temperature.csv",
        base_dir / "temperature_utf8.csv",
        base_dir.parent / "temperature.csv",
        base_dir.parent / "temperature_utf8.csv"
    ]

    file_path = next(
        (p for p in possible_paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 인코딩을 읽을 수 없습니다.")

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

required_columns = ["일시", "최고기온(℃)", "최저기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

# 빈 행 제거
df = df.dropna(subset=["일시"]).copy()

# 월 이름과 연도 분리
month_dict = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_date(value):
    try:
        month_text, year_text = str(value).strip().split("-")

        month = month_dict[month_text.title()]
        year = int(year_text)

        # 두 자리 연도 변환
        if year <= 68:
            year += 2000
        else:
            year += 1900

        return pd.Series([year, month])

    except (ValueError, KeyError, TypeError):
        return pd.Series([None, None])


df[["연도", "월"]] = df["일시"].apply(parse_date)

df = df.dropna(subset=["연도", "월"]).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# 기온을 숫자로 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)


# ==========================================
# 5. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🌡️ 월별 기온분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 6. 월 선택
# ==========================================

month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: month_names[x - 1],
    index=0
)


# ==========================================
# 7. 선택한 월의 데이터 분석
# ==========================================

month_df = df[df["월"] == selected_month].copy()

if month_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# 동일 연월에 여러 행이 있으면 극값으로 통합
result = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

result = result.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"],
    how="all"
)

if result.empty:
    st.warning("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()


# ==========================================
# 8. 주요 통계
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📊 분석 연도 수",
        f"{len(result)}년"
    )

with col2:
    max_temp = result["최고기온(℃)"].max()
    st.metric(
        "🔥 가장 높은 최고기온",
        f"{max_temp:.1f}℃"
    )

with col3:
    min_temp = result["최저기온(℃)"].min()
    st.metric(
        "❄️ 가장 낮은 최저기온",
        f"{min_temp:.1f}℃"
    )


st.markdown("### 📈 연도별 최고기온과 최저기온")

# ==========================================
# 9. 그래프 생성
# ==========================================

fig = go.Figure()

# 최고기온 - 핫핑크
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="#FF69B4",
            width=3
        ),
        marker=dict(
            size=9,
            color="#FF69B4"
        ),
        hovertemplate=
        "%{x}년<br>최고기온: %{y:.1f}℃<extra></extra>"
    )
)

# 최저기온 - 하늘색
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="#87CEEB",
            width=3
        ),
        marker=dict(
            size=9,
            color="#87CEEB"
        ),
        hovertemplate=
        "%{x}년<br>최저기온: %{y:.1f}℃<extra></extra>"
    )
)

# 그래프 레이아웃
fig.update_layout(
    title=dict(
        text="월별 기온분석",
        x=0.5,
        xanchor="center",
        font=dict(size=25, color="#263445")
    ),

    xaxis=dict(
        title="연도",
        tickmode="linear",
        dtick=1,
        showgrid=True,
        gridcolor="#E5EAF0"
    ),

    yaxis=dict(
        title="온도 (℃)",
        showgrid=True,
        gridcolor="#E5EAF0",
        zeroline=True
    ),

    legend=dict(
        title="기온 구분",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    height=550,
    margin=dict(l=40, r=40, t=100, b=50)
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. 분석 데이터 표
# ==========================================

with st.expander("📋 연도별 상세 데이터 확인하기"):

    display_df = result.rename(columns={
        "연도": "연도",
        "최고기온(℃)": "최고기온 (℃)",
        "최저기온(℃)": "최저기온 (℃)"
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.caption(
    "🌡️ 데이터 분석: Python Pandas | "
    "그래프 제작: Plotly | "
    "웹 앱: Streamlit"
)
zs
