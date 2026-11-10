
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
    page_title="서울 기온 분석 & AI 예측",
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
    background: linear-gradient(90deg, #69d5ff, #bd9cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    color: #aab9d0;
    margin-bottom: 25px;
}

.info-card {
    background: #202f46;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #34445e;
    margin-bottom: 12px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
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

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. CSV 불러오기
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
            "CSV 파일을 프로젝트 최상위 폴더에 넣어주세요."
        )

    df = None

    for encoding in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:

        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 인코딩을 확인해주세요.")

    required = ["일시", "평균기온(℃)"]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"CSV에 {col} 열이 없습니다."
            )

    df["일시"] = pd.to_datetime(
        df["일시"],
        errors="coerce"
    )

    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    df = df.dropna(subset=["일시"])

    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    df = df[
        (df["연도"] >= 1907) &
        (df["연도"] <= 2025)
    ]

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 4. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🌡️ SEOUL CLIMATE LAB</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '1907~2025 서울 기온 분석 · 결측치 처리 · 미래 예측'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# 5. 기본 통계
# ==========================================

c1, c2, c3 = st.columns(3)

c1.metric("📅 분석 기간", "1907~2025")

c2.metric("📊 원본 데이터", f"{len(df):,}개")

c3.metric(
    "🌡️ 전체 평균기온",
    f"{df['평균기온(℃)'].mean():.2f}℃"
)


# ==========================================
# 6. 월 선택
# ==========================================

st.markdown(
    '<div class="section-title">📈 01. 월별 기온 분석</div>',
    unsafe_allow_html=True
)

months = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

selected_month_name = st.selectbox(
    "분석할 월",
    months
)

selected_month = months.index(
    selected_month_name
) + 1


# ==========================================
# 7. 월별 평균기온 계산
# ==========================================

monthly = (
    df[df["월"] == selected_month]
    .groupby("연도")["평균기온(℃)"]
    .mean()
)

# 1907~2025년 전체 연도 생성
all_years = pd.Index(
    range(1907, 2026),
    name="연도"
)

original_series = monthly.reindex(all_years)

missing_count = int(
    original_series.isna().sum()
)

observed_count = int(
    original_series.notna().sum()
)

if observed_count < 5:
    st.error("선택한 월의 관측 데이터가 너무 적습니다.")
    st.stop()


# ==========================================
# 8. 실제 관측 그래프
# ==========================================

st.markdown("### 실제 관측 기온")

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(color="#ff65b5", width=2),
        marker=dict(size=4)
    )
)

fig1.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    xaxis=dict(dtick=10, gridcolor="#34445e"),
    yaxis=dict(gridcolor="#34445e"),
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    hovermode="x unified"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# 9. 결측치 처리 방식 선택
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧩 02. 결측치 처리 방식 선택</div>',
    unsafe_allow_html=True
)

st.write(
    "데이터가 비어 있는 연도를 어떤 방법으로 처리할지 선택하세요."
)

missing_method = st.radio(
    "결측치 처리 방법",
    [
        "1. 결측치 제거",
        "2. 중앙값으로 대체",
        "3. 선형보간법"
    ],
    horizontal=True
)


# ==========================================
# 10. 결측치 처리 함수
# ==========================================

def process_missing(series, method):

    result = series.copy()

    if method == "1. 결측치 제거":

        result = result.dropna()

    elif method == "2. 중앙값으로 대체":

        median_value = result.median()

        result = result.fillna(median_value)

    elif method == "3. 선형보간법":

        result = result.interpolate(
            method="linear",
            limit_direction="both"
        )

    return result.astype(float)


processed_series = process_missing(
    original_series,
    missing_method
)


# ==========================================
# 11. 결측치 처리 통계
# ==========================================

filled_count = int(
    processed_series.notna().sum() - observed_count
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "전체 연도",
    "119년"
)

m2.metric(
    "결측 연도",
    f"{missing_count}년"
)

m3.metric(
    "처리된 데이터",
    f"{len(processed_series)}개"
)


if missing_count == 0:
    st.info(
        "선택한 월에는 결측 연도가 없습니다. "
        "처리 방법을 바꿔도 결과가 동일할 수 있습니다."
    )


# ==========================================
# 12. 결측치 처리 전후 비교 그래프
# ==========================================

st.markdown("### 결측치 처리 전후 비교")

fig2 = go.Figure()

# 원본 관측값
fig2.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="markers",
        name="원본 관측값",
        marker=dict(
            color="white",
            size=6
        )
    )
)

# 처리된 전체 값
fig2.add_trace(
    go.Scatter(
        x=processed_series.index,
        y=processed_series.values,
        mode="lines",
        name="결측치 처리 결과",
        line=dict(
            color="#55d6ff",
            width=2.5
        )
    )
)

