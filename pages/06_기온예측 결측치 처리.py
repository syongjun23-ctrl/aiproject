
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="서울 기온 분석 & AI 예측",
    page_icon="🌡️",
    layout="wide"
)


# ==================================================
# 2. 디자인
# ==================================================

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


# ==================================================
# 3. 데이터 불러오기
# ==================================================

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
            "프로젝트 최상위 폴더에 temperature_utf8.csv를 넣어주세요."
        )

    df = None

    for encoding in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:

        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    required_columns = ["일시", "평균기온(℃)"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"'{col}' 열이 없습니다. 현재 열: {list(df.columns)}"
            )

    # 날짜 처리
    df["일시"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        errors="coerce"
    )

    # 기온 처리
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    # 날짜가 잘못된 행만 제거
    df = df.dropna(subset=["일시"]).copy()

    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    df = df[
        (df["연도"] >= 1907) &
        (df["연도"] <= 2025)
    ].copy()

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==================================================
# 4. 제목
# ==================================================

st.markdown(
    '<div class="main-title">🌡️ SEOUL CLIMATE LAB</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '1907~2025 서울 기온 분석 · 결측치 처리 · AI 미래 예측'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# 5. 기본 통계
# ==================================================

c1, c2, c3 = st.columns(3)

c1.metric("📅 분석 기간", "1907~2025")

c2.metric("📊 전체 관측 행", f"{len(df):,}개")

c3.metric(
    "🌡️ 전체 평균기온",
    f"{df['평균기온(℃)'].mean():.2f}℃"
)


# ==================================================
# 6. 월 선택
# ==================================================

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
    "분석할 월을 선택하세요.",
    months,
    index=0
)

selected_month = months.index(selected_month_name) + 1


# ==================================================
# 7. 월별 평균기온 계산
# ==================================================

monthly = (
    df[df["월"] == selected_month]
    .groupby("연도")["평균기온(℃)"]
    .mean()
)

# 1907~2025 전체 연도를 먼저 생성
all_years = pd.Index(
    range(1907, 2026),
    name="연도"
)

# 관측되지 않은 연도는 NaN으로 유지
original_series = monthly.reindex(all_years).astype(float)

# 무한대 값도 결측치로 처리
original_series = original_series.replace(
    [np.inf, -np.inf],
    np.nan
)

missing_count = int(original_series.isna().sum())
observed_count = int(original_series.notna().sum())

if observed_count < 5:
    st.error("선택한 월의 유효한 관측 데이터가 5개 미만입니다.")
    st.stop()


# ==================================================
# 8. 실제 관측 그래프
# ==================================================

st.markdown("### 🌡️ 실제 관측 평균기온")

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="lines+markers",
        name="실제 관측 기온",
        line=dict(color="#ff65b5", width=2.5),
        marker=dict(size=5),
        connectgaps=False
    )
)

fig1.update_layout(
    template="plotly_dark",
    height=420,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    xaxis=dict(
        dtick=10,
        gridcolor="#34445e"
    ),
    yaxis=dict(
        gridcolor="#34445e"
    )
)

st.plotly_chart(fig1, use_container_width=True)


# ==================================================
# 9. 결측치 처리
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧩 02. 결측치 처리 방식 선택</div>',
    unsafe_allow_html=True
)

st.write(
    "관측값이 비어 있는 연도를 어떤 방식으로 처리할지 선택하세요."
)

method_labels = {
    "1. 결측치 제거": "제거",
    "2. 중앙값으로 대체": "중앙값 대체",
    "3. 선형보간법": "선형보간"
}

selected_method = st.radio(
    "결측치 처리 방법",
    list(method_labels.keys()),
    horizontal=True
)


# ==================================================
# 10. 결측치 처리 함수
# ==================================================

def process_missing(series, method):

    result = series.copy().astype(float)

    if method == "1. 결측치 제거":

        # 실제 관측값만 사용
        result = result.dropna()

    elif method == "2. 중앙값으로 대체":

        median_value = result.median()

        result = result.fillna(median_value)

    elif method == "3. 선형보간법":

        result = result.interpolate(
            method="linear",
            limit_direction="both"
        )

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    return result.astype(float)


processed_series = process_missing(
    original_series,
    selected_method
)

if len(processed_series) < 5:
    st.error("결측치 처리 후 학습 가능한 데이터가 부족합니다.")
    st.stop()


# ==================================================
# 11. 결측치 통계
# ==================================================

