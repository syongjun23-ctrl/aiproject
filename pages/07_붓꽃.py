
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.inspection import permutation_importance


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="Iris AI 품종 예측",
    page_icon="🌸",
    layout="wide"
)


# ==========================================
# 2. 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f5ff, #edf5ff);
}

.main .block-container {
    max-width: 1300px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #7967e8, #e879b9);
    padding: 35px;
    border-radius: 25px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(120,90,200,0.2);
}

.hero h1 {
    font-size: 38px;
    font-weight: 900;
    color: white;
}

.hero p {
    color: white;
    font-size: 16px;
}

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #6654c9;
    margin-top: 25px;
    margin-bottom: 12px;
}

.result {
    background: white;
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    border: 1px solid #e9e4ff;
}

.algorithm-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e9e4ff;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 15px;
    border: 1px solid #eee8ff;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 제목
# ==========================================

st.markdown("""
<div class="hero">
    <h1>🌸 IRIS AI CLASSIFIER</h1>
    <p>3가지 인공지능 알고리즘으로 분석하는 붓꽃 품종 예측</p>
    <p>꽃잎의 길이와 너비를 입력하고 AI의 판단을 확인해 보세요!</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    paths = [
        current_dir.parent / "Iris.csv",
        current_dir / "Iris.csv"
    ]

    file_path = next(
        (p for p in paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "Iris.csv 파일을 찾을 수 없습니다. "
            "프로젝트 최상위 폴더를 확인하세요."
        )

    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    if len(df.columns) != 5:
        raise ValueError("CSV 데이터는 총 5개 열이어야 합니다.")

    df.columns = [
        "꽃받침길이",
        "꽃받침너비",
        "꽃잎길이",
        "꽃잎너비",
        "품종"
    ]

    numeric_cols = [
        "꽃받침길이",
        "꽃받침너비",
        "꽃잎길이",
        "꽃잎너비"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["품종"] = df["품종"].astype(str).str.strip()

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=numeric_cols + ["품종"])

    return df.reset_index(drop=True)


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 5. 데이터 준비
# ==========================================

features = ["꽃잎길이", "꽃잎너비"]

X = df[features]
y = df["품종"]

if y.nunique() < 2:
    st.error("2개 이상의 품종 데이터가 필요합니다.")
    st.stop()

if y.value_counts().min() < 2:
    st.error("각 품종마다 최소 2개의 데이터가 필요합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==========================================
# 6. 알고리즘 설정
# ==========================================

algorithm_names = [
    "🌳 랜덤 포레스트",
    "📍 KNN",
    "⚖️ SVM"
]

algorithm_descriptions = {
    "🌳 랜덤 포레스트": {
        "title": "Random Forest (랜덤 포레스트)",
        "principle": """
여러 개의 의사결정나무를 만들어 각각 품종을 예측한 뒤
가장 많은 표를 얻은 품종을 최종 결과로 선택합니다.
""",
        "features": [
            "여러 나무의 결과를 종합하여 예측합니다.",
            "복잡한 데이터 패턴을 학습할 수 있습니다.",
            "특성 중요도를 확인할 수 있습니다."
        ],
        "example": "300개의 의사결정나무가 투표하여 최종 품종을 결정합니다."
    },

    "📍 KNN": {
        "title": "K-Nearest Neighbors (K-최근접 이웃)",
        "principle": """
새로운 데이터가 들어오면 기존 데이터 중에서
가장 가까운 K개의 데이터를 찾습니다.
그 이웃들이 가장 많이 속한 품종으로 분류합니다.
""",
        "features": [
            "주변 데이터의 영향을 많이 받습니다.",
            "구조가 단순하고 이해하기 쉽습니다.",
            "거리 계산이 중요하므로 데이터 표준화가 필요합니다."
        ],
        "example": "가장 가까운 5개 붓꽃의 품종을 확인하고 다수결로 결정합니다."
    },

    "⚖️ SVM": {
        "title": "Support Vector Machine (서포트 벡터 머신)",
        "principle": """
품종이 서로 잘 구분되도록 데이터 사이에 경계선을 만듭니다.
각 품종을 구분하는 경계를 학습하여 새로운 데이터를 분류합니다.
""",
        "features": [
            "데이터 사이의 분류 경계를 학습합니다.",
            "커널을 사용하면 복잡한 경계도 표현할 수 있습니다.",
            "특성의 크기에 영향을 받으므로 표준화가 중요합니다."
        ],
        "example": "RBF 커널을 사용해 복잡한 붓꽃 품종의 경계를 학습합니다."
    }
}


def make_model(name):

    if name == "🌳 랜덤 포레스트":
        return RandomForestClassifier(
            n_estimators=300,
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        )

    elif name == "📍 KNN":
        return Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(
                n_neighbors=5,
                weights="distance"
            ))
        ])

    elif name == "⚖️ SVM":
        return Pipeline([
            ("scaler", StandardScaler()),
            ("svm", SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                probability=True,
                random_state=42
            ))
        ])


# ==========================================
# 7. 알고리즘별 테스트 정확도 비교
# ==========================================

accuracies = {}

for name in algorithm_names:

    test_model = make_model(name)

    test_model.fit(X_train, y_train)

    predictions = test_model.predict(X_test)

    accuracies[name] = accuracy_score(
        y_test,
        predictions
    )


# ==========================================
# 8. 데이터 현황
# ==========================================

st.markdown(
    '<div class="section-title">📊 데이터 분석 현황</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("품종 개수", f"{y.nunique()}종")
c3.metric("사용 알고리즘", "3가지")
c4.metric("테스트 데이터", f"{len(X_test)}개")


# ==========================================
# 9. 알고리즘 선택
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧠 AI 알고리즘 선택</div>',
    unsafe_allow_html=True
)

selected_algorithm = st.selectbox(
    "사용할 분류 알고리즘을 선택하세요.",
    algorithm_names
)

description = algorithm_descriptions[selected_algorithm]

st.markdown(
    f"""
    <div class="algorithm-card">
        <h3 style="color:#7967e8;">
            {description["title"]}
        </h3>
        <p>{description["principle"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("🔎 이 알고리즘의 특징 자세히 보기"):

    for feature in description["features"]:
        st.markdown(f"- {feature}")

    st.info(description["example"])


# ==========================================
# 10. 알고리즘 정확도 비교
# ==========================================

st.markdown(
    '<div class="section-title">🏆 알고리즘 성능 비교</div>',
    unsafe_allow_html=True
)

accuracy_df = pd.DataFrame({
    "알고리즘": list(accuracies.keys()),
    "정확도": [
        value * 100
        for value in accuracies.values()
    ]
})

accuracy_fig = go.Figure()

accuracy_fig.add_trace(
    go.Bar(
        x=accuracy_df["알고리즘"],
        y=accuracy_df["정확도"],
        marker_color=["#8D78EF", "#36A2EB", "#E879B9"],
        text=[
            f"{v:.1f}%"
            for v in accuracy_df["정확도"]
        ],
        textposition="outside"
    )
)

accuracy_fig.update_layout(
    template="plotly_white",
    height=370,
    title="3가지 알고리즘의 테스트 정확도",
    yaxis_title="정확도 (%)",
    yaxis=dict(range=[0, 115]),
    showlegend=False
)

st.plotly_chart(
    accuracy_fig,
    use_container_width=True
)

st.caption(
    "동일한 학습/테스트 데이터 분할을 사용한 비교입니다. "
    "정확도는 데이터 분할에 따라 달라질 수 있습니다."
)


# ==========================================
# 11. 선택한 알고리즘 최종 학습
# ==========================================

model = make_model(selected_algorithm)

model.fit(X, y)

classes = model.classes_


# ==========================================
# 12. 사용자 입력
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🎯 꽃잎 정보 입력</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

length_min = float(X["꽃잎길이"].min())
length_max = float(X["꽃잎길이"].max())

width_min = float(X["꽃잎너비"].min())
width_max = float(X["꽃잎너비"].max())

with left:

    st.markdown("### 🌸 꽃잎 길이")

    st.caption(
        f"입력 가능 범위: {length_min:.2f} ~ {length_max:.2f} cm"
    )

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

    st.caption(
        f"입력 가능 범위: {width_min:.2f} ~ {width_max:.2f} cm"
    )

    petal_width = st.slider(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(np.clip(1.8, width_min, width_max)),
        step=0.1,
        key="petal_width"
    )

st.info(
    "입력 범위는 Iris.csv에 실제로 기록된 꽃잎 길이와 너비의 "
    "최솟값 및 최댓값을 기준으로 설정했습니다."
)

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=features
)


# ==========================================
# 13. 예측
# ==========================================

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

best_prob = float(
    probabilities[np.where(classes == prediction)[0][0]]
)


# ==========================================
# 14. 예측 결과
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🏆 AI 예측 결과</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="result">
        <h2 style="color:#7967e8;">
            {selected_algorithm}
        </h2>
        <h1 style="color:#e879b9;font-size:38px;">
            🌸 {prediction}
        </h1>
        <h3>예측 확률: {best_prob * 100:.1f}%</h3>
        <p style="color:gray;">
            선택한 알고리즘으로 입력 데이터를 분석했습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 15. 분류 영역 그래프
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🌈 AI 품종 분류 지도</div>',
    unsafe_allow_html=True
)

st.write(
    "배경색은 선택한 알고리즘이 예측한 품종 영역입니다. "
    "무지개색 별은 사용자가 입력한 좌표입니다."
)

species_colors = {
    classes[i]: color
    for i, color in enumerate(
        ["#FF6384", "#36A2EB", "#42C98A"][:len(classes)]
    )
}

x_min = length_min - 0.2
x_max = length_max + 0.2
y_min = width_min - 0.1
y_max = width_max + 0.1

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 250),
    np.linspace(y_min, y_max, 250)
)

