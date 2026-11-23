
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import ast
import re

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="CINE AI | Movie Research Lab",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: #101018;
    color: #ffffff;
}

section[data-testid="stSidebar"] {
    background: #181823;
    border-right: 1px solid #343344;
}

.hero {
    background: linear-gradient(120deg, #291c42, #6e2855, #a83d56);
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 43px;
    font-weight: 800;
    color: white;
}

.hero p {
    color: #f0dce8;
    font-size: 16px;
}

.movie-card {
    background: #211f2d;
    border: 1px solid #383346;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 12px;
}

.movie-title {
    font-size: 19px;
    font-weight: 800;
    color: white;
}

.movie-detail {
    color: #c1bdcc;
    font-size: 14px;
    line-height: 1.8;
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    margin: 25px 0 15px 0;
}

div[data-testid="stMetric"] {
    background: #211f2d;
    border: 1px solid #383346;
    padding: 16px;
    border-radius: 13px;
}

.stButton button {
    border-radius: 10px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    file_path = Path("tmdb_5000_movies.csv")

    if not file_path.exists():
        raise FileNotFoundError(
            "tmdb_5000_movies.csv 파일이 app.py와 같은 폴더에 없습니다."
        )

    df = pd.read_csv(file_path)

    required = [
        "id", "title", "genres", "overview",
        "vote_average", "vote_count",
        "popularity", "release_date",
        "budget", "revenue", "runtime", "keywords"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            "CSV에 필요한 열이 없습니다: " + ", ".join(missing)
        )

    numeric_cols = [
        "vote_average", "vote_count",
        "popularity", "budget", "revenue", "runtime"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["vote_average"] = df["vote_average"].fillna(0)
    df["vote_count"] = df["vote_count"].fillna(0)
    df["popularity"] = df["popularity"].fillna(0)
    df["budget"] = df["budget"].fillna(0)
    df["revenue"] = df["revenue"].fillna(0)
    df["runtime"] = df["runtime"].fillna(0)

    df["title"] = df["title"].fillna("제목 없음")
    df["overview"] = df["overview"].fillna("")
    df["genres"] = df["genres"].fillna("[]")
    df["keywords"] = df["keywords"].fillna("[]")

    df["release_date"] = pd.to_datetime(
        df["release_date"], errors="coerce"
    )

    df["year"] = df["release_date"].dt.year

    return df


# ==========================================
# 3. JSON 형태 데이터 처리
# ==========================================

def extract_names(value):

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):
            return " ".join(
                str(item.get("name", ""))
                for item in parsed
                if isinstance(item, dict)
            )

    except (ValueError, SyntaxError, TypeError):
        pass

    return ""


def extract_genres(value):

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):
            return [
                item["name"]
                for item in parsed
                if isinstance(item, dict) and "name" in item
            ]

    except (ValueError, SyntaxError, TypeError):
        pass

    return []


# ==========================================
# 4. 데이터 전처리 및 AI 모델
# ==========================================

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.info(
        "CSV 파일을 GitHub 저장소의 app.py와 같은 위치에 올려주세요."
    )
    st.stop()


df["genre_names"] = df["genres"].apply(extract_names)
df["keyword_names"] = df["keywords"].apply(extract_names)

df["features"] = (
    df["genre_names"] + " " +
    df["keyword_names"] + " " +
    df["overview"]
)

df["features"] = df["features"].str.lower()

# ==========================================
# 5. 영화 추천 AI
# ==========================================

@st.cache_resource
def train_recommender(text_data):

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=15000,
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(text_data)

    return vectorizer, matrix


vectorizer, tfidf_matrix = train_recommender(
    df["features"].tolist()
)

# ==========================================
# 6. 공통 데이터
# ==========================================

genre_list = sorted({
    genre
    for genres in df["genre_names"]
    for genre in genres.split()
    if genre
})

genre_expanded = df.assign(
    genre=df["genre_names"].str.split()
).explode("genre")

genre_expanded = genre_expanded[
    genre_expanded["genre"] != ""
].copy()

C = df.loc[df["vote_count"] > 0, "vote_average"].mean()
if pd.isna(C):
    C = 0

m = 50

df["weighted_rating"] = (
    (df["vote_count"] / (df["vote_count"] + m))
    * df["vote_average"]
    +
    (m / (df["vote_count"] + m)) * C
)

# ==========================================
# 7. 영화 추천 함수
# ==========================================

def recommend_movies(movie_title, selected_genres=None, count=10):

    matched = df.index[df["title"] == movie_title].tolist()

    if not matched:
        return pd.DataFrame()

    movie_idx = matched[0]

    similarity = cosine_similarity(
        tfidf_matrix[movie_idx],
        tfidf_matrix
    ).flatten()

    result = df.copy()
    result["similarity"] = similarity

    result = result[
        result.index != movie_idx
    ].copy()

    if selected_genres:
        result = result[
            result["genre_names"].apply(
                lambda x: any(g in x.split() for g in selected_genres)
            )
        ]

    result["recommend_score"] = (
        result["similarity"] * 0.7
        +
        (result["weighted_rating"] / 10) * 0.3
    )

    result = result.sort_values(
        "recommend_score",
        ascending=False
    )

    return result.head(count)


# ==========================================
# 8. 사이드바
# ==========================================

st.sidebar.markdown("# 🎬 CINE AI")
st.sidebar.caption("MOVIE RESEARCH LAB")
st.sidebar.divider()

page = st.sidebar.radio(
    "메뉴",
    [
        "🏠 메인 대시보드",
        "🤖 AI 영화 추천",
        "📊 데이터 분석",
        "🔍 영화 탐색"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### 📁 데이터 현황")

st.sidebar.metric("전체 영화", f"{len(df):,}편")

st.sidebar.metric(
    "평점 데이터 보유 영화",
    f"{(df['vote_count'] > 0).sum():,}편"
)

st.sidebar.metric(
    "전체 장르",
    f"{len(genre_list)}종"
)

st.sidebar.caption("SOURCE : TMDB 5000 MOVIES")


# ==========================================
# 9. 공통 영화 카드
# ==========================================

def show_movie_cards(data):

    if data.empty:
        st.warning("검색 결과가 없습니다.")
        return

    for start in range(0, len(data), 2):

        cols = st.columns(2)

        for col, (_, movie) in zip(
            cols,
            data.iloc[start:start + 2].iterrows()
        ):

            with col:

                year = (
                    int(movie["year"])
                    if pd.notna(movie["year"])
                    else "연도 미상"
                )

                st.markdown(
                    f"""
                    <div class="movie-card">
                        <div class="movie-title">
                            🎬 {movie['title']}
                        </div>
                        <div class="movie-detail">
                            📅 {year}<br>
                            🎭 {movie['genre_names']}<br>
                            ⭐ {movie['vote_average']:.1f} / 10<br>
                            👥 투표 수: {int(movie['vote_count']):,}<br>
                            🔥 인기도: {movie['popularity']:.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ==========================================
# 10. 메인 대시보드
# ==========================================

if page == "🏠 메인 대시보드":

    st.markdown("""
    <div class="hero">
        <h1>🎬 CINE AI</h1>
        <p>영화 데이터로 발견하는 나만의 영화 취향</p>
        <p>ARTIFICIAL INTELLIGENCE × MOVIE DATA</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🎞️ 영화 수", f"{len(df):,}편")
    c2.metric("🎭 장르 수", f"{len(genre_list)}종")
    c3.metric(
        "⭐ 평균 평점",
        f"{df.loc[df['vote_count'] > 0, 'vote_average'].mean():.2f}"
    )
    c4.metric(
        "🔥 평균 인기도",
        f"{df['popularity'].mean():.1f}"
    )

    st.markdown(
        '<div class="section-title">🏆 인기 영화 TOP 10</div>',
        unsafe_allow_html=True
    )

    popular = df.sort_values(
        "popularity", ascending=False
    ).head(10)

    fig = px.bar(
        popular.sort_values("popularity"),
        x="popularity",
        y="title",
        orientation="h",
        color="popularity",
        color_continuous_scale=["#754080", "#f05d83"],
        template="plotly_dark",
        labels={
            "popularity": "인기도",
            "title": "영화"
        }
    )

    fig.update_layout(
        height=500,
        coloraxis_showscale=False,
        paper_bgcolor="#101018",
        plot_bgcolor="#101018"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="section-title">⭐ 평점 TOP 10</div>',
        unsafe_allow_html=True
    )

    best = df[
        df["vote_count"] >= 100
    ].sort_values(
        "weighted_rating",
        ascending=False
    ).head(10)

    show_movie_cards(best)


# ==========================================
# 11. AI 영화 추천
# ==========================================

elif page == "🤖 AI 영화 추천":

    st.markdown("""
    <div class="hero">
        <h1>🤖 AI MOVIE RECOMMENDER</h1>
        <p>좋아하는 영화를 선택하고 새로운 영화를 발견하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 좋아하는 영화 선택")

    selected_movie = st.selectbox(
        "영화 제목",
        sorted(df["title"].unique())
    )

    st.markdown("### 🎭 선호 장르")

    selected_genres = st.multiselect(
        "원하는 장르를 선택하세요. 선택하지 않으면 모든 장르를 대상으로 추천합니다.",
        genre_list
    )

    count = st.slider(
        "추천 영화 개수",
        min_value=5,
        max_value=20,
        value=10
    )

    if st.button(
        "✨ AI 영화 추천 시작",
        type="primary",
        use_container_width=True
    ):

        result = recommend_movies(
            selected_movie,
            selected_genres,
            count
        )

        st.divider()

        if result.empty:
            st.warning("조건에 맞는 영화가 없습니다.")

        else:
            st.success(
                f"'{selected_movie}'를 기준으로 "
                f"{len(result)}편을 추천합니다!"
            )

            st.markdown("### 🍿 추천 결과")

            show_movie_cards(result)

            st.markdown("### 📊 추천 영화 유사도")

            chart_data = result.sort_values(
                "similarity"
            )

            fig = px.bar(
                chart_data,
                x="similarity",
                y="title",
                orientation="h",
                color="similarity",
                color_continuous_scale=["#754080", "#f05d83"],
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#101018",
                plot_bgcolor="#101018",
                xaxis_title="코사인 유사도",
                yaxis_title="영화 제목"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "AI는 영화의 장르, 키워드, 줄거리를 분석합니다. "
                "TF-IDF로 텍스트를 수치화하고 코사인 유사도로 "
                "비슷한 영화를 찾아냅니다."
            )


# ==========================================
# 12. 데이터 분석
# ==========================================

elif page == "📊 데이터 분석":

    st.markdown("""
    <div class="hero">
        <h1>📊 MOVIE DATA LAB</h1>
        <p>영화 산업의 다양한 데이터를 분석합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎭 장르 분석",
        "⭐ 평점 분석",
        "📅 연도 분석",
        "💰 수익 분석"
    ])

    with tab1:

        st.markdown("### 장르별 영화 제작 수")

        genre_counts = (
            genre_expanded.groupby("genre")
            .size()
            .reset_index(name="영화 수")
            .sort_values("영화 수", ascending=False)
        )

        fig = px.bar(
            genre_counts,
            x="genre",
            y="영화 수",
            color="영화 수",
            color_continuous_scale=["#694184", "#ef6387"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 장르별 평균 평점")

        genre_rating = (
            genre_expanded[
                genre_expanded["vote_count"] > 0
            ]
            .groupby("genre")
            .agg(
                평균평점=("vote_average", "mean"),
                영화수=("id", "count")
            )
            .reset_index()
            .sort_values("평균평점", ascending=False)
        )

        fig = px.bar(
            genre_rating,
            x="genre",
            y="평균평점",
            color="평균평점",
            color_continuous_scale=["#694184", "#ef6387"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018",
            yaxis_range=[0, 10]
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:

        st.markdown("### 영화 평점 분포")

        rated = df[df["vote_count"] > 0]

        fig = px.histogram(
            rated,
            x="vote_average",
            nbins=20,
            color_discrete_sequence=["#e85d88"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018",
            xaxis_title="평균 평점",
            yaxis_title="영화 수"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 인기도와 평점의 관계")

        fig = px.scatter(
            rated,
            x="popularity",
            y="vote_average",
            hover_name="title",
            size="vote_count",
            color="vote_average",
            color_continuous_scale=["#754080", "#f05d83"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab3:

        st.markdown("### 연도별 영화 제작 수")

        yearly = (
            df.dropna(subset=["year"])
            .groupby("year")
            .size()
            .reset_index(name="영화 수")
        )

        yearly = yearly[
            (yearly["year"] >= 1900)
            & (yearly["year"] <= 2020)
        ]

        fig = px.line(
            yearly,
            x="year",
            y="영화 수",
            markers=True,
            color_discrete_sequence=["#ed6590"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018",
            xaxis_title="개봉 연도",
            yaxis_title="영화 수"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 연도별 평균 평점")

        yearly_rating = (
            df[df["vote_count"] > 0]
            .dropna(subset=["year"])
            .groupby("year")
            .agg(
                평균평점=("vote_average", "mean"),
                영화수=("id", "count")
            )
            .reset_index()
        )

        yearly_rating = yearly_rating[
            (yearly_rating["year"] >= 1900)
            & (yearly_rating["year"] <= 2020)
            & (yearly_rating["영화수"] >= 5)
        ]

        fig = px.line(
            yearly_rating,
            x="year",
            y="평균평점",
            markers=True,
            color_discrete_sequence=["#55c6d7"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018",
            yaxis_range=[0, 10]
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab4:

        st.markdown("### 제작비와 수익 관계")

        money = df[
            (df["budget"] > 0)
            & (df["revenue"] > 0)
        ].copy()

        fig = px.scatter(
            money,
            x="budget",
            y="revenue",
            hover_name="title",
            color="vote_average",
            color_continuous_scale=["#754080", "#f05d83"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#101018",
            plot_bgcolor="#101018",
            xaxis_title="제작비 (USD)",
            yaxis_title="수익 (USD)"
        )

        st.plotly_chart(fig, use_container_width=True)

        money["profit"] = money["revenue"] - money["budget"]

        st.markdown("### 수익이 높은 영화 TOP 10")

        top_profit = money.sort_values(
            "profit", ascending=False
        ).head(10)

        st.dataframe(
            top_profit[
                ["title", "budget", "revenue", "profit"]
            ].rename(columns={
                "title": "영화",
                "budget": "제작비",
                "revenue": "수익",
                "profit": "추정 수익"
            }),
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 13. 영화 탐색
# ==========================================

elif page == "🔍 영화 탐색":

    st.markdown("""
    <div class="hero">
        <h1>🔍 MOVIE EXPLORER</h1>
        <p>원하는 영화를 검색하고 정보를 확인하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    keyword = st.text_input(
        "영화 제목 검색",
        placeholder="영화 제목을 입력하세요."
    )

    selected_genre = st.selectbox(
        "장르 선택",
        ["전체"] + genre_list
    )

    min_rating = st.slider(
        "최소 평점",
        0.0, 10.0, 0.0, 0.5
    )

    filtered = df.copy()

    if keyword:
        filtered = filtered[
            filtered["title"].str.contains(
                keyword,
                case=False,
                regex=False,
                na=False
            )
        ]

    if selected_genre != "전체":
        filtered = filtered[
            filtered["genre_names"].apply(
                lambda x: selected_genre in x.split()
            )
        ]

    filtered = filtered[
        filtered["vote_average"] >= min_rating
    ]

    filtered = filtered.sort_values(
        "popularity",
        ascending=False
    )

    st.markdown(
        f"### 🔎 검색 결과: {len(filtered):,}편"
    )

    if not filtered.empty:

        st.dataframe(
            filtered[
                [
                    "title", "genre_names",
                    "release_date", "vote_average",
                    "vote_count", "runtime"
                ]
            ].rename(columns={
                "title": "영화 제목",
                "genre_names": "장르",
                "release_date": "개봉일",
                "vote_average": "평균 평점",
                "vote_count": "투표 수",
                "runtime": "상영 시간"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.markdown("### 🎥 영화 상세 정보")

        detail_title = st.selectbox(
            "상세 정보를 확인할 영화",
            filtered["title"].tolist()
        )

        movie = filtered[
            filtered["title"] == detail_title
        ].iloc[0]

        c1, c2, c3 = st.columns(3)

        c1.metric("⭐ 평점", f"{movie['vote_average']:.1f}/10")
        c2.metric("🔥 인기도", f"{movie['popularity']:.1f}")
        c3.metric("⏱️ 상영 시간", f"{int(movie['runtime'])}분")

        st.markdown(f"### {movie['title']}")
        st.write("**장르:**", movie["genre_names"])
        st.write("**개봉일:**", str(movie["release_date"].date()) if pd.notna(movie["release_date"]) else "정보 없음")
        st.write("**줄거리:**", movie["overview"])

        if movie["homepage"]:
            st.markdown(
                f"[공식 홈페이지 바로가기]({movie['homepage']})"
            )

    else:
        st.warning("검색 결과가 없습니다.")


# ==========================================
# 14. 하단 정보
# ==========================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:20px; color:#aaa5b8;">
    <h3 style="color:#e66b91;">🎬 CINE AI</h3>
    MOVIE RESEARCH LAB
    <br>
    Powered by Python · Streamlit · Scikit-learn
    <br>
    Data Source: TMDB 5000 Movie Dataset
</div>
""", unsafe_allow_html=True)

