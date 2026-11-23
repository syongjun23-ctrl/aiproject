
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import ast
import html
from pathlib import Path
from io import BytesIO

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="CINE AI | 영화 분석",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 2. 디자인
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #F8FAFC !important;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, #252849 0%, transparent 35%),
        linear-gradient(135deg, #101321 0%, #171A2E 55%, #101321 100%);
}

[data-testid="stHeader"] {
    background: rgba(16,19,33,0.95);
}

[data-testid="stSidebar"] {
    background: #171A2B !important;
    border-right: 1px solid #343952;
}

[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

[data-testid="stMarkdownContainer"] p {
    color: #E5E7EB !important;
}

[data-testid="stMetric"] {
    background: #252A42;
    border: 1px solid #414967;
    border-radius: 16px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #C7D2FE !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

[data-testid="stMetricDelta"] {
    color: #86EFAC !important;
}

.stSelectbox label,
.stMultiSelect label,
.stSlider label,
.stTextInput label,
.stRadio label {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

[data-baseweb="select"] > div {
    background-color: #252A42 !important;
    border-color: #69749B !important;
    color: #FFFFFF !important;
}

[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

input, textarea {
    background-color: #252A42 !important;
    color: #FFFFFF !important;
    border-color: #69749B !important;
}

.stButton > button {
    background: linear-gradient(90deg, #7567F8, #A855F7) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    padding: 10px 20px !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #9388FF, #C084FC) !important;
}

div[data-testid="stTabs"] button {
    color: #DDE3F0 !important;
    font-weight: 700 !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #C4B5FD !important;
}

hr {
    border-color: #3A405B !important;
}

.movie-card {
    background: linear-gradient(145deg, #292E49, #20243A);
    border: 1px solid #485174;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    min-height: 150px;
}

.movie-title {
    font-size: 20px;
    font-weight: 900;
    color: #FFFFFF !important;
    line-height: 1.4;
    margin-bottom: 7px;
}

.movie-korean {
    font-size: 17px;
    font-weight: 800;
    color: #FFD166 !important;
    margin-bottom: 12px;
}

.movie-info {
    color: #D7DCEF !important;
    font-size: 14px;
    line-height: 1.8;
}

.hero {
    background: linear-gradient(110deg, #38336F, #573B85, #293C6B);
    padding: 32px;
    border-radius: 20px;
    border: 1px solid #7771C7;
    margin-bottom: 25px;
}

.hero-title {
    color: #FFFFFF !important;
    font-size: 38px;
    font-weight: 900;
}

.hero-subtitle {
    color: #E5E7FF !important;
    font-size: 16px;
}

.section-title {
    color: #FFFFFF !important;
    font-size: 24px;
    font-weight: 900;
    margin-top: 20px;
    margin-bottom: 15px;
}

.notice {
    background: #252A42;
    border-left: 4px solid #A78BFA;
    border-radius: 8px;
    padding: 13px 16px;
    color: #E5E7EB !important;
    margin: 10px 0 20px 0;
}

[data-testid="stExpander"] {
    background: #222740;
    border: 1px solid #414967;
    border-radius: 12px;
}

[data-testid="stExpander"] summary {
    color: #FFFFFF !important;
}

.stAlert {
    color: #FFFFFF !important;
}

small {
    color: #CBD5E1 !important;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. 공통 화면 함수
# ==================================================

def show_footer():
    """HTML을 문자열로 노출하지 않고 실제 HTML로 렌더링."""
    st.markdown("""
    <div style="text-align:center; padding:15px;">
        <div style="
            color:#FFFFFF;
            font-size:20px;
            font-weight:900;
        ">
            🎬 CINE AI
        </div>
        <div style="
            color:#CBD5E1;
            font-size:13px;
            margin-top:8px;
        ">
            TMDB 5000 Movies Dataset 기반 영화 분석 프로젝트
        </div>
        <div style="
            color:#A5B4FC;
            font-size:12px;
            margin-top:6px;
        ">
            영화 평점과 인기도는 데이터셋에 수록된 값입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_notice(message):
    """안내 문구 HTML 렌더링."""
    safe_message = html.escape(str(message))
    st.markdown(
        f'<div class="notice">{safe_message}</div>',
        unsafe_allow_html=True
    )


# ==================================================
# 4. 한국어 영화 제목
# ==================================================

KOREAN_TITLE_MAP = {
    "Avatar": "아바타",
    "Titanic": "타이타닉",
    "The Dark Knight": "다크 나이트",
    "The Dark Knight Rises": "다크 나이트 라이즈",
    "Inception": "인셉션",
    "Interstellar": "인터스텔라",
    "The Avengers": "어벤져스",
    "Avengers: Age of Ultron": "어벤져스: 에이지 오브 울트론",
    "Iron Man": "아이언맨",
    "Iron Man 2": "아이언맨 2",
    "Iron Man 3": "아이언맨 3",
    "Captain America: The First Avenger": "퍼스트 어벤져",
    "Captain America: The Winter Soldier": "캡틴 아메리카: 윈터 솔져",
    "Captain America: Civil War": "캡틴 아메리카: 시빌 워",
    "Guardians of the Galaxy": "가디언즈 오브 갤럭시",
    "Guardians of the Galaxy Vol. 2": "가디언즈 오브 갤럭시 2",
    "Doctor Strange": "닥터 스트레인지",
    "Spider-Man": "스파이더맨",
    "Spider-Man 2": "스파이더맨 2",
    "Spider-Man 3": "스파이더맨 3",
    "The Amazing Spider-Man": "어메이징 스파이더맨",
    "The Amazing Spider-Man 2": "어메이징 스파이더맨 2",
    "Man of Steel": "맨 오브 스틸",
    "Batman Begins": "배트맨 비긴즈",
    "Batman v Superman: Dawn of Justice": "배트맨 대 슈퍼맨: 저스티스의 시작",
    "Suicide Squad": "수어사이드 스쿼드",
    "Wonder Woman": "원더 우먼",
    "Joker": "조커",
    "The Matrix": "매트릭스",
    "The Matrix Reloaded": "매트릭스 2: 리로디드",
    "The Matrix Revolutions": "매트릭스 3: 레볼루션",
    "The Lord of the Rings: The Fellowship of the Ring": "반지의 제왕: 반지 원정대",
    "The Lord of the Rings: The Two Towers": "반지의 제왕: 두 개의 탑",
    "The Lord of the Rings: The Return of the King": "반지의 제왕: 왕의 귀환",
    "The Hobbit: An Unexpected Journey": "호빗: 뜻밖의 여정",
    "Harry Potter and the Philosopher's Stone": "해리 포터와 마법사의 돌",
    "Harry Potter and the Chamber of Secrets": "해리 포터와 비밀의 방",
    "Harry Potter and the Prisoner of Azkaban": "해리 포터와 아즈카반의 죄수",
    "Harry Potter and the Goblet of Fire": "해리 포터와 불의 잔",
    "Harry Potter and the Order of the Phoenix": "해리 포터와 불사조 기사단",
    "Harry Potter and the Half-Blood Prince": "해리 포터와 혼혈 왕자",
    "Harry Potter and the Deathly Hallows: Part 1": "해리 포터와 죽음의 성물 1",
    "Harry Potter and the Deathly Hallows: Part 2": "해리 포터와 죽음의 성물 2",
    "Frozen": "겨울왕국",
    "Frozen II": "겨울왕국 2",
    "Toy Story": "토이 스토리",
    "Toy Story 2": "토이 스토리 2",
    "Toy Story 3": "토이 스토리 3",
    "Finding Nemo": "니모를 찾아서",
    "Finding Dory": "도리를 찾아서",
    "Inside Out": "인사이드 아웃",
    "Up": "업",
    "WALL·E": "월-E",
    "Ratatouille": "라따뚜이",
    "Coco": "코코",
    "Zootopia": "주토피아",
    "The Lion King": "라이온 킹",
    "Beauty and the Beast": "미녀와 야수",
    "Aladdin": "알라딘",
    "The Little Mermaid": "인어공주",
    "Spectre": "007 스펙터",
    "Skyfall": "007 스카이폴",
    "Casino Royale": "007 카지노 로얄",
    "The Fast and the Furious": "분노의 질주",
    "Fast Five": "분노의 질주: 언리미티드",
    "Furious 7": "분노의 질주: 더 세븐",
    "Mad Max: Fury Road": "매드 맥스: 분노의 도로",
    "Gladiator": "글래디에이터",
    "The Wolf of Wall Street": "더 울프 오브 월 스트리트",
    "Forrest Gump": "포레스트 검프",
    "The Shawshank Redemption": "쇼생크 탈출",
    "Pulp Fiction": "펄프 픽션",
    "Fight Club": "파이트 클럽",
    "The Godfather": "대부",
    "The Godfather: Part II": "대부 2",
    "The Green Mile": "그린 마일",
    "The Social Network": "소셜 네트워크",
    "La La Land": "라라랜드",
    "Whiplash": "위플래쉬",
    "The Grand Budapest Hotel": "그랜드 부다페스트 호텔",
    "The Revenant": "레버넌트: 죽음에서 돌아온 자",
    "Django Unchained": "장고: 분노의 추적자",
    "Inglourious Basterds": "바스터즈: 거친 녀석들",
    "Shutter Island": "셔터 아일랜드",
    "Gone Girl": "나를 찾아줘",
    "The Conjuring": "컨저링",
    "The Conjuring 2": "컨저링 2",
    "It": "그것",
    "Get Out": "겟 아웃",
    "The Exorcist": "엑소시스트",
    "The Hangover": "행오버",
    "Home Alone": "나 홀로 집에",
    "The Truman Show": "트루먼 쇼",
    "The Pursuit of Happyness": "행복을 찾아서",
    "The Martian": "마션",
    "Gravity": "그래비티",
    "Arrival": "컨택트",
    "Edge of Tomorrow": "엣지 오브 투모로우",
    "The Day After Tomorrow": "투모로우",
    "Jurassic Park": "쥬라기 공원",
    "Jurassic World": "쥬라기 월드",
    "King Kong": "킹콩",
    "Godzilla": "고질라",
    "Transformers": "트랜스포머",
    "The Hunger Games": "헝거게임",
    "Divergent": "다이버전트",
    "Twilight": "트와일라잇",
    "The Fault in Our Stars": "안녕, 헤이즐",
    "The Notebook": "노트북",
    "Me Before You": "미 비포 유",
    "The Devil Wears Prada": "악마는 프라다를 입는다",
    "The Intern": "인턴",
    "The Greatest Showman": "위대한 쇼맨",
    "Mamma Mia!": "맘마미아!",
    "Les Misérables": "레 미제라블",
    "The Imitation Game": "이미테이션 게임",
    "Life of Pi": "라이프 오브 파이",
    "Slumdog Millionaire": "슬럼독 밀리어네어",
    "Black Swan": "블랙 스완",
    "The Curious Case of Benjamin Button": "벤자민 버튼의 시간은 거꾸로 간다",
    "The Secret Life of Walter Mitty": "월터의 상상은 현실이 된다",
    "The Lego Movie": "레고 무비",
    "Despicable Me": "슈퍼배드",
    "Despicable Me 2": "슈퍼배드 2",
    "Minions": "미니언즈",
    "Shrek": "슈렉",
    "Shrek 2": "슈렉 2",
    "Kung Fu Panda": "쿵푸팬더",
    "Kung Fu Panda 2": "쿵푸팬더 2",
    "How to Train Your Dragon": "드래곤 길들이기",
    "The Incredibles": "인크레더블",
    "Monsters, Inc.": "몬스터 주식회사",
    "Monsters University": "몬스터 대학교",
    "Cars": "카",
    "Cars 2": "카 2",
    "Cars 3": "카 3",
    "The Secret Life of Pets": "마이펫의 이중생활",
    "Sing": "씽",
    "The Boss Baby": "보스 베이비",
    "The Simpsons Movie": "심슨 가족, 더 무비"
}


@st.cache_data(show_spinner=False, ttl=86400)
def translate_title(title):
    title = str(title).strip()

    if title in KOREAN_TITLE_MAP:
        return KOREAN_TITLE_MAP[title]

    if TRANSLATOR_AVAILABLE:
        try:
            result = GoogleTranslator(
                source="auto",
                target="ko"
            ).translate(title)

            if result:
                return result.strip()

        except Exception:
            pass

    return "한국어 번역 준비 중"


# ==================================================
# 5. CSV 불러오기
# ==================================================

@st.cache_data(show_spinner=False)
def load_data(source):
    if isinstance(source, bytes):
        data = pd.read_csv(BytesIO(source))
    else:
        data = pd.read_csv(source)

    required_columns = [
        "title", "genres", "keywords", "overview",
        "vote_average", "vote_count", "popularity",
        "release_date", "budget", "revenue", "runtime"
    ]

    for col in required_columns:
        if col not in data.columns:
            data[col] = np.nan

    numeric_columns = [
        "vote_average", "vote_count", "popularity",
        "budget", "revenue", "runtime"
    ]

    for col in numeric_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data["title"] = data["title"].fillna("제목 없음").astype(str)
    data["overview"] = data["overview"].fillna("").astype(str)

    data["release_date"] = pd.to_datetime(
        data["release_date"],
        errors="coerce"
    )

    data["year"] = data["release_date"].dt.year

    def parse_json_names(value):
        try:
            parsed = (
                ast.literal_eval(value)
                if isinstance(value, str)
                else []
            )

            if isinstance(parsed, list):
                return [
                    str(item.get("name", ""))
                    for item in parsed
                    if isinstance(item, dict)
                    and item.get("name")
                ]

        except (ValueError, SyntaxError, TypeError):
            pass

        return []

    data["genre_list"] = data["genres"].apply(parse_json_names)
    data["keyword_list"] = data["keywords"].apply(parse_json_names)

    data["genre_names"] = data["genre_list"].apply(
        lambda items: " | ".join(items)
    )

    data["keyword_names"] = data["keyword_list"].apply(
        lambda items: " ".join(items)
    )

    data["search_text"] = (
        data["title"].fillna("") + " " +
        data["overview"].fillna("") + " " +
        data["genre_names"].fillna("") + " " +
        data["keyword_names"].fillna("")
    )

    if "id" in data.columns:
        data = data.drop_duplicates(
            subset=["id"],
            keep="first"
        )

    return data.reset_index(drop=True)


CSV_NAME = "tmdb_5000_movies.csv"
base_dir = Path(__file__).resolve().parent

search_locations = [
    base_dir,
    base_dir.parent,
    Path.cwd(),
    Path.cwd().parent
]

for parent in base_dir.parents:
    search_locations.append(parent)

csv_path = None

for folder in dict.fromkeys(search_locations):
    candidate = folder / CSV_NAME

    if candidate.is_file():
        csv_path = candidate
        break

df = None

if csv_path is not None:
    try:
        df = load_data(str(csv_path))
        st.sidebar.success("CSV 자동 연결 완료")
    except Exception as error:
        st.error(f"CSV 읽기 오류: {error}")
        st.stop()

else:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">📁 영화 데이터 연결</div>
        <div class="hero-subtitle">
            CSV 파일을 찾지 못했습니다. 아래에서 업로드해주세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "TMDB 영화 데이터 CSV 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "tmdb_5000_movies.csv 파일을 업로드하면 사이트를 이용할 수 있습니다."
        )
        st.stop()

    try:
        df = load_data(uploaded_file.getvalue())
        st.sidebar.success("업로드 CSV 연결 완료")
    except Exception as error:
        st.error(f"업로드 CSV 읽기 오류: {error}")
        st.stop()


# ==================================================
# 6. 영화 카드 및 상세 정보
# ==================================================

def format_money(value):
    if pd.isna(value) or value <= 0:
        return "정보 없음"
    return f"${value:,.0f}"


def render_movie_card(movie, show_overview=True):
    title = str(movie["title"])
    korean = translate_title(title)

    year = (
        str(int(movie["year"]))
        if pd.notna(movie["year"])
        else "연도 미상"
    )

    rating = (
        f'{movie["vote_average"]:.1f}'
        if pd.notna(movie["vote_average"])
        else "정보 없음"
    )

    genres = movie["genre_names"] or "장르 정보 없음"

    st.markdown(
        f"""
        <div class="movie-card">
            <div class="movie-title">{html.escape(title)}</div>
            <div class="movie-korean">{html.escape(korean)}</div>
            <div class="movie-info">
                📅 개봉 연도: {year}<br>
                ⭐ 평점: {rating}<br>
                🎭 장르: {html.escape(genres)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    overview = str(movie["overview"])

    if show_overview and overview.strip():
        with st.expander("영화 줄거리 보기"):
            st.write(overview)


def movie_detail(movie):
    title = str(movie["title"])
    korean = translate_title(title)

    st.markdown(f"# {title}")

    st.markdown(
        f"<h3 style='color:#FFD166 !important;'>{html.escape(korean)}</h3>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "평점",
        f'{movie["vote_average"]:.1f}'
        if pd.notna(movie["vote_average"])
        else "-"
    )

    c2.metric(
        "인기도",
        f'{movie["popularity"]:.1f}'
        if pd.notna(movie["popularity"])
        else "-"
    )

    c3.metric(
        "투표 수",
        f'{movie["vote_count"]:,.0f}'
        if pd.notna(movie["vote_count"])
        else "-"
    )

    st.markdown("### 🎭 영화 정보")
    st.write(f"**장르:** {movie['genre_names'] or '정보 없음'}")

    if pd.notna(movie["release_date"]):
        st.write(f"**개봉일:** {movie['release_date'].date()}")
    else:
        st.write("**개봉일:** 정보 없음")

    if pd.notna(movie["runtime"]):
        st.write(f"**상영 시간:** {movie['runtime']:.0f}분")
    else:
        st.write("**상영 시간:** 정보 없음")

    st.write(f"**제작비:** {format_money(movie['budget'])}")
    st.write(f"**수익:** {format_money(movie['revenue'])}")

    st.markdown("### 📖 줄거리")
    st.write(movie["overview"] or "줄거리 정보가 없습니다.")

    if "homepage" in movie.index:
        homepage = movie["homepage"]

        if pd.notna(homepage) and str(homepage).strip():
            st.markdown(f"[🌐 공식 홈페이지 바로가기]({homepage})")


# ==================================================
# 7. AI 추천 알고리즘
# ==================================================

@st.cache_resource
def train_recommender(text_data):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=12000,
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(text_data)

    return matrix


def get_recommendations(movie_index, number=100):
    text_data = tuple(df["search_text"].tolist())
    matrix = train_recommender(text_data)

    similarity = cosine_similarity(
        matrix[movie_index],
        matrix
    ).flatten()

    similarity[movie_index] = -1

    indices = similarity.argsort()[::-1][:number]

    return indices, similarity[indices]


# ==================================================
# 8. 사이드바
# ==================================================

st.sidebar.markdown("# 🎬 CINE AI")
st.sidebar.caption("AI 영화 분석 및 추천 플랫폼")
st.sidebar.divider()

page = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 메인 대시보드",
        "🤖 AI 영화 추천",
        "📊 데이터 분석",
        "🔎 영화 탐색"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### 📁 데이터 정보")
st.sidebar.write(f"🎞️ 전체 영화: {len(df):,}편")
st.sidebar.write("📊 TMDB 5000 Movies Dataset")


# ==================================================
# 9. 메인 대시보드
# ==================================================

if page == "🏠 메인 대시보드":

    st.markdown("""
    <div class="hero">
        <div class="hero-title">🎬 CINE AI</div>
        <div class="hero-subtitle">
            영화 데이터를 분석하고, 나에게 맞는 영화를 발견해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_movies = len(df)
    avg_rating = df["vote_average"].mean()

    total_genres = len({
        genre
        for genres in df["genre_list"]
        for genre in genres
    })

    total_votes = df["vote_count"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("전체 영화", f"{total_movies:,}편")
    c2.metric("평균 평점", f"{avg_rating:.2f}점")
    c3.metric("장르 종류", f"{total_genres}개")
    c4.metric("전체 투표 수", f"{total_votes:,.0f}")

    st.divider()

    st.markdown(
        '<div class="section-title">🔥 인기 영화 TOP 10</div>',
        unsafe_allow_html=True
    )

    popular = df.sort_values(
        "popularity",
        ascending=False
    ).head(10)

    cols = st.columns(2)

    for i, (_, movie) in enumerate(popular.iterrows()):
        with cols[i % 2]:
            render_movie_card(movie, False)

    st.divider()

    st.markdown(
        '<div class="section-title">🏆 평점 높은 영화 TOP 10</div>',
        unsafe_allow_html=True
    )

    highly_rated = df[
        df["vote_count"] >= 100
    ].sort_values(
        "vote_average",
        ascending=False
    ).head(10)

    cols = st.columns(2)

    for i, (_, movie) in enumerate(highly_rated.iterrows()):
        with cols[i % 2]:
            render_movie_card(movie, False)


# ==================================================
# 10. AI 영화 추천
# ==================================================

elif page == "🤖 AI 영화 추천":

    st.markdown("# 🤖 AI 영화 추천")

    show_notice(
        "영화의 장르, 키워드, 줄거리 정보를 분석해 비슷한 영화를 추천합니다."
    )

    movie_titles = sorted(df["title"].unique().tolist())

    selected_title = st.selectbox(
        "좋아하는 영화를 선택하세요.",
        movie_titles
    )

    selected_movie = df[
        df["title"] == selected_title
    ].iloc[0]

    selected_index = int(selected_movie.name)

    st.markdown(f"### 🎥 {selected_title}")

    st.markdown(
        f"<h3 style='color:#FFD166 !important;'>{html.escape(translate_title(selected_title))}</h3>",
        unsafe_allow_html=True
    )

    st.write(f"**장르:** {selected_movie['genre_names'] or '정보 없음'}")

    all_genres = sorted({
        genre
        for genres in df["genre_list"]
        for genre in genres
    })

    selected_genres = st.multiselect(
        "추천받고 싶은 장르를 선택하세요.",
        all_genres
    )

    number = st.slider(
        "추천 영화 개수",
        min_value=3,
        max_value=15,
        value=6
    )

    if st.button("✨ AI 영화 추천 시작", use_container_width=True):

        with st.spinner("영화를 분석하고 있습니다..."):

            indices, scores = get_recommendations(
                selected_index,
                number=100
            )

            recommendations = df.iloc[indices].copy()
            recommendations["similarity"] = scores

            if selected_genres:
                recommendations = recommendations[
                    recommendations["genre_list"].apply(
                        lambda genres: any(
                            genre in genres
                            for genre in selected_genres
                        )
                    )
                ]

            recommendations = recommendations.head(number)

        if recommendations.empty:
            st.warning("조건에 맞는 영화가 없습니다. 장르를 변경해 보세요.")

        else:
            st.success(f"{len(recommendations)}개의 영화를 찾았습니다!")

            cols = st.columns(2)

            for i, (_, movie) in enumerate(recommendations.iterrows()):
                with cols[i % 2]:
                    render_movie_card(movie)

                    score = float(movie["similarity"])

                    st.progress(
                        max(0.0, min(score, 1.0)),
                        text=f"영화 유사도 {score * 100:.1f}%"
                    )

    st.caption(
        "추천 알고리즘: TF-IDF와 코사인 유사도를 이용한 콘텐츠 기반 추천"
    )


# ==================================================
# 11. 데이터 분석
# ==================================================

elif page == "📊 데이터 분석":

    st.markdown("# 📊 영화 데이터 분석")

    show_notice(
        "TMDB 영화 데이터를 장르, 평점, 개봉 연도, 제작비와 수익 관점에서 분석합니다."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎭 장르 분석",
        "⭐ 평점 분석",
        "📅 연도 분석",
        "💰 수익 분석"
    ])

    genre_expanded = df.explode("genre_list").copy()
    genre_expanded["genre"] = genre_expanded["genre_list"]

    genre_expanded = genre_expanded[
        genre_expanded["genre"].notna()
        & (genre_expanded["genre"] != "")
    ]

    # 장르 분석
    with tab1:

        st.markdown("### 장르별 영화 수")

        genre_counts = (
            genre_expanded["genre"]
            .value_counts()
            .reset_index()
        )

        genre_counts.columns = ["장르", "영화 수"]

        fig = px.bar(
            genre_counts,
            x="영화 수",
            y="장르",
            orientation="h",
            color="영화 수",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )

        fig.update_layout(
            height=600,
            yaxis={"categoryorder": "total ascending"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 장르별 평균 평점")

        genre_rating = (
            genre_expanded.groupby("genre")["vote_average"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        genre_rating.columns = ["장르", "평균 평점"]

        fig = px.bar(
            genre_rating,
            x="장르",
            y="평균 평점",
            color="평균 평점",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            xaxis_tickangle=-35
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(genre_counts, use_container_width=True, hide_index=True)

    # 평점 분석
    with tab2:

        st.markdown("### 영화 평점 분포")

        rating_data = df.dropna(subset=["vote_average"])

        fig = px.histogram(
            rating_data,
            x="vote_average",
            nbins=20,
            color_discrete_sequence=["#A78BFA"],
            template="plotly_dark"
        )

        fig.update_layout(
            xaxis_title="평점",
            yaxis_title="영화 수",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 인기도와 평점의 관계")

        scatter_data = df.dropna(
            subset=["popularity", "vote_average"]
        )

        fig = px.scatter(
            scatter_data,
            x="popularity",
            y="vote_average",
            hover_name="title",
            color="vote_average",
            color_continuous_scale="Plasma",
            template="plotly_dark"
        )

        fig.update_layout(
            xaxis_title="인기도",
            yaxis_title="평점",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

    # 연도 분석
    with tab3:

        st.markdown("### 연도별 영화 개봉 수")

        yearly = (
            df.dropna(subset=["year"])
            .groupby("year")
            .agg(
                영화수=("title", "count"),
                평균평점=("vote_average", "mean")
            )
            .reset_index()
        )

        yearly["year"] = yearly["year"].astype(int)

        fig = px.line(
            yearly,
            x="year",
            y="영화수",
            markers=True,
            color_discrete_sequence=["#C4B5FD"],
            template="plotly_dark"
        )

        fig.update_layout(
            xaxis_title="개봉 연도",
            yaxis_title="영화 수",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 연도별 평균 평점")

        fig = px.line(
            yearly,
            x="year",
            y="평균평점",
            markers=True,
            color_discrete_sequence=["#F9A8D4"],
            template="plotly_dark"
        )

        fig.update_layout(
            xaxis_title="개봉 연도",
            yaxis_title="평균 평점",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            yearly.sort_values("year", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    # 수익 분석
    with tab4:

        st.markdown("### 제작비와 수익의 관계")

        money_data = df[
            (df["budget"] > 0)
            & (df["revenue"] > 0)
        ].copy()

        if not money_data.empty:

            fig = px.scatter(
                money_data,
                x="budget",
                y="revenue",
                hover_name="title",
                color="vote_average",
                color_continuous_scale="Viridis",
                template="plotly_dark"
            )

            fig.update_layout(
                xaxis_title="제작비 ($)",
                yaxis_title="수익 ($)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("제작비와 수익 데이터가 없습니다.")

        st.markdown("### 수익 TOP 10")

        top_revenue = (
            df[df["revenue"] > 0]
            .sort_values("revenue", ascending=False)
            .head(10)
        )

        if not top_revenue.empty:

            fig = px.bar(
                top_revenue,
                x="revenue",
                y="title",
                orientation="h",
                color="revenue",
                color_continuous_scale="Teal",
                template="plotly_dark"
            )

            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="수익 ($)",
                yaxis_title="영화",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                top_revenue[
                    ["title", "revenue", "vote_average"]
                ],
                use_container_width=True,
                hide_index=True
            )


# ==================================================
# 12. 영화 탐색
# ==================================================

elif page == "🔎 영화 탐색":

    st.markdown("# 🔎 영화 탐색")

    show_notice(
        "영화 제목을 검색하고 장르와 평점을 설정해 원하는 영화를 찾아보세요."
    )

    search = st.text_input(
        "영화 제목 검색",
        placeholder="예: Avatar, Titanic, Inception"
    )

    all_genres = sorted({
        genre
        for genres in df["genre_list"]
        for genre in genres
    })

    c1, c2 = st.columns(2)

    with c1:
        selected_genre = st.selectbox(
            "장르 선택",
            ["전체"] + all_genres
        )

    with c2:
        min_rating = st.slider(
            "최소 평점",
            0.0,
            10.0,
            0.0,
            0.5
        )

    filtered = df.copy()

    if search.strip():
        filtered = filtered[
            filtered["title"].str.contains(
                search.strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    if selected_genre != "전체":
        filtered = filtered[
            filtered["genre_list"].apply(
                lambda genres: selected_genre in genres
            )
        ]

    filtered = filtered[
        filtered["vote_average"].fillna(0) >= min_rating
    ]

    sort_option = st.selectbox(
        "정렬 방식",
        [
            "인기도 높은 순",
            "평점 높은 순",
            "개봉 연도 최신 순",
            "투표 수 많은 순"
        ]
    )

    sort_columns = {
        "인기도 높은 순": "popularity",
        "평점 높은 순": "vote_average",
        "개봉 연도 최신 순": "year",
        "투표 수 많은 순": "vote_count"
    }

    filtered = filtered.sort_values(
        sort_columns[sort_option],
        ascending=False
    )

    st.markdown(f"### 검색 결과: {len(filtered):,}편")

    if filtered.empty:

        st.warning("검색 결과가 없습니다.")

    else:

        selected_movie_title = st.selectbox(
            "상세 정보를 확인할 영화 선택",
            filtered["title"].tolist()
        )

        selected_movie = filtered[
            filtered["title"] == selected_movie_title
        ].iloc[0]

        st.divider()
        movie_detail(selected_movie)

        st.divider()
        st.markdown("### 🎞️ 검색 결과 목록")

        display_count = st.slider(
            "표시할 영화 수",
            5,
            30,
            10
        )

        display_movies = filtered.head(display_count)

        cols = st.columns(2)

        for i, (_, movie) in enumerate(display_movies.iterrows()):
            with cols[i % 2]:
                render_movie_card(movie)


# ==================================================
# 13. 모든 메뉴에서 공통 하단 문구
# ==================================================

st.divider()
show_footer()