grid = pd.DataFrame({
    "꽃잎길이": xx.ravel(),
    "꽃잎너비": yy.ravel()
})

Z = model.predict(grid)

class_to_num = {
    name: i
    for i, name in enumerate(classes)
}

Z_num = np.array([
    class_to_num[v] for v in Z
]).reshape(xx.shape)

fig = go.Figure()

colorscale = []

for i, name in enumerate(classes):

    start = i / len(classes)
    end = (i + 1) / len(classes)

    colorscale.append([start, species_colors[name]])
    colorscale.append([end, species_colors[name]])

fig.add_trace(
    go.Contour(
        x=np.linspace(x_min, x_max, 250),
        y=np.linspace(y_min, y_max, 250),
        z=Z_num,
        colorscale=colorscale,
        opacity=0.24,
        showscale=False,
        contours=dict(
            coloring="fill",
            showlines=True,
            start=0,
            end=len(classes)-1,
            size=1
        ),
        hoverinfo="skip",
        name="품종 분류 영역"
    )
)

# 실제 붓꽃 데이터
for species in classes:

    subset = df[df["품종"] == species]

    fig.add_trace(
        go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                size=8,
                color=species_colors[species],
                line=dict(color="white", width=1)
            )
        )
    )

# 무지개색 입력 좌표
rainbow = [
    "#FF0000",
    "#FF7F00",
    "#FFFF00",
    "#00CC44",
    "#0099FF",
    "#3333FF",
    "#9400D3"
]

