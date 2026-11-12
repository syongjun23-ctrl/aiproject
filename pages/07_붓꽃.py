
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.inspection import permutation_importance


# =========================================================
# 1. 페이지 설정 및 디자인
# =========================================================

st.set_page_config(
    page_title="Iris AI 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f5ff, #edf5ff);
}
.main .block-container {
    max-width: 1400px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #7967e8, #e879b9);
    padding: 32px;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}
.hero h1, .hero p {
    color: white;
}
.section-title {
    font-size: 25px;
    font-weight: 800;
    color: #715ed1;
    margin-top: 25px;
    margin-bottom: 15px;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #eee8ff;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🌸 IRIS AI CLASSIFIER</h1>
    <p>세 가지 인공지능이 동시에 분석하는 붓꽃 품종 예측</p>
    <p>측정값을 입력하면 세 알고리즘이 자동으로 예측합니다.</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 2. CSV 파일 불러오기
# =========================================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    possible_paths = [
        current_dir.parent / "Iris.csv",
        current_dir / "Iris.csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "Iris.csv 파일을 찾을 수 없습니다. "
            "프로젝트 최상위 폴더에 Iris.csv를 넣어주세요."
        )

    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

    if len(data.columns) != 5:
        raise ValueError(
            "CSV 파일에는 꽃받침 길이, 꽃받침 너비, "
            "꽃잎 길이, 꽃잎 너비, 품종의 5개 열이 필요합니다."
        )

    data.columns = [
        "꽃받침길이",
        "꽃받침너비",
        "꽃잎길이",
        "꽃잎너비",
        "품종"
    ]

    numeric_columns = [
        "꽃받침길이",
        "꽃받침너비",
        "꽃잎길이",
        "꽃잎너비"
    ]

    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["품종"] = data["품종"].astype(str).str.strip()

    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(subset=numeric_columns + ["품종"])

    return data.reset_index(drop=True)


try:
    df = load_data()
except Exception as error:
    st.error(f"데이터 불러오기 실패: {error}")
    st.stop()


# =========================================================
# 3. 데이터 준비
# =========================================================

FEATURES = ["꽃잎길이", "꽃잎너비"]

X = df[FEATURES]
y = df["품종"]

if y.nunique() < 2 or y.value_counts().min() < 2:
    st.error("각 품종별 데이터가 최소 2개 이상 필요합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================================================
# 4. 세 가지 알고리즘을 자동으로 생성하는 함수
# =========================================================

def create_all_models():

    knn_k = min(5, len(X_train))

    # 중요: 세 알고리즘은 항상 전부 생성됩니다.
    # 사용자가 선택하는 기능은 존재하지 않습니다.

    all_models = {
        "랜덤 포레스트": RandomForestClassifier(
            n_estimators=300,
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        ),

        "KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(
                n_neighbors=knn_k,
                weights="distance"
            ))
        ]),

        "SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                probability=True,
                random_state=42
            ))
        ])
    }

    return all_models


# =========================================================
# 5. 세 알고리즘 동시 학습 및 정확도 측정
# =========================================================

evaluation_models = create_all_models()

accuracies = {}

for algorithm_name, algorithm_model in evaluation_models.items():

    algorithm_model.fit(X_train, y_train)

    test_prediction = algorithm_model.predict(X_test)

    accuracies[algorithm_name] = accuracy_score(
        y_test,
        test_prediction
    )


# =========================================================
# 6. 알고리즘 설명
# =========================================================

st.markdown(
    '<div class="section-title">🧠 사용 알고리즘</div>',
    unsafe_allow_html=True
)

info_columns = st.columns(3)

algorithm_descriptions = [
    (
        "🌳 랜덤 포레스트",
        "여러 의사결정나무의 예측을 모아 다수결로 품종을 결정합니다."
    ),
    (
        "📍 KNN",
        "입력값과 가까운 기존 데이터 5개를 찾아 주변 품종을 기준으로 예측합니다."
    ),
    (
        "⚖️ SVM",
        "품종을 가장 잘 구분하는 경계선을 학습하여 새로운 데이터를 분류합니다."
    )
]

for column, (title, description) in zip(
    info_columns,
    algorithm_descriptions
):
    with column:
        st.markdown(f"### {title}")
        st.write(description)


# =========================================================
# 7. 데이터 현황
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">📊 데이터 분석 현황</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{y.nunique()}종")
c3.metric("동시 실행 알고리즘", "3개")
c4.metric("테스트 데이터", f"{len(X_test)}개")


# =========================================================
# 8. 알고리즘 정확도 비교
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🏆 알고리즘 정확도 비교</div>',
    unsafe_allow_html=True
)

