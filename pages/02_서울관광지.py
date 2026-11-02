
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

st.set_page_config(
    page_title="SEOUL SPOTLIGHT",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PLACES = [
    {
        "rank": 1, "name": "명동", "en": "Myeong-dong",
        "category": "SHOPPING", "emoji": "🛍️",
        "lat": 37.5636, "lon": 126.9850,
        "desc": "K-뷰티 쇼핑, 길거리 음식, 화장품 매장이 가득한 서울 대표 쇼핑 거리.",
        "tip": "저녁 시간에 방문하면 활기찬 야시장 분위기를 즐길 수 있어요.",
        "color": "#F4C76B",
    },
    {
        "rank": 2, "name": "N서울타워", "en": "N Seoul Tower",
        "category": "LANDMARK", "emoji": "🌃",
        "lat": 37.5512, "lon": 126.9882,
        "desc": "남산 정상에서 서울의 전경을 360도로 감상할 수 있는 랜드마크.",
        "tip": "해 질 무렵 올라가면 노을과 야경을 모두 볼 수 있어요.",
        "color": "#F4C76B",
    },
    {
        "rank": 3, "name": "코엑스", "en": "COEX",
        "category": "CULTURE", "emoji": "📚",
        "lat": 37.5125, "lon": 127.0588,
        "desc": "별마당도서관, 쇼핑몰, 전시·공연장이 모여 있는 복합 문화 공간.",
        "tip": "별마당도서관의 거대한 책장 앞에서 사진을 남겨보세요.",
        "color": "#70D6C8",
    },
    {
        "rank": 4, "name": "강남역", "en": "Gangnam Station",
        "category": "SHOPPING", "emoji": "✨",
        "lat": 37.4979, "lon": 127.0276,
        "desc": "트렌디한 패션 매장과 맛집, 카페가 이어지는 서울의 핫플레이스.",
        "tip": "골목 안쪽의 개성 있는 카페도 둘러보세요.",
        "color": "#F4C76B",
    },
    {
        "rank": 5, "name": "홍대", "en": "Hongdae",
        "category": "CULTURE", "emoji": "🎸",
        "lat": 37.5563, "lon": 126.9236,
        "desc": "버스킹, 스트리트 패션, 개성 있는 상점과 밤문화로 유명한 거리.",
        "tip": "주말 저녁에는 거리 공연을 즐겨보세요.",
        "color": "#70D6C8",
    },
    {
        "rank": 6, "name": "경복궁", "en": "Gyeongbokgung Palace",
        "category": "HISTORY", "emoji": "🏯",
        "lat": 37.5796, "lon": 126.9770,
        "desc": "조선 왕조의 대표 궁궐로, 한국 전통 건축과 역사를 만날 수 있는 곳.",
        "tip": "한복을 입고 방문하면 특별한 사진을 남길 수 있어요.",
        "color": "#B69CFF",
    },
    {
        "rank": 7, "name": "동대문디자인플라자", "en": "DDP",
        "category": "ARCHITECTURE", "emoji": "🏛️",
        "lat": 37.5671, "lon": 127.0095,
        "desc": "독특한 곡선 건축으로 유명한 디자인·전시·패션 복합 문화 공간.",
        "tip": "야간 조명이 멋져서 사진 촬영 명소로 좋아요.",
        "color": "#70D6C8",
    },
    {
        "rank": 8, "name": "광장시장", "en": "Gwangjang Market",
        "category": "FOOD", "emoji": "🥢",
        "lat": 37.5701, "lon": 126.9997,
        "desc": "빈대떡, 마약김밥, 육회 등 한국 시장 먹거리를 즐길 수 있는 전통시장.",
        "tip": "여러 음식을 조금씩 나눠 먹어보세요.",
        "color": "#FF9F83",
    },
    {
        "rank": 9, "name": "북촌한옥마을", "en": "Bukchon Hanok Village",
        "category": "HISTORY", "emoji": "🏘️",
        "lat": 37.5826, "lon": 126.9830,
        "desc": "전통 한옥이 이어지는 골목에서 서울의 옛 풍경을 만날 수 있는 마을.",
        "tip": "실제 주민이 거주하는 곳이니 조용히 관람해 주세요.",
        "color": "#B69CFF",
    },
    {
        "rank": 10, "name": "성수동", "en": "Seongsu-dong",
        "category": "TREND", "emoji": "☕",
        "lat": 37.5445, "lon": 127.0560,
        "desc": "옛 공장을 개조한 카페와 팝업스토어, 편집숍이 모인 감성 거리.",
        "tip": "방문 전 새로운 팝업스토어 일정을 확인해 보세요.",
        "color": "#FF9F83",
    },
]

# 디자인 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

:root {
  --bg: #080D18;
  --panel: #101827;
  --gold: #F4C76B;
  --white: #F5F7FB;
}

html, body, [class*="css"] {
  font-family: 'DM Sans','Noto Sans KR',sans-serif;
}

.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(56,87,145,.20), transparent 34%),
    radial-gradient(ellipse at 92% 15%, rgba(123,83,173,.13), transparent 30%),
    var(--bg);
  color: var(--white);
}

