
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

# ==========================================
# 2. 디자인
# ==========================================
st.markdown("""
<style>
.stApp {
    background: #F8FAFC;
}
.main-title {
    text-align: center;
    font-size: 40px;
    font-weight: 900;
    color: #263445;
    padding-top: 15px;
}
.sub-title {
    text-align: center;
    color: #82909F;
    font-size: 16px;
    margin-bottom: 25px;
}
.section-title {
    font-size: 25px;
    font-weight: 800;
    color: #263445;
    margin-top: 20px;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #E5EAF0;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. CSV 불러오기
# ==========================================
@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    paths = [
        base_dir / "temperature.csv",
        base_dir / "temperature_utf8.csv",
        base_dir.parent / "temperature.csv",
        base_dir.parent / "temperature_utf8.csv"
    ]

    file_path = next(
        (p for p in paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    data = None

    for encoding in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 인코딩을 확인할 수 없습니다.")

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 4. 날짜 전처리
# ==========================================
required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.stop()

month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

df = df.dropna(subset=["일시"]).copy()

# 월과 두 자리 연도 분리
date_parts = df["일시"].astype(str).str.strip().str.extract(
    r"^([A-Za-z]{3})-(\d{2})$"
)

df["월"] = date_parts[0].str.title().map(month_map)
df["연도끝자리"] = pd.to_numeric(
    date_parts[1], errors="coerce"
)

df = df.dropna(subset=["월", "연도끝자리"]).copy()

df["월"] = df["월"].astype(int)
df["연도끝자리"] = df["연도끝자리"].astype(int)

# ==========================================
# ★ 핵심 수정: 1907~2026 연도 복원
# ==========================================
# 데이터가 시간순으로 정렬되어 있다는 점을 이용
# 1907~1999 -> 2000~2026으로 세기가 넘어갈 때
# 99에서 00으로 바뀌는 순간 100년을 더함

century = 1900
previous_year = None
full_years = []

for yy in df["연도끝자리"]:

    if previous_year is not None and yy < previous_year:
        century += 100

    full_years.append(century + yy)
    previous_year = yy

df["연도"] = full_years

# 숫자형 변환
temperature_columns = [
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

for col in temperature_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 1907~2025년 데이터만 사용
df = df[
    (df["연도"] >= 1907) &
    (df["연도"] <= 2025)
].copy()

# 동일 연도, 동일 월의 데이터 통합
monthly_data = (
    df.groupby(["연도", "월"])
    .agg({
        "평균기온(℃)": "mean",
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values(["연도", "월"])
)

available_years = sorted(
    monthly_data["연도"].unique().tolist()
)

if not available_years:
    st.error("1907~2025년 사이에 분석할 데이터가 없습니다.")
    st.stop()


# ==========================================
# 5. 메인 제목
# ==========================================
st.markdown(
    '<div class="main-title">🌡️ 서울 기온 분석 대시보드</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '1907년부터 2025년까지의 서울 기온 변화 살펴보기'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 6. 데이터 현황
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📅 분석 시작 연도", "1907년")

with col2:
    st.metric("📅 분석 종료 연도", "2025년")

with col3:
    st.metric("📊 데이터 연도 수", f"{len(available_years)}년")


# ==========================================
# 7. 서울 월별 평균기온 그래프
# ==========================================
st.markdown(
    '<div class="section-title">🌸 서울의 월별 평균기온</div>',
    unsafe_allow_html=True
)

st.caption(
    "1907~2025년 전체 자료에서 각 월의 평균기온을 계산한 그래프입니다."
)

# 전체 기간의 월별 평균기온 계산
climate_data = (
    monthly_data.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_names,
        y=climate_data.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#9370DB",
            width=4
        ),
        marker=dict(
            size=10,
            color="#9370DB"
        ),
        fill="tozeroy",
        fillcolor="rgba(147,112,219,0.10)",
        hovertemplate="%{x}<br>평균기온: %{y:.1f}℃<extra></extra>"
    )
)

fig1.update_layout(
    title=dict(
        text="서울의 월별 평균기온 (1907~2025)",
        x=0.5,
        xanchor="center"
    ),
    xaxis=dict(
        title="월",
        categoryorder="array",
        categoryarray=month_names
    ),
    yaxis=dict(
        title="평균기온 (℃)",
        showgrid=True,
        gridcolor="#E5EAF0"
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=480,
    hovermode="x unified",
    margin=dict(t=80, b=50)
)

st.plotly_chart(fig1, width="stretch")

st.divider()


# ==========================================
# 8. 연도 선택
# ==========================================
st.markdown(
    '<div class="section-title">📈 연도별 기온 분석 및 비교</div>',
    unsafe_allow_html=True
)

st.caption(
    "연도를 1개 선택하면 해당 연도의 최고·최저기온을, "
    "2개 선택하면 두 연도를 비교합니다."
)

selected_years = st.multiselect(
    "📅 분석할 연도를 선택하세요 (최대 2개)",
    options=available_years,
    default=[2025] if 2025 in available_years else [available_years[-1]],
    max_selections=2,
    format_func=lambda x: f"{x}년"
)


# ==========================================
# 9. 연도별 그래프
# ==========================================
if len(selected_years) == 0:

    st.info("분석할 연도를 선택해 주세요.")

else:

    selected_years = sorted(selected_years)

    fig2 = go.Figure()

    # 한 연도 선택
    if len(selected_years) == 1:

        year = selected_years[0]

        year_data = monthly_data[
            monthly_data["연도"] == year
        ].set_index("월").reindex(range(1, 13))

        st.subheader(f"📊 {year}년 최고기온 및 최저기온")

        # 최고기온
        fig2.add_trace(
            go.Scatter(
                x=month_names,
                y=year_data["최고기온(℃)"],
                mode="lines+markers",
                name="최고기온",
                connectgaps=False,
                line=dict(
                    color="#FF69B4",
                    width=4
                ),
                marker=dict(size=9),
                hovertemplate="%{x}<br>최고기온: %{y:.1f}℃<extra></extra>"
            )
        )

        # 최저기온
        fig2.add_trace(
            go.Scatter(
                x=month_names,
                y=year_data["최저기온(℃)"],
                mode="lines+markers",
                name="최저기온",
                connectgaps=False,
                line=dict(
                    color="#87CEEB",
                    width=4
                ),
                marker=dict(size=9),
                hovertemplate="%{x}<br>최저기온: %{y:.1f}℃<extra></extra>"
            )
        )

    # 두 연도 선택
    elif len(selected_years) == 2:

        year1, year2 = selected_years

        st.subheader(f"📊 {year1}년 vs {year2}년 기온 비교")

        colors = {
            year1: {
                "high": "#FF69B4",
                "low": "#87CEEB"
            },
            year2: {
                "high": "#E91E63",
                "low": "#1E90FF"
            }
        }

        for year in selected_years:

            year_data = monthly_data[
                monthly_data["연도"] == year
            ].set_index("월").reindex(range(1, 13))

            # 최고기온
            fig2.add_trace(
                go.Scatter(
                    x=month_names,
                    y=year_data["최고기온(℃)"],
                    mode="lines+markers",
                    name=f"{year}년 최고기온",
                    connectgaps=False,
                    line=dict(
                        color=colors[year]["high"],
                        width=3,
                        dash="solid" if year == year1 else "dash"
                    ),
                    marker=dict(size=8),
                    hovertemplate=(
                        f"{year}년 최고기온<br>"
                        "%{x}: %{y:.1f}℃<extra></extra>"
                    )
                )
            )

            # 최저기온
            fig2.add_trace(
                go.Scatter(
                    x=month_names,
                    y=year_data["최저기온(℃)"],
                    mode="lines+markers",
                    name=f"{year}년 최저기온",
                    connectgaps=False,
                    line=dict(
                        color=colors[year]["low"],
                        width=3,
                        dash="solid" if year == year1 else "dash"
                    ),
                    marker=dict(size=8),
                    hovertemplate=(
                        f"{year}년 최저기온<br>"
                        "%{x}: %{y:.1f}℃<extra></extra>"
                    )
                )
            )

    # 공통 그래프 디자인
    fig2.update_layout(
        title=dict(
            text="연도별 최고기온 및 최저기온 분석",
            x=0.5,
            xanchor="center",
            font=dict(size=24)
        ),
        xaxis=dict(
            title="월",
            categoryorder="array",
            categoryarray=month_names
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
        margin=dict(t=100, b=50)
    )

    st.plotly_chart(fig2, width="stretch")


# ==========================================
# 10. 상세 데이터
# ==========================================
with st.expander("📋 연도별 월별 상세 데이터 확인"):

    if selected_years:

        table_data = monthly_data[
            monthly_data["연도"].isin(selected_years)
        ].copy()

        table_data["월"] = table_data["월"].map(
            lambda x: f"{x}월"
        )

        table_data = table_data.rename(
            columns={
                "연도": "연도",
                "월": "월",
                "평균기온(℃)": "평균기온(℃)",
                "최고기온(℃)": "최고기온(℃)",
                "최저기온(℃)": "최저기온(℃)"
            }
        )

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("연도를 선택하면 상세 데이터가 표시됩니다.")


# ==========================================
# 11. 하단
# ==========================================
st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#82909F; padding:15px;">
        🌡️ SEOUL TEMPERATURE ANALYSIS<br>
        Data Analysis: Pandas | Visualization: Plotly | Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
