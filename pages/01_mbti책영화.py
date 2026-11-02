
import streamlit as st
import html

st.set_page_config(
    page_title="LOVE LETTER | MBTI ROMANCE",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# 🎨 디자인 CSS
# -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Playfair+Display:wght@500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #fff5f7 0%, #fffaf3 50%, #fcecf2 100%);
    font-family: 'Gowun Dodum', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero {
    background: linear-gradient(125deg, #e99caf, #d98ca9, #b98ba9);
    border-radius: 30px;
    padding: 65px 30px;
    text-align: center;
    color: white;
    box-shadow: 0 15px 40px rgba(183, 113, 143, 0.2);
    margin-bottom: 35px;
}

.hero-label {
    font-size: 12px;
    letter-spacing: 5px;
    opacity: 0.9;
    margin-bottom: 20px;
}

.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(40px, 7vw, 68px);
    font-weight: 700;
    margin: 0;
    color: white;
    letter-spacing: 2px;
}

.hero p {
    font-size: 16px;
    line-height: 1.8;
    margin-top: 20px;
    color: #fff9fb;
}

.hero-heart {
    font-size: 35px;
    margin-bottom: 12px;
}

.section-title {
    text-align: center;
    color: #92546f;
    font-size: 27px;
    font-weight: bold;
    margin-top: 40px;
    margin-bottom: 10px;
}

.section-subtitle {
    text-align: center;
    color: #aa8796;
    font-size: 14px;
    margin-bottom: 30px;
}

.info-box {
    background: rgba(255,255,255,0.75);
    border: 1px solid #f2dce5;
    border-radius: 22px;
    padding: 23px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(180,120,145,0.07);
}

.info-number {
    color: #c47b99;
    font-size: 27px;
    font-weight: bold;
}

.info-text {
    color: #927482;
    font-size: 13px;
}

.book-card {
    background: rgba(255,255,255,0.9);
    border: 1px solid #f1dce4;
    border-radius: 22px;
    padding: 27px;
    min-height: 235px;
    box-shadow: 0 8px 25px rgba(170,100,130,0.08);
    transition: all 0.3s ease;
    margin-bottom: 15px;
}

.book-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 30px rgba(170,100,130,0.17);
    border-color: #dba1b7;
}

.card-tag {
    display: inline-block;
    background: #fceaf0;
    color: #b76e8b;
    border-radius: 30px;
    padding: 6px 13px;
    font-size: 11px;
    letter-spacing: 1px;
    margin-bottom: 17px;
}

.card-title {
    color: #75465b;
    font-size: 23px;
    font-weight: bold;
    line-height: 1.5;
    margin-bottom: 8px;
}

.card-author {
    color: #b17e93;
    font-size: 13px;
    margin-bottom: 20px;
}

.card-description {
    color: #806d76;
    font-size: 14px;
    line-height: 1.9;
}

.movie-card {
    background: linear-gradient(145deg, #fff, #fff2f6);
    border: 1px solid #efd6e0;
    border-radius: 22px;
    padding: 27px;
    min-height: 235px;
    box-shadow: 0 8px 25px rgba(170,100,130,0.08);
    transition: all 0.3s ease;
    margin-bottom: 15px;
}

.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 30px rgba(170,100,130,0.17);
}

.movie-number {
    font-family: 'Playfair Display', serif;
    color: #d7a2b6;
    font-size: 37px;
    margin-bottom: 5px;
}