for i, color in enumerate(rainbow):

    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers",
            marker=dict(
                size=39 - i * 4,
                color=color,
                line=dict(color="white", width=1)
            ),
            showlegend=False,
            hoverinfo="skip"
        )
    )

fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers+text",
        text=["YOUR INPUT"],
        textposition="top center",
        marker=dict(
            size=13,
            symbol="star",
            color="white",
            line=dict(color="#222222", width=2)
        ),
        name="내 입력값",
        hovertemplate=(
            "꽃잎 길이: %{x:.2f} cm<br>"
            "꽃잎 너비: %{y:.2f} cm"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=650,
    template="plotly_white",
    title=f"{selected_algorithm} 품종 분류 영역",
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    legend_title="붓꽃 품종",
    hovermode="closest"
)

fig.update_xaxes(range=[x_min, x_max])
fig.update_yaxes(range=[y_min, y_max])

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 16. 품종별 예측 확률
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">📈 품종별 예측 확률</div>',
    unsafe_allow_html=True
)

prob_df = pd.DataFrame({
    "품종": classes,
    "예측 확률": probabilities * 100
}).sort_values(
    "예측 확률",
    ascending=False
)

prob_fig = go.Figure(
    go.Bar(
        x=prob_df["품종"],
        y=prob_df["예측 확률"],
        marker_color=[
            species_colors[s]
            for s in prob_df["품종"]
        ],
        text=[
            f"{v:.1f}%"
            for v in prob_df["예측 확률"]
        ],
        textposition="outside"
    )
)