.block-container {
  max-width: 1240px;
  padding-top: 2.1rem;
  padding-bottom: 4rem;
}

#MainMenu, footer, header {
  visibility: hidden;
}

.hero {
  position: relative;
  overflow: hidden;
  padding: 35px 38px 32px;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 25px;
  background: linear-gradient(115deg, #182741, #0F1829 58%, #2C2542);
  box-shadow: 0 24px 80px rgba(0,0,0,.24);
  margin-bottom: 23px;
}

.hero:after {
  content: "SEOUL";
  position: absolute;
  right: -10px;
  bottom: -44px;
  font-size: clamp(75px, 15vw, 190px);
  font-weight: 900;
  letter-spacing: -.09em;
  color: rgba(255,255,255,.035);
  pointer-events: none;
}

.eyebrow {
  color: var(--gold);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .24em;
  margin-bottom: 13px;
}

.hero h1 {
  font-size: clamp(35px, 6vw, 66px);
  line-height: 1.04;
  letter-spacing: -.055em;
  font-weight: 900;
  margin: 0;
  color: #fff;
}

.hero h1 span {
  color: var(--gold);
}

.hero p {
  color: #B9C3D3;
  font-size: 14px;
  line-height: 1.8;
  margin: 17px 0 0;
  max-width: 590px;
}

.pill {
  display: inline-block;
  border: 1px solid rgba(244,199,107,.35);
  background: rgba(244,199,107,.09);
  color: #F4D99D;
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .13em;
  margin-bottom: 17px;
}

.section-kicker {
  color: var(--gold);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .22em;
  margin: 25px 0 7px;
}

.section-title {
  color: #F7F8FC;
  font-size: 25px;
  font-weight: 850;
  letter-spacing: -.04em;
  margin: 0 0 6px;
}

.section-sub {
  color: #8F9BB0;
  font-size: 12px;
  margin-bottom: 15px;
}

.stat-wrap {
  background: linear-gradient(145deg,#131E30,#0E1726);
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 17px;
  padding: 17px 18px;
  min-height: 88px;
}

.stat-label {
  color: #8996AB;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .13em;
}

.stat-value {
  color: #F7F8FC;
  font-size: 25px;
  font-weight: 850;
  margin-top: 4px;
}

.stat-note {
  color: #77859B;
  font-size: 10px;
  margin-top: 2px;
}

.place-card {
  background: linear-gradient(145deg,#152032,#0E1624);
  border: 1px solid rgba(255,255,255,.085);
  border-radius: 17px;
  padding: 17px 18px 16px;
  min-height: 178px;
  margin-bottom: 13px;
  transition: transform .2s ease;
}

.place-card:hover {
  transform: translateY(-3px);
  border-color: rgba(244,199,107,.45);
}

.place-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.rank {
  font-size: 11px;
  color: #F4C76B;
  font-weight: 900;
  letter-spacing: .1em;
}

.category {
  font-size: 9px;
  letter-spacing: .15em;
  color: #9CAAC0;
  border: 1px solid rgba(255,255,255,.12);
  padding: 5px 8px;
  border-radius: 99px;
}

.place-name {
  font-size: 17px;
  font-weight: 850;
  color: #F7F8FC;
}

.place-en {
  font-size: 10px;
  color: #8290A5;
  margin-top: 2px;
}

.place-desc {
  font-size: 11px;
  line-height: 1.65;
  color: #C0C9D7;
  margin-top: 12px;
  min-height: 37px;
}

.place-tip {
  font-size: 10px;
  line-height: 1.6;
  color: #E5C982;
  margin-top: 9px;
}

.footer {
  text-align: center;
  color: #65738A;
  font-size: 10px;
  letter-spacing: .08em;
  padding-top: 22px;
  margin-top: 20px;
  border-top: 1px solid rgba(255,255,255,.07);
}

@media(max-width:700px) {
  .block-container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .hero {
    padding: 27px 22px;
  }
}
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown("""
<div class="hero">
  <div class="pill">✦ THE ULTIMATE CITY GUIDE · 2026</div>
  <div class="eyebrow">DISCOVER THE SOUL OF KOREA</div>
  <h1>SEOUL<br><span>SPOTLIGHT.</span></h1>
  <p>
  처음 만나는 서울, 가장 빛나는 10개의 스팟.<br>
  외국인 여행객의 발길이 모이는 명소부터
  서울의 감성까지 한눈에 만나보세요.
  </p>
</div>
""", unsafe_allow_html=True)

# 상단 통계
s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""
    <div class="stat-wrap">
    <div class="stat-label">CURATED PLACES</div>
    <div class="stat-value">10 SPOTS</div>
    <div class="stat-note">서울 대표 여행 명소</div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="stat-wrap">
    <div class="stat-label">CITY</div>
    <div class="stat-value">SEOUL</div>
    <div class="stat-note">대한민국의 심장</div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="stat-wrap">
    <div class="stat-label">TRAVEL VIBE</div>
    <div class="stat-value">∞</div>
    <div class="stat-note">History · Trend · Food · View</div>
    </div>
    """, unsafe_allow_html=True)

# 지도 섹션
st.markdown("""
<div class="section-kicker">01 / THE MAP</div>
<div class="section-title">서울을 한눈에, 명소를 한 번에.</div>
<div class="section-sub">
지도 위 숫자 마커를 누르면 각 장소의 정보를 확인할 수 있어요.
</div>
""", unsafe_allow_html=True)

# 관광 테마 필터
selected_category = st.selectbox(
    "관광 테마",
    ["전체 보기", "쇼핑", "문화·트렌드", "역사", "먹거리", "건축"]
)

category_map = {
    "쇼핑": ["SHOPPING"],
    "문화·트렌드": ["CULTURE", "TREND"],
    "역사": ["HISTORY"],
    "먹거리": ["FOOD"],
    "건축": ["ARCHITECTURE"],
}

filtered = PLACES if selected_category == "전체 보기" else [
    p for p in PLACES
    if p["category"] in category_map[selected_category]
]

# 서울 지도 생성
m = folium.Map(
    location=[37.555, 126.986],
    zoom_start=12,
    tiles="CartoDB dark_matter",
    control_scale=True,
    prefer_canvas=True,
)

Fullscreen(
    position="topright",
    title="전체 화면",
    title_cancel="닫기"
).add_to(m)

# 지도에 관광지 마커 추가
for p in filtered:

    popup_html = f"""
    <div style="font-family:Arial,sans-serif;width:220px;color:#172033;">
      <div style="font-size:10px;letter-spacing:2px;color:#9A762D;font-weight:800;">
      SEOUL SPOTLIGHT · #{p['rank']:02d}
      </div>
      <div style="font-size:17px;font-weight:800;margin:7px 0 2px;">
      {p['emoji']} {p['name']}
      </div>
      <div style="font-size:11px;color:#657187;margin-bottom:8px;">
      {p['en']}
      </div>
      <div style="font-size:12px;line-height:1.55;">
      {p['desc']}
      </div>
    </div>
    """

    icon = folium.DivIcon(
        html=f"""
        <div style="
          width:31px;
          height:31px;
          border-radius:50%;
          background:{p['color']};
          border:2px solid #fff;
          box-shadow:0 3px 14px rgba(0,0,0,.55);
          color:#101827;
          font-size:12px;
          font-weight:900;
          display:flex;
          align-items:center;
          justify-content:center;
          font-family:Arial,sans-serif;">
          {p['rank']}
        </div>
        """,
        icon_size=(35, 35),
        icon_anchor=(17, 17),
    )

    folium.Marker(
        location=[p["lat"], p["lon"]],
        tooltip=f"#{p['rank']} · {p['name']} / {p['en']}",
        popup=folium.Popup(popup_html, max_width=280),
        icon=icon,
    ).add_to(m)

# 지도 화면 출력
st_folium(
    m,
    height=570,
    use_container_width=True,
    returned_objects=[],
    key="seoul_spotlight_map",
)

# 관광지 설명 섹션
st.markdown("""
<div class="section-kicker">02 / THE COLLECTION</div>
<div class="section-title">놓치면 아쉬운 서울의 순간들.</div>
<div class="section-sub">
각 장소의 매력과 여행 팁을 짧게 정리했어요.
</div>
""", unsafe_allow_html=True)

# 관광지 카드 출력
for start in range(0, len(filtered), 2):

    cols = st.columns(2, gap="medium")

    for col, p in zip(cols, filtered[start:start+2]):

        with col:

            st.markdown(f"""
            <div class="place-card">

              <div class="place-top">
                <span class="rank">
                NO. {p['rank']:02d} &nbsp; {p['emoji']}
                </span>

                <span class="category">
                {p['category']}
                </span>
              </div>

              <div class="place-name">
              {p['name']}
              </div>

              <div class="place-en">
              {p['en']}
              </div>

              <div class="place-desc">
              {p['desc']}
              </div>

              <div class="place-tip">
              ✦ TIP &nbsp; {p['tip']}
              </div>

            </div>
            """, unsafe_allow_html=True)

# 하단 푸터
st.markdown("""
<div class="footer">
SEOUL SPOTLIGHT · MADE FOR CURIOUS TRAVELERS<br>
MAP DATA © OPENSTREETMAP CONTRIBUTORS · CARTODB BASEMAP
</div>
""", unsafe_allow_html=True)

# 자료 출처
with st.expander("자료 및 순위 기준"):

    st.write(
        "이 목록은 서울시·서울AI재단이 공개한 "
        "2025년 외국인 방문객 분석을 참고하여 "
        "주요 방문 지역과 대표 역사·문화 관광지를 "
        "함께 구성한 큐레이션입니다. "
        "서울시 공식 단일 TOP 10 순위는 아닙니다."
    )

    st.markdown(
        "[서울시 공식 분석 자료 보기](https://english.seoul.go.kr/from-k-culture-to-k-hiking-foreign-tourists-venture-beyond-seouls-top-attractions/)"
    )