.result-banner {
    background: linear-gradient(120deg, #f8e3eb, #fff1f3);
    border: 1px solid #efd2df;
    border-radius: 22px;
    padding: 25px;
    text-align: center;
    margin: 25px 0;
}

.result-banner h2 {
    color: #92546f;
    font-size: 30px;
    margin: 5px;
}

.result-banner p {
    color: #a77b8e;
    font-size: 14px;
}

.footer {
    text-align: center;
    color: #b18b9c;
    font-size: 12px;
    padding: 35px 0 10px;
    letter-spacing: 1px;
    line-height: 2;
}

.stButton > button {
    background: linear-gradient(120deg, #d98da9, #bd7898);
    color: white;
    border: none;
    border-radius: 15px;
    height: 55px;
    font-size: 17px;
    font-weight: bold;
    box-shadow: 0 7px 18px rgba(185,110,145,0.22);
    transition: 0.25s;
}

.stButton > button:hover {
    background: linear-gradient(120deg, #c77898, #a96788);
    transform: translateY(-3px);
    color: white;
    border: none;
}

div[data-baseweb="select"] > div {
    background: white;
    border: 1px solid #e9cbd7;
    border-radius: 13px;
}

.stTabs [data-baseweb="tab"] {
    color: #986b80;
    font-weight: bold;
}

.stTabs [aria-selected="true"] {
    color: #c47796 !important;
}

@media (max-width: 600px) {
    .hero {
        padding: 45px 15px;
    }
    .hero p {
        font-size: 13px;
    }
    .book-card, .movie-card {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# 📚 MBTI 추천 데이터
# -----------------------------

data = {
    "INFP": {
        "books": [
            ("오늘 밤, 세계에서 이 사랑이 사라진다 해도", "이치조 미사키", "매일 기억을 잃는 소녀와 그녀를 사랑하는 소년의 애틋한 이야기."),
            ("오만과 편견", "제인 오스틴", "서로에 대한 오해를 넘어 진정한 사랑을 발견하는 클래식 로맨스.")
        ],
        "movies": [
            ("플립", "미국", "풋풋한 첫사랑과 설렘을 담은 사랑스러운 영화."),
            ("라라랜드", "미국", "꿈과 사랑 사이에서 고민하는 두 사람의 아름다운 이야기.")
        ]
    },
    "INFJ": {
        "books": [
            ("너의 췌장을 먹고 싶어", "스미노 요루", "삶과 사랑의 의미를 생각하게 만드는 애틋한 이야기."),
            ("작은 아씨들", "루이자 메이 올컷", "사랑과 꿈, 가족의 소중함을 담은 따뜻한 소설.")
        ],
        "movies": [
            ("이프 온리", "미국", "사랑하는 사람의 소중함을 깨닫게 해주는 감동적인 로맨스."),
            ("비포 선라이즈", "미국", "하룻밤 동안 깊은 대화를 나누며 가까워지는 두 사람.")
        ]
    },
    "INTP": {
        "books": [
            ("노르웨이의 숲", "무라카미 하루키", "청춘과 사랑, 상실에 관한 깊은 감성의 이야기."),
            ("오만과 편견", "제인 오스틴", "인물들의 심리와 관계 변화가 매력적인 고전.")
        ],
        "movies": [
            ("이터널 선샤인", "미국", "기억을 지워도 사랑은 남을 수 있을까? 독특한 로맨스."),
            ("어바웃 타임", "영국", "시간 여행을 통해 사랑과 일상의 소중함을 알아가는 영화.")
        ]
    },
    "INTJ": {
        "books": [
            ("제인 에어", "샬럿 브론테", "자신의 신념과 사랑을 지켜 나가는 주인공의 이야기."),
            ("오만과 편견", "제인 오스틴", "서로 다른 두 사람이 편견을 넘어 사랑에 빠지는 소설.")
        ],
        "movies": [
            ("시간을 달리는 소녀", "일본", "시간을 되돌릴 수 있는 소녀의 청춘과 사랑."),
            ("어바웃 타임", "영국", "사랑과 인생의 의미를 생각하게 만드는 영화.")
        ]
    },
    "ENFP": {
        "books": [
            ("달러구트 꿈 백화점", "이미예", "상상력 가득한 세계와 따뜻한 감성을 담은 이야기."),
            ("오늘 밤, 세계에서 이 사랑이 사라진다 해도", "이치조 미사키", "설렘과 슬픔이 함께하는 청춘 로맨스.")
        ],
        "movies": [
            ("플립", "미국", "귀엽고 풋풋한 첫사랑의 설렘을 느낄 수 있는 영화."),
            ("맘마미아!", "미국", "신나는 음악과 사랑, 웃음이 가득한 영화.")
        ]
    },
    "ENFJ": {
        "books": [
            ("아몬드", "손원평", "감정과 공감, 사람 사이의 관계를 생각하게 하는 소설."),
            ("작은 아씨들", "루이자 메이 올컷", "가족과 사랑, 꿈을 향한 성장을 그린 작품.")
        ],
        "movies": [
            ("노팅 힐", "영국", "평범한 서점 주인과 유명 배우의 사랑 이야기."),
            ("이프 온리", "미국", "사랑하는 사람의 소중함을 깨닫게 하는 영화.")
        ]
    },
    "ENTP": {
        "books": [
            ("오만과 편견", "제인 오스틴", "재치 있는 대화와 흥미로운 인물 관계가 매력적인 소설."),
            ("위대한 개츠비", "F. 스콧 피츠제럴드", "화려한 사랑과 욕망, 꿈을 담은 고전.")
        ],
        "movies": [
            ("500일의 썸머", "미국", "사랑에 대한 서로 다른 관점을 보여주는 영화."),
            ("이터널 선샤인", "미국", "독특한 설정으로 사랑의 의미를 묻는 작품.")
        ]
    },
    "ENTJ": {
        "books": [
            ("제인 에어", "샬럿 브론테", "자신의 가치와 사랑을 지키는 강인한 주인공의 이야기."),
            ("오만과 편견", "제인 오스틴", "당당한 두 인물이 서로를 이해해 가는 로맨스.")
        ],
        "movies": [
            ("라라랜드", "미국", "꿈을 향해 달려가는 두 사람의 사랑과 선택."),
            ("비긴 어게인", "미국", "음악을 통해 새로운 시작을 맞이하는 사람들의 이야기.")
        ]
    },
    "ISFP": {
        "books": [
            ("어린 왕자", "생텍쥐페리", "사랑과 관계의 소중함을 감성적으로 그린 작품."),
            ("나는 나로 살기로 했다", "김수현", "자신의 마음을 돌아보고 위로받을 수 있는 책.")
        ],
        "movies": [
            ("너의 이름은.", "일본", "운명처럼 연결된 두 사람의 신비로운 사랑."),
            ("플립", "미국", "따뜻하고 귀여운 첫사랑 이야기.")
        ]
    },
    "ISFJ": {
        "books": [
            ("나미야 잡화점의 기적", "히가시노 게이고", "사람들 사이의 따뜻한 인연과 마음을 그린 소설."),
            ("작은 아씨들", "루이자 메이 올컷", "가족과 우정, 사랑의 소중함을 담은 작품.")
        ],
        "movies": [
            ("노트북", "미국", "오랜 시간 이어지는 사랑을 그린 감동적인 영화."),
            ("건축학개론", "한국", "첫사랑의 추억과 아련한 감정을 담은 작품.")
        ]
    },
    "ISTP": {
        "books": [
            ("완득이", "김려령", "유쾌하고 솔직한 청춘의 성장 이야기."),
            ("오만과 편견", "제인 오스틴", "서로 티격태격하다 사랑을 발견하는 이야기.")
        ],
        "movies": [
            ("500일의 썸머", "미국", "현실적인 연애와 사랑의 여러 모습을 보여주는 영화."),
            ("비긴 어게인", "미국", "음악과 새로운 인연이 만들어 내는 따뜻한 이야기.")
        ]
    },
    "ISTJ": {
        "books": [
            ("위대한 개츠비", "F. 스콧 피츠제럴드", "사랑과 꿈, 인간의 욕망을 그린 고전 소설."),
            ("오만과 편견", "제인 오스틴", "오해를 넘어 서로를 이해하게 되는 사랑 이야기.")
        ],
        "movies": [
            ("어바웃 타임", "영국", "일상의 소중함과 사랑을 알려주는 영화."),
            ("노팅 힐", "영국", "서로 다른 삶을 살아가는 두 사람의 로맨스.")
        ]
    },
    "ESFP": {
        "books": [
            ("작은 아씨들", "루이자 메이 올컷", "다양한 인물들의 사랑과 성장 이야기."),
            ("위대한 개츠비", "F. 스콧 피츠제럴드", "화려하고 강렬한 사랑을 담은 소설.")
        ],
        "movies": [
            ("맘마미아!", "미국", "신나는 음악과 유쾌한 사랑이 가득한 영화."),
            ("플립", "미국", "풋풋하고 사랑스러운 첫사랑 이야기.")
        ]
    },
    "ESFJ": {
        "books": [
            ("나미야 잡화점의 기적", "히가시노 게이고", "따뜻한 마음과 사람들의 인연을 담은 작품."),
            ("작은 아씨들", "루이자 메이 올컷", "가족과 사랑, 서로를 향한 애정을 그린 소설.")
        ],
        "movies": [
            ("노트북", "미국", "한 사람을 향한 오랜 사랑을 보여주는 영화."),
            ("노팅 힐", "영국", "설레고 따뜻한 만남을 그린 로맨스.")
        ]
    },
    "ESTP": {
        "books": [
            ("오만과 편견", "제인 오스틴", "재치 있는 인물들의 티격태격 로맨스."),
            ("위대한 개츠비", "F. 스콧 피츠제럴드", "화려한 사랑과 욕망을 담은 이야기.")
        ],
        "movies": [
            ("타이타닉", "미국", "운명적인 만남과 강렬한 사랑을 담은 영화."),
            ("라라랜드", "미국", "꿈과 사랑이 어우러진 화려한 뮤지컬 로맨스.")
        ]
    },
    "ESTJ": {
        "books": [
            ("제인 에어", "샬럿 브론테", "자신의 가치관과 사랑을 지켜 나가는 이야기."),
            ("오만과 편견", "제인 오스틴", "편견을 넘어 진정한 사랑을 발견하는 소설.")
        ],
        "movies": [
            ("건축학개론", "한국", "첫사랑의 설렘과 아련한 추억을 담은 영화."),
            ("어바웃 타임", "영국", "사랑과 가족, 일상의 소중함을 보여주는 영화.")
        ]
    }
}


# -----------------------------
# 🏠 메인 화면
# -----------------------------

st.markdown("""
<div class="hero">
    <div class="hero-heart">♡</div>
    <div class="hero-label">THE ROMANCE COLLECTION</div>
    <h1>LOVE LETTER</h1>
    <p>
        당신의 MBTI가 좋아할 만한 이야기<br>
        책과 영화로 만나는 특별한 로맨스
    </p>
    <div style="font-size:12px; letter-spacing:3px; margin-top:25px;">
        FIND YOUR ROMANCE · 2026
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# 💌 소개 카드
# -----------------------------

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="info-box">
        <div class="info-number">16</div>
        <div class="info-text">MBTI TYPES</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info-box">
        <div class="info-number">02</div>
        <div class="info-text">ROMANCE BOOKS</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="info-box">
        <div class="info-number">02</div>
        <div class="info-text">ROMANCE MOVIES</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# 💗 MBTI 선택
# -----------------------------

st.markdown("""
<div class="section-title">Find Your Romance ♡</div>
<div class="section-subtitle">
당신의 MBTI를 선택하고 나만의 로맨스를 발견해 보세요.
</div>
""", unsafe_allow_html=True)

mbti_types = [
    "INFP", "INFJ", "ENFP", "ENFJ",
    "INTP", "INTJ", "ENTP", "ENTJ",
    "ISFP", "ISFJ", "ESFP", "ESFJ",
    "ISTP", "ISTJ", "ESTP", "ESTJ"
]

mbti = st.selectbox(
    "💌 당신의 MBTI는 무엇인가요?",
    mbti_types,
    index=0
)

if st.button("♡ 나의 로맨스 찾기 ♡", use_container_width=True):

    st.session_state["show_result"] = True
    st.session_state["selected_mbti"] = mbti

# -----------------------------
# 💕 추천 결과
# -----------------------------

if st.session_state.get("show_result", False):

    selected = st.session_state["selected_mbti"]
    result = data[selected]

    st.markdown("""
    <div class="result-banner">
        <div style="font-size:30px;">💌</div>
        <p>YOUR PERSONAL ROMANCE COLLECTION</p>
        <h2>♡ """ + selected + """ ♡</h2>
        <p>당신의 감성에 어울리는 작품들을 준비했어요.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📚 BOOK COLLECTION", "🎬 MOVIE COLLECTION"])

    with tab1:

        st.markdown("""
        <div class="section-title">Books for You</div>
        <div class="section-subtitle">당신의 마음을 채워줄 두 권의 책</div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)

        for i, book in enumerate(result["books"]):
            title, author, desc = book

            with cols[i]:
                st.markdown(f"""
                <div class="book-card">
                    <div class="card-tag">BOOK NO. 0{i+1}</div>
                    <div class="card-title">♡ {html.escape(title)}</div>
                    <div class="card-author">✍️ {html.escape(author)}</div>
                    <div class="card-description">
                        {html.escape(desc)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:

        st.markdown("""
        <div class="section-title">Movies for You</div>
        <div class="section-subtitle">당신의 하루를 특별하게 만들어 줄 두 편의 영화</div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)

        for i, movie in enumerate(result["movies"]):
            title, country, desc = movie

            with cols[i]:
                st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-number">0{i+1}.</div>
                    <div class="card-tag">MOVIE COLLECTION</div>
                    <div class="card-title">♡ {html.escape(title)}</div>
                    <div class="card-author">🎞️ {html.escape(country)}</div>
                    <div class="card-description">
                        {html.escape(desc)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("""
    <div class="result-banner">
        <div style="font-size:28px;">🌷</div>
        <h2>Make Your Day Romantic</h2>
        <p>오늘 하루, 당신만의 특별한 이야기를 만나보세요.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↻ 다른 MBTI 다시 선택하기", use_container_width=True):
        st.session_state["show_result"] = False
        st.rerun()


# -----------------------------
# 🌸 하단
# -----------------------------

st.markdown("""
<div class="footer">
    ♡ LOVE LETTER ♡<br>
    YOUR PERSONAL ROMANCE COLLECTION<br><br>
    Made with LOVE · 2026<br>
    MBTI 추천은 재미를 위한 콘텐츠입니다.
</div>
""", unsafe_allow_html=True)