accuracy_df = pd.DataFrame({
    "알고리즘": list(accuracies.keys()),
    "테스트 정확도": [
        accuracies[name] * 100
        for name in accuracies
    ]
})

accuracy_fig = go.Figure()

accuracy_fig.add_trace(go.Bar(
    x=accuracy_df["알고리즘"],
    y=accuracy_df["테스트 정확도"],
    marker_color=["#8D78EF", "#36A2EB", "#E879B9"],
    text=[
        f"{value:.1f}%"
        for value in accuracy_df["테스트 정확도"]
    ],
    textposition="outside"
))

accuracy_fig.update_layout(
    title="세 알고리즘의 테스트 정확도",
    template="plotly_white",
    height=370,
    yaxis_title="정확도 (%)",
    yaxis=dict(range=[0, 115]),
    showlegend=False
)

st.plotly_chart(accuracy_fig, use_container_width=True)

st.caption(
    "세 알고리즘 모두 동일한 학습 데이터와 테스트 데이터로 평가합니다."
)


# =========================================================
# 9. 사용자 입력
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🎯 붓꽃 측정값 입력</div>',
    unsafe_allow_html=True
)

length_min = float(X["꽃잎길이"].min())
length_max = float(X["꽃잎길이"].max())
width_min = float(X["꽃잎너비"].min())
width_max = float(X["꽃잎너비"].max())

left, right = st.columns(2)

with left:
    st.markdown("### 🌸 꽃잎 길이")
    st.caption(f"입력 범위: {length_min:.2f} ~ {length_max:.2f} cm")

    petal_length = st.slider(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=float(np.clip(5.0, length_min, length_max)),
        step=0.1,
        key="petal_length"
    )

with right:
    st.markdown("### 🌼 꽃잎 너비")
    st.caption(f"입력 범위: {width_min:.2f} ~ {width_max:.2f} cm")

    petal_width = st.slider(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(np.clip(1.8, width_min, width_max)),
        step=0.1,
        key="petal_width"
    )

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=FEATURES
)


# =========================================================
# 10. 세 알고리즘 최종 모델 학습
# =========================================================

# 평가용 모델과 별개로 전체 데이터를 학습한 예측용 모델을 만듭니다.
# 세 알고리즘 모두 자동으로 학습됩니다.

prediction_models = create_all_models()

for algorithm_name, algorithm_model in prediction_models.items():
    algorithm_model.fit(X, y)


# =========================================================
# 11. 세 알고리즘 동시 예측
# =========================================================

prediction_rows = []
probability_rows = []

for algorithm_name, algorithm_model in prediction_models.items():

    # 모든 알고리즘에서 predict를 실행합니다.
    predicted_species = algorithm_model.predict(input_data)[0]

    # 모든 알고리즘에서 predict_proba를 실행합니다.
    probabilities = algorithm_model.predict_proba(input_data)[0]

    model_classes = algorithm_model.classes_

    predicted_index = list(model_classes).index(predicted_species)

    confidence = probabilities[predicted_index] * 100

    prediction_rows.append({
        "알고리즘": algorithm_name,
        "예측 품종": predicted_species,
        "예측 확률": confidence,
        "테스트 정확도": accuracies[algorithm_name] * 100
    })

    probability_row = {
        "알고리즘": algorithm_name
    }

    for species, probability in zip(model_classes, probabilities):
        probability_row[species] = probability * 100

    probability_rows.append(probability_row)


# 세 알고리즘 결과를 하나의 표로 합칩니다.
result_table = pd.DataFrame(prediction_rows)

probability_table = pd.DataFrame(probability_rows)


# =========================================================
# 12. 통합 예측 결과표
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🏆 세 알고리즘 통합 예측 결과</div>',
    unsafe_allow_html=True
)

st.write(
    f"입력값: 꽃잎 길이 {petal_length:.1f} cm / "
    f"꽃잎 너비 {petal_width:.1f} cm"
)

