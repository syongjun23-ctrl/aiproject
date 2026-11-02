
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import html

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="SEOUL SPOTLIGHT",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# 관광지 데이터
# -----------------------------
PLACES = [
    {
        "name": "명동",
        "eng": "MYEONG-DONG",
        "category": "쇼핑",
        "emoji": "🛍️",
        "lat": 37.5636,
        "lon": 126.9850,
        "desc": "다양한 쇼핑 매장과 길거리 음식, 화장품 매장이 가득한 서울 대표 관광 거리.",
        "tip": "길거리 음식과 쇼핑을 함께 즐겨보세요."
    },
    {
        "name": "N서울타워",
        "eng": "N SEOUL TOWER",
        "category": "랜드마크",
        "emoji": "🗼",
        "lat": 37.5512,
        "lon": 126.9882,
        "desc": "남산 정상에 위치한 서울의 대표 랜드마크. 아름다운 서울의 전경을 감상할 수 있어요.",
        "tip": "해 질 무렵 방문하면 멋진 야경을 볼 수 있어요."
    },
    {
        "name": "코엑스",
        "eng": "COEX",
        "category": "문화",
        "emoji": "🏙️",
        "lat": 37.5125,
        "lon": 127.0588,
        "desc": "대형 쇼핑몰과 아쿠아리움, 별마당도서관이 있는 복합 문화 공간.",
        "tip": "별마당도서관에서 인증 사진을 남겨보세요."
    },
    {
        "name": "강남역",
        "eng": "GANGNAM",
        "category": "쇼핑",
        "emoji": "💎",
        "lat": 37.4979,
        "lon": 127.0276,
        "desc": "세련된 상점과 맛집, 카페가 모여 있는 서울의 대표 번화가.",
        "tip": "한국의 최신 패션과 트렌드를 구경해 보세요."
    },
    {
        "name": "홍대",
        "eng": "HONGDAE",
        "category": "문화",
        "emoji": "🎸",
        "lat": 37.5563,
        "lon": 126.9236,
        "desc": "개성 있는 카페와 거리 공연, 예술 문화가 어우러진 젊음의 거리.",
        "tip": "주말 저녁 거리 공연을 구경해 보세요."
    },
    {
        "name": "경복궁",
        "eng": "GYEONGBOKGUNG",
        "category": "역사",
        "emoji": "🏯",
        "lat": 37.5796,
        "lon": 126.9770,
        "desc": "조선 왕조의 대표 궁궐로 한국의 전통 건축과 역사를 느낄 수 있는 장소.",
        "tip": "한복을 입고 방문하면 더욱 특별한 추억을 만들 수 있어요."
    },
    {
        "name": "동대문디자인플라자",
        "eng": "DDP",
        "category": "건축",
        "emoji": "✨",
        "lat": 37.5671,
        "lon": 127.0095,
        "desc": "독특하고 미래적인 건축 디자인으로 유명한 서울의 문화 공간.",
        "tip": "건물 외관과 야간 조명을 감상해 보세요."
    },
    {
        "name": "광장시장",
        "eng": "GWANGJANG MARKET",
        "category": "먹거리",
        "emoji": "🍜",
        "lat": 37.5701,
        "lon": 126.9997,
        "desc": "빈대떡, 마약김밥, 육회 등 다양한 한국 음식을 맛볼 수 있는 전통시장.",
        "tip": "여러 가지 시장 음식을 조금씩 맛보는 것을 추천해요."
    },
    {
        "name": "북촌한옥마을",
        "eng": "BUKCHON HANOK VILLAGE",
        "category": "역사",
        "emoji": "🏘️",
        "lat": 37.5826,
        "lon": 126.9830,
        "desc": "전통 한옥이 아름답게 보존되어 있는 서울의 대표적인 전통 마을.",
        "tip": "주민들이 거주하는 곳이니 조용히 관람해 주세요."
    },
    {
        "name": "성수동",
        "eng": "SEONGSU",
        "category": "트렌드",
        "emoji": "☕",
        "lat": 37.5445,
        "lon": 127.0560,
        "desc": "감각적인 카페와 팝업스토어, 편집숍이 모여 있는 서울의 핫플레이스.",
        "tip": "개성 있는 카페와 팝업스토어를 구경해 보세요."
    }
]

# -----------------------------
# 디자인 CSS
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Noto Sans KR', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(40, 90, 150, 0.18), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(190, 145, 70, 0.10), transparent 25%),
        #080D18;
    color: #F5F6FA;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.hero {
    padding: 45px 35px;
    border-radius: 25px;
    background: linear-gradient(125deg, #17243A 0%, #101827 55%, #202A3B 100%);
    border: 1px solid rgba(255,255,255,0.09);
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
}

.hero:after {
    content: "SEOUL";
    position: absolute;
    right: -15px;
    bottom: -45px;
    font-size: 130px;
    font-weight: 900;
    letter-spacing: -8px;
    color: rgba(255,255,255,0.035);
}