fig2.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    xaxis=dict(dtick=10, gridcolor="#34445e"),
    yaxis=dict(gridcolor="#34445e"),
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    hovermode="x unified"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.caption(
    "흰색 점은 실제 관측값, 하늘색 선은 선택한 방법으로 "
    "결측치를 처리한 결과입니다."
)


# ==========================================
# 13. 알고리즘 선택
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🤖 03. 예측 알고리즘 선택</div>',
    unsafe_allow_html=True
)

algorithm_names = [
    "선형 회귀",
    "다항 회귀",
    "랜덤 포레스트"
]

selected_algorithms = st.multiselect(
    "비교할 알고리즘을 선택하세요.",
    algorithm_names,
    default=algorithm_names
)

if not selected_algorithms:
    st.warning("최소 하나의 알고리즘을 선택해주세요.")
    st.stop()


# ==========================================
# 14. 예측 연도
# ==========================================

target_year = st.number_input(
    "예측하고 싶은 연도",
    min_value=2026,
    max_value=2100,
    value=2050,
    step=1
)


# ==========================================
# 15. 모델 생성 함수
# ==========================================

def create_model(name):

    if name == "선형 회귀":

        return LinearRegression()

    elif name == "다항 회귀":

        return Pipeline([
            (
                "poly",
                PolynomialFeatures(degree=2)
            ),
            (
                "linear",
                LinearRegression()
            )
        ])

    elif name == "랜덤 포레스트":

        return RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=3,
            random_state=42
        )


colors = {
    "선형 회귀": "#ff6464",
    "다항 회귀": "#55d6ff",
    "랜덤 포레스트": "#b58aff"
}


# ==========================================
# 16. 선택한 결측치 처리 방식으로 예측
# ==========================================

X = processed_series.index.to_numpy().reshape(-1, 1)
y = processed_series.to_numpy()

future_years = np.arange(
    2026,
    int(target_year) + 1
).reshape(-1, 1)

if len(X) < 5:
    st.error("학습할 데이터가 부족합니다.")
    st.stop()


st.markdown("---")

st.markdown(
    '<div class="section-title">🔮 04. 미래 기온 예측</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"**현재 결측치 처리:** {missing_method}  |  "
    f"**예측 연도:** {target_year}년"
)


# ==========================================
# 17. 선택한 알고리즘 예측 그래프
# ==========================================

fig3 = go.Figure()

# 실제 관측값
fig3.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="lines+markers",
        name="실제 관측값",
        line=dict(color="white", width=2)
    )
)

# 처리된 데이터
fig3.add_trace(
    go.Scatter(
        x=processed_series.index,
        y=processed_series.values,
        mode="lines",
        name="결측치 처리 데이터",
        line=dict(color="#8b9bb4", width=1.5, dash="dot")
    )
)

prediction_results = []

for name in selected_algorithms:

    model = create_model(name)

    model.fit(X, y)

    # 과거 학습 결과
    historical = model.predict(X)

    fig3.add_trace(
        go.Scatter(
            x=processed_series.index,
            y=historical,
            mode="lines",
            name=f"{name} 학습 결과",
            line=dict(
                color=colors[name],
                width=1.5,
                dash="dot"
            )
        )
    )

    # 미래 예측
    future_prediction = model.predict(future_years)

    forecast_x = np.concatenate([
        [2025],
        future_years.flatten()
    ])

    forecast_y = np.concatenate([
        [float(processed_series.loc[2025])],
        future_prediction
    ])

    fig3.add_trace(
        go.Scatter(
            x=forecast_x,
            y=forecast_y,
            mode="lines",
            name=f"{name} 미래 예측",
            line=dict(
                color=colors[name],
                width=3
            )
        )
    )

    final_value = model.predict(
        np.array([[int(target_year)]])
    )[0]

    prediction_results.append({
        "알고리즘": name,
        "예측 연도": f"{target_year}년",
        "예측 평균기온(℃)": round(float(final_value), 2)
    })


fig3.add_vline(
    x=2025,
    line_dash="dash",
    line_color="white",
    annotation_text="미래 예측 시작"
)

fig3.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    xaxis=dict(
        dtick=10,
        gridcolor="#34445e"
    ),
    yaxis=dict(
        gridcolor="#34445e"
    ),
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=-0.25
    ),
    margin=dict(b=100)
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==========================================
# 18. 최종 예측 결과
# ==========================================

st.markdown("### 🎯 선택한 방법의 최종 예측값")

result_df = pd.DataFrame(prediction_results)

cols = st.columns(len(prediction_results))

for col, row in zip(
    cols,
    prediction_results
):

    with col:

        st.metric(
            row["알고리즘"],
            f"{row['예측 평균기온(℃)']:.2f}℃"
        )

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 19. 결측치 처리 방법별 예측 비교
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔬 05. 결측치 처리 방법에 따른 예측 차이</div>',
    unsafe_allow_html=True
)