imputed_count = len(processed_series) - observed_count

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "전체 연도",
    "119년"
)

m2.metric(
    "결측 연도",
    f"{missing_count}년"
)

m3.metric(
    "실제 관측 연도",
    f"{observed_count}년"
)

m4.metric(
    "대체된 연도",
    f"{imputed_count}년"
)

if missing_count == 0:

    st.info(
        "현재 선택한 월에는 결측 연도가 없습니다. "
        "따라서 결측치 처리 방법에 따른 예측 차이가 없을 수 있습니다."
    )

elif selected_method == "1. 결측치 제거":

    st.warning(
        f"{missing_count}개의 결측 연도를 학습에서 제외했습니다."
    )

else:

    st.success(
        f"{missing_count}개의 결측 연도를 선택한 방법으로 대체했습니다."
    )


# ==================================================
# 12. 결측치 처리 전후 비교
# ==================================================

st.markdown("### 📊 결측치 처리 전후 비교")

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="markers",
        name="실제 관측값",
        marker=dict(
            color="white",
            size=7
        )
    )
)

fig2.add_trace(
    go.Scatter(
        x=processed_series.index,
        y=processed_series.values,
        mode="lines+markers",
        name="처리된 데이터",
        line=dict(
            color="#55d6ff",
            width=2
        ),
        marker=dict(size=3)
    )
)

fig2.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    xaxis=dict(dtick=10, gridcolor="#34445e"),
    yaxis=dict(gridcolor="#34445e"),
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a"
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "흰색 점은 원본 관측값이며, 하늘색 선은 결측치 처리 후 학습에 사용하는 데이터입니다."
)


# ==================================================
# 13. 예측 알고리즘 선택
# ==================================================

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
    "비교할 알고리즘을 선택하세요. 여러 개 선택할 수 있습니다.",
    algorithm_names,
    default=algorithm_names
)

if len(selected_algorithms) == 0:
    st.warning("최소 하나의 알고리즘을 선택해주세요.")
    st.stop()


# ==================================================
# 14. 예측 연도
# ==================================================

target_year = st.number_input(
    "🔮 예측하고 싶은 연도",
    min_value=2026,
    max_value=2100,
    value=2050,
    step=1
)


# ==================================================
# 15. 알고리즘 생성
# ==================================================

def create_model(name):

    if name == "선형 회귀":

        return LinearRegression()

    elif name == "다항 회귀":

        return make_pipeline(
            PolynomialFeatures(degree=2),
            LinearRegression()
        )

    elif name == "랜덤 포레스트":

        return RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1
        )


algorithm_colors = {
    "선형 회귀": "#ff6464",
    "다항 회귀": "#55d6ff",
    "랜덤 포레스트": "#b58aff"
}

method_dash = {
    "1. 결측치 제거": "solid",
    "2. 중앙값으로 대체": "dash",
    "3. 선형보간법": "dot"
}


# ==================================================
# 16. 모델 학습 및 예측 공통 함수
# ==================================================

def train_and_predict(series, algorithm, target):

    # 데이터 검사
    series = series.dropna().astype(float)

    if len(series) < 5:
        raise ValueError("학습 데이터가 부족합니다.")

    if not np.isfinite(series.values).all():
        raise ValueError("학습 데이터에 유효하지 않은 값이 있습니다.")

    # 연도를 기준 연도에서 빼서 수치 안정성 확보
    years = series.index.to_numpy(dtype=float)

    X = (years - 1907).reshape(-1, 1)
    y = series.to_numpy(dtype=float)

    # 미래 연도
    future_years = np.arange(
        2026,
        int(target) + 1
    )

    future_X = (future_years - 1907).reshape(-1, 1)

    # 모델 생성
    model = create_model(algorithm)

    # 학습
    model.fit(X, y)

    # 미래 예측
    predictions = model.predict(future_X)

    # 마지막 학습 연도의 예측값
    last_year = int(years[-1])

    last_X = np.array([
        [last_year - 1907]
    ])

    last_prediction = float(
        model.predict(last_X)[0]
    )

    # 목표 연도 예측값
    target_prediction = float(predictions[-1])

    if not np.isfinite(target_prediction):
        raise ValueError("예측 결과가 유효하지 않습니다.")

    return {
        "model": model,
        "future_years": future_years,
        "predictions": predictions,
        "last_year": last_year,
        "last_prediction": last_prediction,
        "target_prediction": target_prediction
    }