prob_fig.update_layout(
    template="plotly_white",
    height=350,
    yaxis_title="예측 확률 (%)",
    yaxis=dict(range=[0, 115]),
    showlegend=False
)

st.plotly_chart(
    prob_fig,
    use_container_width=True
)


# ==========================================
# 17. 알고리즘의 판단 근거
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔍 AI 판단 근거 분석</div>',
    unsafe_allow_html=True
)

st.write(
    "특성 중요도는 각 측정 항목을 섞었을 때 "
    "모델의 예측 정확도가 얼마나 감소하는지를 이용해 계산합니다."
)

importance = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=10,
    random_state=42,
    scoring="accuracy"
)

importance_fig = go.Figure(
    go.Bar(
        x=importance.importances_mean * 100,
        y=features,
        orientation="h",
        marker_color=["#8D78EF", "#E879B9"],
        text=[
            f"{v * 100:.2f}%"
            for v in importance.importances_mean
        ],
        textposition="outside"
    )
)

importance_fig.update_layout(
    template="plotly_white",
    height=320,
    title="측정 항목별 특성 중요도",
    xaxis_title="정확도 감소량 (%)",
    yaxis_title="측정 항목"
)

st.plotly_chart(
    importance_fig,
    use_container_width=True
)

st.info(
    "특성 중요도는 해당 모델과 테스트 데이터에서 측정한 "
    "변수의 상대적 영향도를 나타냅니다. "
    "값이 낮거나 음수일 수도 있으며, 인과관계를 의미하지는 않습니다."
)


# ==========================================
# 18. 가장 가까운 실제 붓꽃
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔬 가장 비슷한 실제 붓꽃 5개</div>',
    unsafe_allow_html=True
)

mean_values = X.mean()
std_values = X.std().replace(0, 1)

scaled_X = (X - mean_values) / std_values

scaled_input = (
    input_data - mean_values
) / std_values

distances = np.sqrt(
    ((scaled_X - scaled_input.iloc[0]) ** 2).sum(axis=1)
)

nearest_indices = distances.nsmallest(5).index

nearest_df = df.loc[
    nearest_indices,
    ["꽃잎길이", "꽃잎너비", "품종"]
].copy()

nearest_df["유사도 거리"] = distances.loc[
    nearest_indices
].values

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

st.caption(
    "유사도 거리는 표준화한 두 측정값의 유클리드 거리입니다. "
    "이 표는 참고용이며 최종 품종은 선택한 알고리즘이 결정합니다."
)


# ==========================================
# 19. 마무리
# ==========================================

st.markdown("---")

st.markdown("""
<div class="hero">
    <h2>🌸 IRIS AI LAB</h2>
    <p>세 가지 알고리즘으로 붓꽃의 품종을 분석해 보세요!</p>
    <p>Python · Pandas · Scikit-learn · Streamlit · Plotly</p>
</div>
""", unsafe_allow_html=True)