st.write(
    "동일한 알고리즘을 사용하더라도 결측치를 처리하는 방식에 "
    "따라 예측 결과가 어떻게 달라지는지 비교합니다."
)

all_methods = [
    "1. 결측치 제거",
    "2. 중앙값으로 대체",
    "3. 선형보간법"
]

comparison_rows = []

fig4 = go.Figure()

# 각 처리 방법과 선택한 알고리즘 조합 비교
for method in all_methods:

    method_series = process_missing(
        original_series,
        method
    )

    method_X = method_series.index.to_numpy().reshape(-1, 1)
    method_y = method_series.to_numpy()

    for name in selected_algorithms:

        model = create_model(name)

        model.fit(method_X, method_y)

        predicted = float(
            model.predict(
                np.array([[int(target_year)]])
            )[0]
        )

        comparison_rows.append({
            "결측치 처리": method,
            "알고리즘": name,
            "예측 평균기온(℃)": round(predicted, 2)
        })

        fig4.add_trace(
            go.Scatter(
                x=[method],
                y=[predicted],
                mode="markers+text",
                name=f"{method} - {name}",
                text=[f"{predicted:.2f}℃"],
                textposition="top center",
                marker=dict(
                    size=13,
                    color=colors[name]
                ),
                legendgroup=name
            )
        )


comparison_df = pd.DataFrame(comparison_rows)

fig4.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="결측치 처리 방식",
    yaxis_title=f"{target_year}년 예측 평균기온 (℃)",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    hovermode="closest",
    xaxis=dict(
        gridcolor="#34445e"
    ),
    yaxis=dict(
        gridcolor="#34445e"
    ),
    legend=dict(
        orientation="h",
        y=-0.3
    ),
    margin=dict(b=110)
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("### 📋 결측치 처리별 예측 결과표")

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 20. 알고리즘 설명
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧠 06. 예측 알고리즘 작동 원리</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-card">
    <h3 style="color:#ff6464;">🔴 선형 회귀</h3>
    과거 기온의 전체적인 추세를 직선으로 학습합니다.

    <hr>

    <b>작동 방식</b>

    데이터에 가장 잘 맞는 직선을 찾아 미래까지 연장합니다.

    <b>특징</b>

    단순하고 전체적인 증가 및 감소 추세를 파악하기 쉽습니다.
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="info-card">
    <h3 style="color:#55d6ff;">🔵 다항 회귀</h3>
    과거 기온의 곡선 형태를 학습합니다.

    <hr>

    <b>작동 방식</b>

    2차 방정식으로 휘어지는 추세선을 만듭니다.

    <b>특징</b>

    기온 변화의 가속 및 감속 추세를 표현할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="info-card">
    <h3 style="color:#b58aff;">🟣 랜덤 포레스트</h3>
    여러 개의 의사결정나무를 활용합니다.

    <hr>

    <b>작동 방식</b>

    여러 나무의 예측값을 평균 내어 결과를 계산합니다.

    <b>특징</b>

    복잡한 데이터 패턴을 학습할 수 있지만 장기 외삽에는 한계가 있습니다.
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 21. 결측치 처리 설명
# ==========================================

st.markdown(
    '<div class="section-title">🧩 결측치 처리 방법의 차이</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
    <h3>1️⃣ 결측치 제거</h3>
    비어 있는 연도 데이터를 학습에서 제외합니다.

    <b>장점</b>
    <p>실제로 관측된 값만 사용합니다.</p>

    <b>단점</b>
    <p>학습 데이터가 줄어듭니다.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
    <h3>2️⃣ 중앙값 대체</h3>
    전체 관측값의 중앙값으로 빈 데이터를 채웁니다.

    <b>장점</b>
    <p>이상치의 영향을 평균보다 적게 받습니다.</p>

    <b>단점</b>
    <p>실제 연도별 기온 변화를 반영하지 못합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
    <h3>3️⃣ 선형보간법</h3>
    앞뒤 연도의 기온을 이용하여 중간값을 추정합니다.

    <b>장점</b>
    <p>시간의 흐름에 따른 변화를 반영합니다.</p>

    <b>단점</b>
    <p>급격한 기온 변화는 정확히 반영하지 못할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 22. 마무리
# ==========================================

st.markdown("---")

st.info(
    "💡 결측치 처리 방법과 예측 알고리즘을 변경하면서 "
    "미래 기온 예측값이 어떻게 달라지는지 비교해 보세요."
)

st.caption(
    "SEOUL CLIMATE LAB | 1907—2025 | "
    "통계적 추정 결과이며 실제 미래 기온과 다를 수 있습니다."
)

        