.eyebrow {
    color: #D7B878;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 4px;
    margin-bottom: 15px;
}

.hero h1 {
    color: #FFFFFF;
    font-size: clamp(38px, 6vw, 66px);
    font-weight: 900;
    letter-spacing: -3px;
    line-height: 1.05;
    margin: 0;
}

.hero p {
    color: #B9C2D0;
    font-size: 15px;
    margin-top: 17px;
    line-height: 1.8;
}

.gold {
    color: #E5C27B;
}

.section-title {
    font-size: 25px;
    font-weight: 900;
    color: #F6F7FB;
    margin: 35px 0 5px 0;
    letter-spacing: -1px;
}

.section-sub {
    color: #8D9AAF;
    font-size: 13px;
    margin-bottom: 20px;
}

.stat-card {
    background: linear-gradient(145deg, #172235, #111927);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 17px;
    padding: 20px;
    min-height: 105px;
}

.stat-number {
    font-size: 28px;
    font-weight: 900;
    color: #E5C27B;
}

.stat-label {
    color: #AAB5C5;
    font-size: 12px;
    margin-top: 5px;
}

.place-card {
    background: linear-gradient(145deg, #172235, #101724);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 17px;
    padding: 19px;
    min-height: 205px;
    margin-bottom: 12px;
    transition: 0.2s;
}

.place-card:hover {
    border-color: rgba(229,194,123,0.6);
    transform: translateY(-3px);
}

.place-number {
    color: #D7B878;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

.place-name {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    margin-top: 9px;
}

.place-eng {
    color: #8190A5;
    font-size: 10px;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.place-desc {
    color: #B9C3D1;
    font-size: 12px;
    line-height: 1.7;
}

.place-tip {
    color: #E5C27B;
    font-size: 11px;
    margin-top: 12px;
}

.category {
    display: inline-block;
    color: #E5C27B;
    background: rgba(229,194,123,0.10);
    border: 1px solid rgba(229,194,123,0.18);
    padding: 4px 9px;
    border-radius: 30px;
    font-size: 10px;
    font-weight: 700;
}

.footer {
    color: #66758A;
    text-align: center;
    font-size: 11px;
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid rgba(255,255,255,0.08);
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    overflow: hidden;
}

.stSelectbox label, .stMultiSelect label {
    color: #DCE3ED !important;
}

div[data-baseweb="select"] > div {
    background: #172235;
    border-color: #34435A;
    border-radius: 10px;
}

.stAlert {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 메인 타이틀
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">THE ULTIMATE SEOUL TRAVEL GUIDE</div>
    <h1>SEOUL<br><span class="gold">SPOTLIGHT.</span></h1>
    <p>
        Discover the soul of Seoul.<br>
        외국인 여행객에게 추천하는 서울의 대표 명소 10곳을 만나보세요.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 통계 카드
# -----------------------------
a, b, c = st.columns(3)

with a:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">10</div>
        <div class="stat-label">MUST-VISIT PLACES</div>
    </div>
    """, unsafe_allow_html=True)

with b:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">2 DAYS</div>
        <div class="stat-label">TRAVEL ITINERARY</div>
    </div>
    """, unsafe_allow_html=True)

with c:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">SEOUL</div>
        <div class="stat-label">SOUTH KOREA</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 지도 영역
# -----------------------------
st.markdown('<div class="section-title">📍 SEOUL MAP</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">서울의 주요 관광지 10곳을 지도에서 확인해 보세요.</div>',
    unsafe_allow_html=True
)

categories = ["전체"] + sorted(set(p["category"] for p in PLACES))

selected_category = st.selectbox(
    "관광지 종류 선택",
    categories,
    index=0
)

if selected_category == "전체":
    filtered_places = PLACES
else:
    filtered_places = [
        p for p in PLACES if p["category"] == selected_category
    ]

# API 키가 필요 없는 OpenStreetMap 사용
m = folium.Map(
    location=[37.5665, 126.9850],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

for i, place in enumerate(PLACES, start=1):
    if place not in filtered_places:
        continue

    popup_html = f"""
    <div style="width:220px; font-family:Arial; color:#222;">
        <h3 style="margin-bottom:5px;">{html.escape(place['emoji'])} {html.escape(place['name'])}</h3>
        <p style="font-size:11px; color:#777; margin-top:0;">
            {html.escape(place['eng'])}
        </p>
        <p style="font-size:12px; line-height:1.5;">
            {html.escape(place['desc'])}
        </p>
        <b style="color:#98752D;">{html.escape(place['category'])}</b>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{i}. {place['name']}",
        popup=folium.Popup(popup_html, max_width=280),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#D7B878;
                color:#101827;
                width:29px;
                height:29px;
                border-radius:50%;
                border:2px solid white;
                text-align:center;
                line-height:25px;
                font-weight:900;
                font-size:13px;
                box-shadow:0 2px 8px rgba(0,0,0,0.4);
            ">{i}</div>
            """,
            icon_size=(29, 29),
            icon_anchor=(14, 14)
        )
    ).add_to(m)

st_folium(
    m,
    width=None,
    height=560,
    returned_objects=[],
    key="seoul_map"
)

st.caption("※ 지도는 OpenStreetMap을 사용합니다. 인터넷 연결이 필요합니다.")

# -----------------------------
# 관광지 소개
# -----------------------------
st.markdown('<div class="section-title">✦ TOP 10 DESTINATIONS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">서울에서 놓치면 아쉬운 대표 명소들을 소개합니다.</div>',
    unsafe_allow_html=True
)

for start in range(0, len(PLACES), 2):
    cols = st.columns(2)

    for col_index, place in enumerate(PLACES[start:start + 2]):
        number = start + col_index + 1

        with cols[col_index]:
            st.markdown(f"""
            <div class="place-card">
                <div class="place-number">DESTINATION  {number:02d}</div>
                <div class="place-name">{place['emoji']} {place['name']}</div>
                <div class="place-eng">{place['eng']}</div>
                <span class="category">{place['category']}</span>
                <div class="place-desc">{place['desc']}</div>
                <div class="place-tip">✦ TIP : {place['tip']}</div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# 1박 2일 일정
# -----------------------------
st.markdown('<div class="section-title">🗓️ 2 DAYS IN SEOUL</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">서울의 대표 관광지 10곳을 둘러보는 추천 여행 코스입니다.</div>',
    unsafe_allow_html=True
)

day1 = [
    ["09:00 - 10:30", "홍대", "거리 구경과 카페 방문", "1시간 30분"],
    ["10:30 - 11:10", "이동", "경복궁으로 이동", "약 40분"],
    ["11:10 - 12:40", "경복궁", "궁궐 관람 및 한복 체험", "1시간 30분"],
    ["12:40 - 13:00", "이동", "북촌한옥마을로 이동", "약 20분"],
    ["13:00 - 14:00", "북촌한옥마을", "한옥 거리 산책 및 점심", "1시간"],
    ["14:00 - 14:30", "이동", "광장시장으로 이동", "약 30분"],
    ["14:30 - 16:00", "광장시장", "전통시장 먹거리 체험", "1시간 30분"],
    ["16:00 - 16:20", "이동", "DDP로 이동", "약 20분"],
    ["16:20 - 17:30", "동대문디자인플라자", "건축물 관람 및 사진 촬영", "1시간 10분"],
    ["17:30 - 17:50", "이동", "명동으로 이동", "약 20분"],
    ["17:50 - 20:00", "명동", "쇼핑 및 저녁 식사", "2시간 10분"],
]

day2 = [
    ["09:00 - 10:00", "남산 산책", "남산 주변 산책 및 전망 감상", "1시간"],
    ["10:00 - 11:30", "N서울타워", "서울 전망 및 사진 촬영", "1시간 30분"],
    ["11:30 - 12:20", "이동", "강남역으로 이동", "약 50분"],
    ["12:20 - 13:30", "강남역", "쇼핑 및 점심 식사", "1시간 10분"],
    ["13:30 - 13:50", "이동", "코엑스로 이동", "약 20분"],
    ["13:50 - 16:00", "코엑스", "별마당도서관 및 쇼핑", "2시간 10분"],
    ["16:00 - 16:30", "이동", "성수동으로 이동", "약 30분"],
    ["16:30 - 20:00", "성수동", "카페, 팝업스토어 및 저녁", "3시간 30분"],
]

st.markdown("### 🌞 DAY 01 — SEOUL CLASSIC")
st.caption("홍대 · 경복궁 · 북촌 · 광장시장 · DDP · 명동")

df1 = pd.DataFrame(
    day1,
    columns=["시간", "장소", "추천 활동", "소요 시간"]
)

st.dataframe(
    df1,
    use_container_width=True,
    hide_index=True
)

st.markdown("### 🌙 DAY 02 — SEOUL TREND")
st.caption("N서울타워 · 강남역 · 코엑스 · 성수동")

df2 = pd.DataFrame(
    day2,
    columns=["시간", "장소", "추천 활동", "소요 시간"]
)

st.dataframe(
    df2,
    use_container_width=True,
    hide_index=True
)

st.info(
    "여행 시간은 추천 일정에 맞춘 대략적인 예상치입니다. "
    "실제 이동 시간과 운영 시간은 날짜와 교통 상황에 따라 달라질 수 있습니다."
)

# -----------------------------
# 하단 안내
# -----------------------------
st.markdown("""
<div class="footer">
    SEOUL SPOTLIGHT · YOUR SEOUL, YOUR STORY<br>
    A LITTLE GUIDE TO THE BIG CITY 🇰🇷
</div>
""", unsafe_allow_html=True)
