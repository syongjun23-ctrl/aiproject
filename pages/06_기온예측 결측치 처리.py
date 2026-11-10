
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 기온 분석 & 미래 예측",
    page_icon="🌡️",
    layout="wide"
)


# ==========================================
# 2. 디자인
# ==========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #101827 0%, #17243a 100%);
        color: white;
    }

    h1, h2, h3, p, label {
        color: white !important;
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #69d5ff, #bd9cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sub-title {
        color: #aab9d0;
        font-size: 15px;
        margin-bottom: 30px;
    }

    .info-card {
        background: #202f46;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #34445e;
        margin-bottom: 15px;
    }

    .info-card h3 {
        margin-top: 0;
    }

    div[data-testid="stMetric"] {
        background: #202f46;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #34445e;
    }

    div[data-testid="stMetricValue"] {
        color: #69d5ff;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .small-text {
        color: #aab9d0;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    base_path = Path(__file__).resolve().parent.parent

    possible_files = [
        base_path / "temperature_utf8.csv",
        base_path / "temperature.csv",
        base_path / "서울기온.csv"
    ]

    file_path = next(
        (p for p in possible_files if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "CSV 파일을 찾을 수 없습니다. "
            "temperature_utf8.csv 파일을 프로젝트 최상위 폴더에 넣어주세요."
        )

    last_error = None

    for encoding in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:

        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break

        except UnicodeDecodeError as e:
            last_error = e

    else:
        raise ValueError(f"CSV 인코딩 오류: {last_error}")

    required_columns = ["일시", "평균기온(℃)"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV에 '{col}' 열이 없습니다. 현재 열: {list(df.columns)}"
            )

    df["일시"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        errors="coerce"
    )

    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    df = df.dropna(
        subset=["일시", "평균기온(℃)"]
    ).copy()

    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    df = df[
        (df["연도"] >= 1907) &
        (df["연도"] <= 2025)
    ]

    return df


# ==========================================
# 4. 데이터 오류 처리
# ==========================================

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 실패: {e}")
    st.stop()


# ==========================================
# 5. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🌡️ SEOUL CLIMATE LAB</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '1907년부터 2025년까지의 기온 데이터 분석과 미래 기온 예측'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# 6. 기본 데이터 통계
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "📅 분석 기간",
    "1907 ~ 2025"
)

col2.metric(
    "📊 관측 데이터",
    f"{len(df):,}개"
)

col3.metric(
    "🌡️ 전체 평균기온",
    f"{df['평균기온(℃)'].mean():.2f} ℃"
)


# ==========================================
# 7. 월 선택
# ==========================================

st.markdown(
    '<div class="section-title">📈 월별 평균기온 분석</div>',
    unsafe_allow_html=True
)

month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

selected_month_name = st.selectbox(
    "분석할 월을 선택하세요.",
    month_names
)

selected_month = month_names.index(
    selected_month_name
) + 1


# ==========================================
# 8. 선택한 월의 연도별 평균기온
# ==========================================

monthly_df = df[
    df["월"] == selected_month
].groupby("연도")["평균기온(℃)"].mean().reset_index()

monthly_df = monthly_df.sort_values("연도")

st.markdown(
    f"### 🌡️ {selected_month}월 연도별 평균기온"
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["평균기온(℃)"],
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="#ff65b5",
            width=2.5
        ),
        marker=dict(size=5),
        hovertemplate="%{x}년<br>%{y:.2f}℃<extra></extra>"
    )
)

fig1.update_layout(
    template="plotly_dark",
    height=430,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(
        dtick=10,
        gridcolor="#34445e"
    ),
    yaxis=dict(
        gridcolor="#34445e",
        zeroline=False
    ),
    legend=dict(
        orientation="h",
        y=1.12
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# 9. 미래 기온 예측
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔮 미래 평균기온 예측</div>',
    unsafe_allow_html=True
)

st.write(
    f"선택한 {selected_month}월의 과거 기온 데이터를 학습하여 "
    "미래 평균기온을 예측합니다."
)

target_year = st.number_input(
    "예측하고 싶은 연도를 입력하세요.",
    min_value=2026,
    max_value=2100,
    value=2050,
    step=1
)


# ==========================================
# 10. 학습 데이터 준비
# ==========================================

X = monthly_df[["연도"]].values
y = monthly_df["평균기온(℃)"].values

if len(X) < 5:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()

last_year = int(monthly_df["연도"].max())

if last_year != 2025:
    st.warning(
        f"데이터의 마지막 관측 연도는 {last_year}년입니다. "
        "1907~2025년 데이터가 모두 포함되어 있는지 확인해주세요."
    )

future_years = np.arange(
    last_year + 1,
    int(target_year) + 1
).reshape(-1, 1)


# ==========================================
# 11. 예측 알고리즘 3개
# ==========================================

# 알고리즘 1: 선형 회귀
linear_model = LinearRegression()

linear_model.fit(X, y)


# 알고리즘 2: 다항 회귀 (2차)
polynomial_model = Pipeline([
    ("poly", PolynomialFeatures(degree=2)),
    ("linear", LinearRegression())
])

polynomial_model.fit(X, y)


# 알고리즘 3: 랜덤 포레스트
forest_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=5,
    min_samples_leaf=3,
    random_state=42
)

forest_model.fit(X, y)


models = {
    "선형 회귀": linear_model,
    "다항 회귀": polynomial_model,
    "랜덤 포레스트": forest_model
}

colors = {
    "선형 회귀": "#ff6464",
    "다항 회귀": "#55d6ff",
    "랜덤 포레스트": "#b58aff"
}


# ==========================================
# 12. 미래 예측 그래프
# ==========================================