# ==================================================
# 17. 선택한 처리 방식으로 예측
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔮 04. 선택한 조건으로 미래 예측</div>',
    unsafe_allow_html=True
)

st.write(
    f"결측치 처리: **{selected_method}**  |  "
    f"예측 대상: **{target_year}년 {selected_month}월**"
)

fig3 = go.Figure()

# 실제 관측 데이터
fig3.add_trace(
    go.Scatter(
        x=original_series.dropna().index,
        y=original_series.dropna().values,
        mode="lines+markers",
        name="실제 관측값",
        line=dict(color="white", width=2.5),
        marker=dict(size=4)
    )
)

# 처리된 데이터
fig3.add_trace(
    go.Scatter(
        x=processed_series.index,
        y=processed_series.values,
        mode="markers",
        name="학습용 처리 데이터",
        marker=dict(
            color="#8b9bb4",
            size=5,
            symbol="circle-open"
        )
    )
)

prediction_results = []
main_results = {}

for name in selected_algorithms:

    try:

        result = train_and_predict(
            processed_series,
            name,
            target_year
        )

        main_results[name] = result

        # 학습 구간
        historical_years = processed_series.index.to_numpy()
        historical_X = (
            historical_years - 1907
        ).reshape(-1, 1)

        historical_predictions = result["model"].predict(
            historical_X
        )

        fig3.add_trace(
            go.Scatter(
                x=historical_years,
                y=historical_predictions,
                mode="lines",
                name=f"{name} 학습 곡선",
                line=dict(
                    color=algorithm_colors[name],
                    width=1.5,
                    dash="dot"
                ),
                opacity=0.65
            )
        )

        # 미래 예측선
        forecast_x = np.concatenate([
            [result["last_year"]],
            result["future_years"]
        ])

        forecast_y = np.concatenate([
            [result["last_prediction"]],
            result["predictions"]
        ])

        fig3.add_trace(
            go.Scatter(
                x=forecast_x,
                y=forecast_y,
                mode="lines",
                name=f"{name} 미래 예측",
                line=dict(
                    color=algorithm_colors[name],
                    width=3
                ),
                hovertemplate="%{x}년<br>%{y:.2f}℃<extra></extra>"
            )
        )

        prediction_results.append({
            "알고리즘": name,
            "예측 연도": f"{target_year}년",
            "예측 평균기온(℃)": round(
                result["target_prediction"], 2
            )
        })

    except Exception as e:

        st.error(f"{name} 학습 오류: {e}")


if not prediction_results:
    st.error("예측에 성공한 알고리즘이 없습니다.")
    st.stop()


fig3.add_vline(
    x=2025,
    line_dash="dash",
    line_color="white",
    annotation_text="2025년 / 예측 구간"
)

fig3.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    xaxis=dict(dtick=10, gridcolor="#34445e"),
    yaxis=dict(gridcolor="#34445e"),
    legend=dict(
        orientation="h",
        y=-0.25
    ),
    margin=dict(b=100)
)

st.plotly_chart(fig3, use_container_width=True)


# ==================================================
# 18. 선택한 조건의 최종 예측값
# ==================================================

st.markdown("### 🎯 최종 예측 결과")

result_df = pd.DataFrame(prediction_results)

result_columns = st.columns(len(prediction_results))

for col, row in zip(result_columns, prediction_results):

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


# ==================================================
# 19. 모든 결측치 처리 방식 비교
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔬 05. 결측치 처리 방식별 예측 비교</div>',
    unsafe_allow_html=True
)

st.write(
    "현재 선택한 알고리즘을 유지한 상태에서 "
    "결측치 처리 방법만 바꾸어 결과를 비교합니다."
)

all_methods = [
    "1. 결측치 제거",
    "2. 중앙값으로 대체",
    "3. 선형보간법"
]

comparison_results = []

fig4 = go.Figure()

# 알고리즘별 / 결측치 처리 방식별 예측
for method in all_methods:

    method_series = process_missing(
        original_series,
        method
    )

    if len(method_series) < 5:
        continue

    for name in selected_algorithms:

        try:

            result = train_and_predict(
                method_series,
                name,
                target_year
            )

            future_years = result["future_years"]
            predictions = result["predictions"]

            # 그래프 범례용 이름
            trace_name = f"{name} / {method}"

            fig4.add_trace(
                go.Scatter(
                    x=future_years,
                    y=predictions,
                    mode="lines",
                    name=trace_name,
                    line=dict(
                        color=algorithm_colors[name],
                        width=2.5,
                        dash=method_dash[method]
                    ),
                    hovertemplate=(
                        "%{x}년<br>"
                        "%{y:.2f}℃"
                        "<extra>" + trace_name + "</extra>"
                    )
                )
            )

            comparison_results.append({
                "결측치 처리": method,
                "알고리즘": name,
                "예측 평균기온(℃)": round(
                    result["target_prediction"], 2
                )
            })

        except Exception as e:

            st.warning(
                f"{method} / {name} 비교 중 오류: {e}"
            )


