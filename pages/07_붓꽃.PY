
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="Iris AI 품종 예측",
    page_icon="🌸",
    layout="wide"
)

# ==========================================
# 2. 디자인 CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f5ff, #edf5ff);
}

.main .block-container {
    max-width: 1250px;
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
    box-shadow: 0 8px 25px rgba(120, 90, 200, 0.2);
}

.hero h1 {
    font-size: 38px;
    font-weight: 900;
    color: white;
}

.hero p {
    font-size: 16px;
    color: white;
}

.result {
    background: white;
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    border: 1px solid #e9e4ff;
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    color: #6654c9;
    margin-top: 25px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #eee8ff;
}

.stButton button {
    border-radius: 12px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 제목
# ==========================================

st.markdown("""
<div class="hero">
    <h1>🌸 IRIS AI CLASSIFIER</h1>
    <p>인공지능으로 예측하는 나만의 붓꽃 품종 분석실</p>
    <p>꽃잎의 길이와 너비를 입력하고 AI의 예측 과정을 확인해 보세요!</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    possible_paths = [
        current_dir.parent / "Iris.csv",
        current_dir / "Iris.csv"
    ]

    file_path = next(
        (p for p in possible_paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "Iris.csv 파일을 찾을 수 없습니다."
        )

    # 실제 업로드된 데이터는 CP949 인코딩
    df = pd.read_csv(file_path, encoding="cp949")

    if len(df.columns) != 5:
        raise ValueError("Iris.csv는 총 5개 열이어야 합니다.")

    # 잘못 저장된 첫 번째 열 제목도 정상화
    df.columns = [
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
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["품종"] = df["품종"].astype(str).str.strip()

    df = df.dropna(subset=numeric_columns + ["품종"])

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류 발생: {e}")
    st.stop()


# ==========================================
# 5. 학습 데이터 및 알고리즘
# ==========================================

features = ["꽃잎길이", "꽃잎너비"]

X = df[features]
y = df["품종"]

if y.nunique() < 2:
    st.error("분류하려면 최소 2개 이상의 품종이 필요합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=5,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# 테스트 데이터 평가
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# 실제 데이터 전체로 최종 모델 학습
model.fit(X, y)


# ==========================================
# 6. 데이터 요약
# ==========================================

st.markdown('<div class="section-title">📊 데이터 분석 현황</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{y.nunique()}종")
c3.metric("모델 정확도", f"{accuracy * 100:.1f}%")
c4.metric("사용 알고리즘", "Random Forest")

st.caption(
    "정확도는 전체 데이터를 학습하기 전 분리한 테스트 데이터에서 측정한 값입니다."
)


# ==========================================
# 7. 사용자 입력
# ==========================================

st.markdown('<div class="section-title">🎯 나만의 붓꽃 측정</div>',
            unsafe_allow_html=True)

left, right = st.columns([1, 1])

with left:

    st.markdown("### 🌱 꽃잎 정보 입력")

    min_length = float(df["꽃잎길이"].min())
    max_length = float(df["꽃잎길이"].max())

    min_width = float(df["꽃잎너비"].min())
    max_width = float(df["꽃잎너비"].max())

    petal_length = st.number_input(
        "🌸 꽃잎 길이 (cm)",
        min_value=0.1,
        max_value=10.0,
        value=5.0,
        step=0.1
    )

    petal_width = st.number_input(
        "🌼 꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=5.0,
        value=1.8,
        step=0.1
    )

    predict_button = st.button(
        "✨ AI 품종 예측하기",
        use_container_width=True,
        type="primary"
    )

with right:

    st.markdown("### 💡 입력값 미리보기")

    st.markdown(
        f"""
        <div class="result">
            <h2 style="color:#7967e8;">YOUR INPUT</h2>
            <h1 style="color:#e879b9;">🌈</h1>
            <h3>꽃잎 길이 : {petal_length:.1f} cm</h3>
            <h3>꽃잎 너비 : {petal_width:.1f} cm</h3>
            <p style="color:gray;">
                이 좌표를 인공지능 모델이 분석합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# 8. 품종 예측
# ==========================================

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=features
)

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

classes = model.classes_

prob_df = pd.DataFrame({
    "품종": classes,
    "예측 확률": probabilities
})

prob_df = prob_df.sort_values(
    "예측 확률",
    ascending=False
)

# ==========================================
# 9. 예측 결과
# ==========================================

st.markdown("---")
st.markdown('<div class="section-title">🏆 AI 예측 결과</div>',
            unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="result">
        <h2 style="color:#7967e8;">AI가 예측한 붓꽃 품종</h2>
        <h1 style="color:#e879b9;font-size:38px;">
            🌸 {prediction}
        </h1>
        <h3>예측 신뢰도: {probabilities[np.where(classes == prediction)[0][0]] * 100:.1f}%</h3>
        <p style="color:gray;">
            랜덤 포레스트의 각 결정 트리가 투표한 결과를 종합했습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 10. 품종별 분류 영역 시각화
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🌈 AI 품종 분류 지도</div>',
    unsafe_allow_html=True
)

st.write(
    "배경색은 AI가 각 위치에서 예측하는 품종을 나타냅니다. "
    "색상 영역의 경계는 품종이 달라지는 지점입니다."
)

# 그래프 격자 생성
x_min = min(0, min_length - 0.5)
x_max = max_length + 0.7

y_min = min(0, min_width - 0.3)
y_max = max_width + 0.4

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
    name: i for i, name in enumerate(classes)
}