# 알고리즘을 선택하는 메뉴 없이 세 결과를 한 표에 출력합니다.
st.dataframe(
    result_table.style.format({
        "예측 확률": "{:.1f}%",
        "테스트 정확도": "{:.1f}%"
    }).background_gradient(
        subset=["예측 확률"],
        cmap="Purples"
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 13. 다수결 결과
# =========================================================

st.markdown(
    '<div class="section-title">🗳️ 세 알고리즘의 최종 투표</div>',
    unsafe_allow_html=True
)

vote_counts = result_table["예측 품종"].value_counts()

max_votes = vote_counts.max()
winners = vote_counts[vote_counts == max_votes].index.tolist()

vote_table = pd.DataFrame({
    "품종": y.unique()
})

vote_table["투표 수"] = (
    vote_table["품종"]
    .map(vote_counts)
    .fillna(0)
    .astype(int)
)

vote_table = vote_table.sort_values(
    "투표 수",
    ascending=False
)

if max_votes >= 2:
    st.success(
        f"🌸 다수결 결과: {', '.join(winners)} "
        f"(3개 중 {max_votes}개 알고리즘이 선택)"
    )
else:
    st.warning(
        "세 알고리즘의 예측 결과가 모두 다릅니다. "
        "아래 결과표에서 각각의 판단을 확인하세요."
    )

st.dataframe(
    vote_table,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 14. 품종별 예측 확률 비교
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">📈 품종별 예측 확률 비교</div>',
    unsafe_allow_html=True
)

species_list = list(y.unique())

species_colors = {
    species: color
    for species, color in zip(
        species_list,
        ["#FF6384", "#36A2EB", "#42C98A"]
    )
}

probability_fig = go.Figure()

for species in species_list:

    if species not in probability_table.columns:
        continue

    probability_fig.add_trace(go.Bar(
        x=probability_table["알고리즘"],
        y=probability_table[species],
        name=species,
        marker_color=species_colors[species],
        text=[
            f"{value:.1f}%"
            for value in probability_table[species]
        ],
        textposition="inside"
    ))

probability_fig.update_layout(
    barmode="group",
    template="plotly_white",
    height=420,
    title="알고리즘별 품종 예측 확률",
    yaxis_title="예측 확률 (%)",
    yaxis=dict(range=[0, 110])
)

st.plotly_chart(
    probability_fig,
    use_container_width=True
)

st.caption(
    "예측 확률은 각 모델이 계산한 확률이며 실제 정답을 보장하지 않습니다."
)


# =========================================================
# 15. 세 알고리즘 분류 영역 비교
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🌈 세 알고리즘 분류 영역 비교</div>',
    unsafe_allow_html=True
)

st.write(
    "동일한 꽃잎 측정값을 기준으로 세 알고리즘이 "
    "각 품종을 어떻게 구분하는지 비교합니다."
)

class_names = list(prediction_models["랜덤 포레스트"].classes_)

class_to_number = {
    species: index
    for index, species in enumerate(class_names)
}

x_min = length_min - 0.2
x_max = length_max + 0.2
y_min = width_min - 0.1
y_max = width_max + 0.1

grid_x = np.linspace(x_min, x_max, 150)
grid_y = np.linspace(y_min, y_max, 150)

xx, yy = np.meshgrid(grid_x, grid_y)

grid_data = pd.DataFrame({
    "꽃잎길이": xx.ravel(),
    "꽃잎너비": yy.ravel()
})

colorscale = []

for index, species in enumerate(class_names):
    start = index / len(class_names)
    end = (index + 1) / len(class_names)

    colorscale.append([start, species_colors[species]])
    colorscale.append([end, species_colors[species]])

fig = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=[
        "🌳 랜덤 포레스트",
        "📍 KNN",
        "⚖️ SVM"
    ],
    horizontal_spacing=0.07
)

rainbow_colors = [
    "#FF0000",
    "#FF7F00",
    "#FFFF00",
    "#00CC44",
    "#0099FF",
    "#3333FF",
    "#9400D3"
]

for column_number, (algorithm_name, algorithm_model) in enumerate(
    prediction_models.items(),
    start=1
):

    grid_predictions = algorithm_model.predict(grid_data)

    z = np.array([
        class_to_number[value]
        for value in grid_predictions
    ]).reshape(xx.shape)

    fig.add_trace(
        go.Contour(
            x=grid_x,
            y=grid_y,
            z=z,
            colorscale=colorscale,
            opacity=0.25,
            showscale=False,
            contours=dict(
                coloring="fill",
                showlines=True,
                start=0,
                end=len(class_names) - 1,
                size=1
            ),
            hoverinfo="skip",
            showlegend=False
        ),
        row=1,
        col=column_number
    )

    # 실제 데이터 표시
    for species in class_names:

        species_data = df[df["품종"] == species]

        fig.add_trace(
            go.Scatter(
                x=species_data["꽃잎길이"],
                y=species_data["꽃잎너비"],
                mode="markers",
                marker=dict(
                    size=5,
                    color=species_colors[species]
                ),
                name=species,
                legendgroup=species,
                showlegend=(column_number == 1),
                hovertemplate=(
                    f"품종: {species}<br>"
                    "꽃잎 길이: %{x:.2f}<br>"
                    "꽃잎 너비: %{y:.2f}"
                    "<extra></extra>"
                )
            ),
            row=1,
            col=column_number
        )

    # 사용자 입력 좌표를 무지개색으로 표시
    for index, color in enumerate(rainbow_colors):

        fig.add_trace(
            go.Scatter(
                x=[petal_length],
                y=[petal_width],
                mode="markers",
                marker=dict(
                    size=30 - index * 3,
                    color=color,
                    line=dict(color="white", width=1)
                ),
                showlegend=False,
                hoverinfo="skip"
            ),
            row=1,
            col=column_number
        )

    # 입력값 중심 별 표시
    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers",
            marker=dict(
                size=13,
                symbol="star",
                color="white",
                line=dict(color="black", width=2)
            ),
            name="사용자 입력값",
            legendgroup="input",
            showlegend=(column_number == 1),
            hovertemplate=(
                "사용자 입력값<br>"
                "꽃잎 길이: %{x:.2f}<br>"
                "꽃잎 너비: %{y:.2f}"
                "<extra></extra>"
            )
        ),
        row=1,
        col=column_number
    )