fig4.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_title="예측 연도",
    yaxis_title="예측 평균기온 (℃)",
    hovermode="x unified",
    plot_bgcolor="#17243a",
    paper_bgcolor="#17243a",
    xaxis=dict(
        dtick=5,
        gridcolor="#34445e"
    ),
    yaxis=dict(
        gridcolor="#34445e"
    ),
    legend=dict(
        orientation="h",
        y=-0.3
    ),
    margin=dict(b=130)
)

st.plotly_chart(fig4, use_container_width=True)


# ==================================================
# 20. 9가지 조합의 최종값 비교
# ==================================================

st.markdown("### 📋 결측치 처리 × 알고리즘 결과표")

comparison_df = pd.DataFrame(comparison_results)

if not comparison_df.empty:

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # 처리 방식별 예측값 차이
    pivot_df = comparison_df.pivot(
        index="결측치 처리",
        columns="알고리즘",
        values="예측 평균기온(℃)"
    )

    st.markdown("### 📊 목표 연도 예측값 비교")

    st.dataframe(
        pivot_df,
        use_container_width=True
    )

    st.caption(
        f"위 결과는 {target_year}년 {selected_month}월의 예측값입니다."
    )

else:

    st.warning("비교 가능한 예측 결과가 없습니다.")


# ==================================================
# 21. 알고리즘 설명
# ==================================================

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

    과거 기온의 전체적인 증가 또는 감소 추세를
    직선으로 학습합니다.

    <hr>

    <b>작동 원리</b>

    데이터와 가장 잘 맞는 직선을 찾아
    미래까지 연장합니다.

    <b>그래프 특징</b>

    일정한 기울기를 가진 직선 형태입니다.
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="info-card">
    <h3 style="color:#55d6ff;">🔵 다항 회귀</h3>

    과거 기온의 곡선 형태를 학습합니다.

    <hr>

    <b>작동 원리</b>

    2차 방정식으로 변화하는 추세를 표현합니다.

    <b>그래프 특징</b>

    상승 또는 하락 속도가 변하는 곡선입니다.
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="info-card">
    <h3 style="color:#b58aff;">🟣 랜덤 포레스트</h3>

    여러 개의 의사결정나무를 이용합니다.

    <hr>

    <b>작동 원리</b>

    여러 나무가 예측한 결과를 평균 내어 계산합니다.

    <b>그래프 특징</b>

    학습 범위 밖에서는 예측값이 평평해지는 경향이 있습니다.
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# 22. 결측치 처리 방법 설명
# ==================================================

st.markdown(
    '<div class="section-title">🧩 07. 결측치 처리 방법</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-card">
    <h3>1️⃣ 결측치 제거</h3>

    비어 있는 연도를 학습에서 제외합니다.

    <hr>

    <b>장점</b>

    실제 관측값만 학습합니다.

    <b>단점</b>

    학습 데이터가 감소합니다.
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="info-card">
    <h3>2️⃣ 중앙값 대체</h3>

    관측값의 중앙값으로 빈 데이터를 채웁니다.

    <hr>

    <b>장점</b>

    극단적인 값의 영향을 적게 받습니다.

    <b>단점</b>

    연도별 변화 추세를 반영하지 못합니다.
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="info-card">
    <h3>3️⃣ 선형보간법</h3>

    앞뒤 연도의 값으로 중간 기온을 추정합니다.

    <hr>

    <b>장점</b>

    시간에 따른 변화를 반영합니다.

    <b>단점</b>

    급격한 변화는 반영하기 어렵습니다.
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# 23. 마무리
# ==================================================

st.markdown("---")

st.info(
    "💡 결측치 처리 방식과 예측 알고리즘을 바꿔가며 "
    "미래 평균기온이 어떻게 달라지는지 비교해 보세요."
)

st.caption(
    "SEOUL CLIMATE LAB | 1907—2025 | "
    "통계적 예측 결과이며 실제 미래 기온을 보장하지 않습니다."
)