Z_num = np.array([
    class_to_num[v] for v in Z
]).reshape(xx.shape)

# 품종별 색상
species_colors = {
    classes[0]: "#FF6384",
    classes[1]: "#36A2EB",
    classes[2]: "#42C98A"
}

# 그래프 생성
fig = go.Figure()

# 분류 영역
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
        opacity=0.22,
        showscale=False,
        contours=dict(
            coloring="fill",
            showlines=True
        ),
        hoverinfo="skip",
        name="AI 분류 영역"
    )
)

# 실제 데이터 표시
for species in classes:

    subset = df[df["품종"] == species]

    fig.add_trace(
        go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                size=9,
                color=species_colors[species],
                line=dict(color="white", width=1)
            ),
            hovertemplate=(
                "품종: " + species +
                "<br>꽃잎 길이: %{x} cm" +
                "<br>꽃잎 너비: %{y} cm" +
                "<extra></extra>"
            )
        )
    )

# 사용자 입력값 무지개색 강조
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

# 입력 좌표 중심 표시
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers+text",
        text=["YOUR INPUT"],
        textposition="top center",
        marker=dict(
            size=13,
            color="white",
            symbol="star",
            line=dict(color="#222222", width=2)
        ),
        name="내 입력값",
        hovertemplate=(
            "내 입력값<br>" +
            "꽃잎 길이: %{x:.2f} cm<br>" +
            "꽃잎 너비: %{y:.2f} cm" +
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=650,
    template="plotly_white",
    title=dict(
        text="🌈 Petal Length × Petal Width",
        x=0.5
    ),
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    legend_title="붓꽃 품종",
    font=dict(
        family="Arial",
        size=13
    ),
    margin=dict(l=30, r=30, t=70, b=40),
    hovermode="closest"
)

fig.update_xaxes(range=[x_min, x_max])
fig.update_yaxes(range=[y_min, y_max])

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 11. 예측 확률 시각화
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">📈 품종별 예측 확률</div>',
    unsafe_allow_html=True
)

prob_fig = go.Figure()

prob_fig.add_trace(
    go.Bar(
        x=prob_df["품종"],
        y=prob_df["예측 확률"] * 100,
        marker_color=[
            species_colors[s] for s in prob_df["품종"]
        ],
        text=[
            f"{v * 100:.1f}%"
            for v in prob_df["예측 확률"]
        ],
        textposition="outside"
    )
)

prob_fig.update_layout(
    height=350,
    template="plotly_white",
    yaxis_title="예측 확률 (%)",
    yaxis=dict(range=[0, 115]),
    xaxis_title="붓꽃 품종",
    showlegend=False
)

st.plotly_chart(
    prob_fig,
    use_container_width=True
)


# ==========================================
# 12. 왜 이 품종으로 분류되었을까?
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔍 AI의 판단 근거 분석</div>',
    unsafe_allow_html=True
)

# 특성 중요도
importance = model.feature_importances_

importance_fig = go.Figure(
    go.Bar(
        x=importance * 100,
        y=features,
        orientation="h",
        marker_color=["#8D78EF", "#E879B9"],
        text=[f"{v * 100:.1f}%" for v in importance],
        textposition="outside"
    )
)

importance_fig.update_layout(
    title="AI가 품종을 구분할 때 활용한 특성 중요도",
    height=300,
    template="plotly_white",
    xaxis_title="중요도 (%)",
    xaxis=dict(range=[0, 115]),
    yaxis_title="측정 항목"
)

st.plotly_chart(
    importance_fig,
    use_container_width=True
)

# 예측 결과 설명
best_prob = float(probabilities[
    np.where(classes == prediction)[0][0]
])

st.markdown(f"""
### 🧠 분석 결과 해설

- 입력한 꽃잎 길이: **{petal_length:.1f} cm**
- 입력한 꽃잎 너비: **{petal_width:.1f} cm**
- 최종 예측 품종: **{prediction}**
- 해당 품종의 예측 확률: **{best_prob * 100:.1f}%**

AI는 입력한 두 가지 측정값을 학습 데이터의 품종별 패턴과 비교했습니다.

그래프에서 입력 좌표가 위치한 배경색은
**{prediction}** 품종으로 분류되는 영역입니다.

예측 확률은 랜덤 포레스트의 개별 결정 트리들이
각 품종에 투표한 비율을 바탕으로 계산됩니다.
""")

# ==========================================
# 13. 가장 가까운 실제 데이터 비교
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔬 가장 비슷한 실제 붓꽃 5개</div>',
    unsafe_allow_html=True
)

# 두 특성의 단위와 범위를 표준화해 거리 계산
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

st.info(
    "유사도 거리는 두 측정값을 표준화한 뒤 계산했습니다. "
    "거리가 작을수록 입력값과 비슷한 실제 데이터입니다. "
    "가까운 데이터는 참고 자료이며 최종 분류는 랜덤 포레스트가 결정합니다."
)

# ==========================================
# 14. 마무리
# ==========================================

st.markdown("---")

st.markdown("""
<div class="hero">
    <h2>🌸 IRIS AI LAB</h2>
    <p>데이터를 이해하면 인공지능의 판단 과정을 이해할 수 있습니다.</p>
    <p>Made with Python · Pandas · Scikit-learn · Streamlit</p>
</div>
""", unsafe_allow_html=True)