fig.update_xaxes(
    title_text="꽃잎 길이 (cm)",
    range=[x_min, x_max]
)

fig.update_yaxes(
    title_text="꽃잎 너비 (cm)",
    range=[y_min, y_max]
)

fig.update_layout(
    template="plotly_white",
    height=600,
    title="세 알고리즘의 분류 영역 비교",
    legend_title="품종",
    margin=dict(t=90, b=40)
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# 16. 알고리즘별 특성 중요도
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🔍 알고리즘별 판단 근거</div>',
    unsafe_allow_html=True
)

st.write(
    "꽃잎 길이와 너비 중 어떤 항목이 예측에 더 큰 영향을 "
    "미치는지 비교합니다."
)

importance_rows = []

for algorithm_name, algorithm_model in evaluation_models.items():

    importance = permutation_importance(
        algorithm_model,
        X_test,
        y_test,
        n_repeats=10,
        random_state=42,
        scoring="accuracy"
    )

    for feature, value in zip(
        FEATURES,
        importance.importances_mean
    ):
        importance_rows.append({
            "알고리즘": algorithm_name,
            "측정 항목": feature,
            "중요도": value * 100
        })

importance_df = pd.DataFrame(importance_rows)

importance_fig = go.Figure()

for algorithm_name in prediction_models.keys():

    subset = importance_df[
        importance_df["알고리즘"] == algorithm_name
    ]

    importance_fig.add_trace(go.Bar(
        x=subset["측정 항목"],
        y=subset["중요도"],
        name=algorithm_name
    ))

importance_fig.update_layout(
    barmode="group",
    template="plotly_white",
    height=400,
    title="알고리즘별 특성 중요도 비교",
    xaxis_title="측정 항목",
    yaxis_title="정확도 감소량 (%)"
)

st.plotly_chart(
    importance_fig,
    use_container_width=True
)

st.caption(
    "특성 중요도는 해당 항목을 섞었을 때 모델의 테스트 성능이 "
    "얼마나 변하는지 나타냅니다. 음수도 나올 수 있습니다."
)


# =========================================================
# 17. 가장 가까운 실제 데이터 5개
# =========================================================

st.markdown("---")
st.markdown(
    '<div class="section-title">🔬 가장 비슷한 실제 붓꽃 5개</div>',
    unsafe_allow_html=True
)

mean_values = X.mean()
std_values = X.std().replace(0, 1)

scaled_X = (X - mean_values) / std_values
scaled_input = (input_data - mean_values) / std_values

distances = np.sqrt(
    ((scaled_X - scaled_input.iloc[0]) ** 2).sum(axis=1)
)

nearest_indices = distances.nsmallest(5).index

nearest_df = df.loc[
    nearest_indices,
    ["꽃잎길이", "꽃잎너비", "품종"]
].copy()

nearest_df["유사도 거리"] = distances.loc[nearest_indices].values

nearest_df = nearest_df.reset_index(drop=True)

st.dataframe(
    nearest_df.style.format({
        "꽃잎길이": "{:.2f}",
        "꽃잎너비": "{:.2f}",
        "유사도 거리": "{:.3f}"
    }),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 18. 마무리
# =========================================================

st.markdown("---")

st.markdown("""
<div class="hero">
    <h2>🌸 IRIS AI LAB</h2>
    <p>한 번의 입력으로 세 가지 알고리즘을 동시에 실행합니다.</p>
    <p>Python · Pandas · Scikit-learn · Streamlit · Plotly</p>
</div>
""", unsafe_allow_html=True)