st.markdown("### 📊 알고리즘별 예측 결과 비교")

fig2 = go.Figure()

# 실제 과거 기온
fig2.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["평균기온(℃)"],
        mode="lines+markers",
        name="실제 관측 기온",
        line=dict(
            color="white",
            width=2.5
        ),
        marker=dict(size=4)
    )
)


# 과거 학습 결과와 미래 예측
for name, model in models.items():

    color = colors[name]

    # 과거 학습 결과
    historical_prediction = model.predict(X)

    fig2.add_trace(
        go.Scatter(
            x=monthly_df["연도"],
            y=historical_prediction,
            mode="lines",
            name=f"{name} 학습 곡선",
            line=dict(
                color=color,
                width=1.5,
                dash="dot"
            ),
            opacity=0.65
        )
    )

    # 미래 예측 결과
    future_prediction = model.predict(future_years)

    # 2025년 실제값에서 미래 예측선 연결
    forecast_x = np.concatenate([
        [last_year],
        future_years.flatten()
    ])

    forecast_y = np.concatenate([
        [monthly_df["평균기온(℃)"].iloc[-1]],
        future_prediction
    ])

    fig2.add_trace(
        go.Scatter(
            x=forecast_x,
            y=forecast_y,
            mode="lines",
            name=f"{name} 미래 예측",
            line=dict(
                color=color,
                width=3
            ),
            hovertemplate="%{x}년<br>%{y:.2f}℃<extra></extra>"
        )
    )


# 예측 시작 지점
fig2.add_vline(
    x=last_year,
    line_dash="dash",
    line_color="#ffffff",
    annotation_text="미래 예측 시작",
    annotation_position="top"
)


fig2.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    xaxis=dict(
        gridcolor="#34445e",
        dtick=10
    ),
    yaxis=dict(
        gridcolor="#34445e"
    ),
    legend=dict(
        orientation="h",
        y=-0.2
    ),
    margin=dict(
        l=20,
        r=20,
        t=40,
        b=90
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==========================================
# 13. 최종 예측값 비교
# ==========================================

st.markdown("### 🎯 최종 예측 결과")

result = []

for name, model in models.items():

    prediction = model.predict(
        np.array([[int(target_year)]])
    )[0]

    result.append({
        "알고리즘": name,
        "예측 연도": f"{int(target_year)}년",
        "예측 평균기온": round(float(prediction), 2)
    })


result_df = pd.DataFrame(result)

result_col1, result_col2, result_col3 = st.columns(3)

for col, row in zip(
    [result_col1, result_col2, result_col3],
    result
):
    with col:
        st.metric(
            row["알고리즘"],
            f"{row['예측 평균기온']:.2f} ℃",
            help=f"{target_year}년 {selected_month}월 예측값"
        )

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 14. 알고리즘 설명
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧠 예측 알고리즘 작동 원리</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)


with col1:
    st.markdown("""
    <div class="info-card">
        <h3 style="color:#ff6464;">🔴 선형 회귀</h3>
        <p>
        과거 기온의 전체적인 증가 또는 감소 추세를
        하나의 직선으로 학습합니다.
        </p>
        <hr>
        <b>작동 방식</b>
        <p>데이터에 가장 잘 맞는 직선을 찾아
        미래까지 연장합니다.</p>
        <b>특징</b>
        <p>단순하고 장기적인 추세 파악에 유리합니다.</p>
        </div>
    """, unsafe_allow_html=True)


with col2:
    st.markdown("""
    <div class="info-card">
        <h3 style="color:#55d6ff;">🔵 다항 회귀</h3>
        <p>
        직선이 아닌 곡선 형태로 과거의
        기온 변화 패턴을 학습합니다.
        </p>
        <hr>
        <b>작동 방식</b>
        <p>2차 방정식을 사용하여
        휘어지는 추세선을 만듭니다.</p>
        <b>특징</b>
        <p>기온 상승이나 하락의 변화 속도를 표현할 수 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)


with col3:
    st.markdown("""
    <div class="info-card">
        <h3 style="color:#b58aff;">🟣 랜덤 포레스트</h3>
        <p>
        여러 개의 의사결정나무를 만들어
        각각의 예측을 종합합니다.
        </p>
        <hr>
        <b>작동 방식</b>
        <p>여러 나무의 예측 결과를 평균 내어
        최종 결과를 계산합니다.</p>
        <b>특징</b>
        <p>복잡한 데이터 패턴을 학습하지만
        학습 범위 밖의 장기 예측에는 한계가 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# 15. 그래프 읽는 방법
# ==========================================

st.markdown("---")

st.markdown("### 💡 그래프 해석 방법")

st.markdown("""
- **흰색 실선:** 실제 관측된 과거 평균기온
- **점선:** 각 알고리즘이 과거 데이터를 학습한 결과
- **빨간색 실선:** 선형 회귀의 미래 예측
- **하늘색 실선:** 다항 회귀의 미래 예측
- **보라색 실선:** 랜덤 포레스트의 미래 예측
- **세로 점선:** 실제 관측과 미래 예측의 경계

예측 결과가 서로 다르다면 각 알고리즘이
과거 데이터를 학습하고 미래로 연장하는 방식이
서로 다르기 때문입니다.
""")

st.caption(
    "※ 이 프로그램의 미래 기온은 통계적 모델을 이용한 추정값입니다. "
    "실제 미래 기후를 확정적으로 예측하는 값은 아닙니다."
)

st.markdown("---")

st.markdown(
    "<center style='color:#8192aa;'>"
    "SEOUL CLIMATE LAB · 1907—2025"
    "</center>",
    unsafe_allow_html=True
)
