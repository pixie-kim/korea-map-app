# app.py
# 실행 전 설치:
# pip install streamlit pillow pandas streamlit-image-coordinates

import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd
import json
import os

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="대한민국 행정구역 업체관리",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .main { background-color: #f5f6fa; }
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 1.6rem !important; font-weight: 700; color: #1a1a2e; }
    .region-badge {
        display: inline-block; background: #1a1a2e; color: #fff;
        border-radius: 6px; padding: 4px 14px; font-size: 1rem;
        font-weight: 700; margin-bottom: 12px;
    }
    .company-card {
        background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .stButton > button { border-radius: 8px; font-family: 'Noto Sans KR', sans-serif; font-weight: 500; }
    .info-box {
        background: #eef2ff; border-left: 4px solid #4361ee; border-radius: 6px;
        padding: 10px 14px; font-size: 0.88rem; color: #333; margin-bottom: 12px;
    }
    .stat-row { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
    .stat-card {
        background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 10px 18px; text-align: center; flex: 1; min-width: 80px;
    }
    .stat-num { font-size: 1.4rem; font-weight: 700; color: #4361ee; }
    .stat-label { font-size: 0.75rem; color: #888; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 데이터 파일
# ─────────────────────────────────────────────
DATA_FILE = "companies.json"

if "region_data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            st.session_state.region_data = json.load(f)
    else:
        st.session_state.region_data = {}

if "selected_region" not in st.session_state:
    st.session_state.selected_region = "서울"

if "last_click" not in st.session_state:
    st.session_state.last_click = None

# ─────────────────────────────────────────────
# 행정구역 좌표 (이미지 1179×1450 기준, x, y, w, h)
# 지도에 표시된 시·군·구 전체
# ─────────────────────────────────────────────
REGIONS = {
    # ── 특별시·광역시·특별자치시 ──
    "서울":   (220, 195, 75, 55),
    "인천":   (155, 205, 65, 60),
    "대전":   (430, 535, 75, 60),
    "세종":   (415, 495, 55, 42),
    "대구":   (620, 655, 78, 60),
    "광주":   (278, 730, 72, 58),
    "울산":   (775, 690, 72, 58),
    "부산":   (730, 765, 85, 65),

    # ── 경기도 ──
    "수원":   (215, 295, 50, 38),
    "성남":   (245, 265, 48, 35),
    "안양":   (210, 265, 40, 32),
    "부천":   (175, 230, 45, 35),
    "광명":   (190, 255, 38, 30),
    "평택":   (210, 340, 58, 45),
    "안성":   (270, 345, 52, 42),
    "화성":   (175, 305, 55, 50),
    "용인":   (255, 290, 55, 45),
    "이천":   (300, 285, 52, 42),
    "여주":   (340, 268, 52, 42),
    "광주(경기)": (270, 248, 48, 38),
    "하남":   (255, 235, 40, 28),
    "구리":   (248, 218, 35, 25),
    "남양주": (278, 210, 58, 38),
    "의정부": (240, 190, 42, 30),
    "양주":   (238, 170, 48, 35),
    "동두천": (228, 152, 42, 30),
    "포천":   (272, 155, 58, 50),
    "가평":   (330, 175, 58, 50),
    "양평":   (308, 248, 50, 40),
    "고양":   (195, 190, 52, 35),
    "파주":   (162, 168, 55, 48),
    "김포":   (150, 205, 45, 38),
    "연천":   (210, 135, 52, 42),
    "안산":   (165, 270, 45, 40),
    "시흥":   (170, 248, 38, 32),
    "의왕":   (210, 278, 35, 28),
    "군포":   (205, 285, 35, 28),
    "과천":   (225, 270, 32, 25),
    "오산":   (212, 318, 40, 32),

    # ── 강원도 ──
    "춘천":   (388, 165, 70, 60),
    "홍천":   (448, 192, 80, 65),
    "원주":   (378, 255, 60, 50),
    "횡성":   (432, 242, 55, 45),
    "평창":   (480, 228, 68, 55),
    "강릉":   (560, 195, 62, 50),
    "동해":   (580, 242, 50, 42),
    "삼척":   (588, 272, 55, 50),
    "태백":   (548, 258, 45, 42),
    "정선":   (510, 245, 52, 48),
    "영월":   (468, 268, 52, 48),
    "제천":   (432, 295, 55, 48),
    "충주":   (390, 295, 58, 48),
    "단양":   (455, 278, 48, 38),
    "화천":   (418, 138, 60, 45),
    "양구":   (458, 135, 52, 42),
    "인제":   (490, 148, 65, 58),
    "고성(강원)": (510, 120, 52, 42),
    "속초":   (535, 148, 42, 35),
    "양양":   (548, 175, 45, 38),
    "철원":   (355, 128, 65, 42),

    # ── 충청북도 ──
    "청주":   (418, 438, 72, 60),
    "청원":   (408, 405, 62, 45),
    "보은":   (448, 495, 58, 48),
    "옥천":   (432, 538, 52, 42),
    "영동":   (450, 568, 55, 45),
    "진천":   (385, 408, 52, 42),
    "음성":   (355, 378, 55, 45),
    "증평":   (388, 388, 40, 32),
    "괴산":   (418, 388, 55, 42),
    "충주(시)": (392, 330, 58, 48),

    # ── 충청남도 ──
    "천안":   (318, 368, 68, 55),
    "아산":   (285, 348, 58, 48),
    "당진":   (222, 348, 58, 48),
    "서산":   (175, 358, 58, 48),
    "태안":   (145, 355, 45, 55),
    "홍성":   (215, 405, 55, 45),
    "예산":   (255, 395, 52, 42),
    "공주":   (310, 435, 62, 50),
    "보령":   (188, 448, 58, 50),
    "청양":   (252, 438, 52, 42),
    "부여":   (268, 475, 58, 48),
    "서천":   (235, 505, 52, 45),
    "논산":   (298, 498, 58, 48),
    "금산":   (368, 535, 52, 45),
    "계룡":   (318, 512, 38, 30),

    # ── 전라북도 ──
    "전주":   (315, 598, 68, 58),
    "익산":   (278, 572, 58, 50),
    "군산":   (238, 558, 55, 48),
    "김제":   (272, 615, 58, 50),
    "완주":   (338, 582, 52, 45),
    "부안":   (235, 638, 52, 50),
    "정읍":   (265, 658, 58, 50),
    "고창":   (238, 698, 55, 50),
    "남원":   (355, 648, 62, 55),
    "순창":   (318, 668, 52, 48),
    "임실":   (330, 630, 50, 42),
    "진안":   (368, 598, 52, 48),
    "무주":   (408, 558, 55, 48),
    "장수":   (378, 638, 52, 48),

    # ── 전라남도 ──
    "목포":   (205, 815, 48, 40),
    "여수":   (388, 830, 58, 52),
    "순천":   (358, 800, 60, 52),
    "광양":   (390, 798, 48, 42),
    "나주":   (268, 778, 55, 48),
    "화순":   (308, 778, 52, 45),
    "담양":   (305, 738, 50, 42),
    "곡성":   (338, 758, 48, 42),
    "구례":   (368, 768, 48, 42),
    "장성":   (270, 728, 50, 42),
    "영광":   (228, 718, 52, 45),
    "함평":   (245, 748, 48, 42),
    "무안":   (222, 778, 45, 38),
    "신안":   (165, 790, 55, 60),
    "진도":   (175, 848, 52, 48),
    "해남":   (240, 848, 65, 55),
    "강진":   (280, 848, 52, 48),
    "장흥":   (310, 838, 52, 48),
    "보성":   (338, 808, 52, 48),
    "고흥":   (360, 840, 62, 55),
    "완도":   (290, 882, 62, 52),
    "영암":   (248, 812, 50, 42),

    # ── 경상북도 ──
    "포항":   (692, 498, 72, 62),
    "경주":   (678, 562, 75, 65),
    "안동":   (625, 435, 80, 68),
    "구미":   (575, 518, 68, 55),
    "영주":   (578, 388, 60, 52),
    "영천":   (655, 598, 62, 52),
    "상주":   (548, 478, 62, 52),
    "문경":   (512, 428, 62, 52),
    "경산":   (650, 645, 58, 48),
    "군위":   (615, 545, 55, 48),
    "의성":   (598, 488, 58, 50),
    "청송":   (648, 468, 55, 48),
    "영양":   (668, 428, 52, 45),
    "영덕":   (692, 455, 50, 45),
    "청도":   (648, 680, 55, 48),
    "고령":   (598, 680, 52, 48),
    "성주":   (572, 598, 55, 48),
    "칠곡":   (582, 622, 48, 40),
    "예천":   (548, 428, 52, 45),
    "봉화":   (608, 388, 62, 48),
    "울진":   (672, 388, 55, 52),
    "울릉":   (785, 195, 35, 30),
    "김천":   (538, 548, 58, 50),
    "철곡":   (582, 565, 45, 38),

    # ── 경상남도 ──
    "창원":   (650, 760, 75, 62),
    "진주":   (578, 778, 70, 60),
    "통영":   (628, 828, 58, 52),
    "사천":   (568, 812, 55, 48),
    "김해":   (695, 782, 60, 52),
    "밀양":   (668, 718, 62, 52),
    "거제":   (695, 840, 65, 58),
    "양산":   (725, 740, 55, 48),
    "의령":   (615, 748, 52, 45),
    "함안":   (635, 775, 52, 45),
    "창녕":   (628, 718, 52, 48),
    "고성(경남)": (600, 808, 52, 48),
    "남해":   (568, 848, 58, 52),
    "하동":   (498, 798, 55, 48),
    "산청":   (538, 758, 55, 48),
    "함양":   (505, 738, 52, 48),
    "거창":   (528, 708, 55, 48),
    "합천":   (568, 738, 58, 48),

    # ── 제주특별자치도 ──
    "제주":   (340, 955, 85, 65),
    "서귀포": (340, 1010, 85, 55),
}

# ─────────────────────────────────────────────
# 이미지 로드 & 오버레이
# ─────────────────────────────────────────────
@st.cache_data
def load_image(path: str):
    return Image.open(path).convert("RGB")

def draw_overlay(img: Image.Image, selected: str) -> Image.Image:
    overlay = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(overlay)
    if selected in REGIONS:
        x, y, w, h = REGIONS[selected]
        draw.rectangle([x, y, x + w, y + h],
                       fill=(67, 97, 238, 90),
                       outline=(67, 97, 238, 230),
                       width=3)
    return overlay.convert("RGB")

def detect_region(cx: int, cy: int, display_w: int, orig_w: int, orig_h: int) -> str | None:
    """
    클릭 좌표(display 기준) → 원본 좌표로 변환 후 지역명 반환
    streamlit_image_coordinates 는 display 픽셀 좌표를 반환하므로
    비율로 원본 좌표계로 환산해야 함
    """
    scale = orig_w / display_w
    display_h = int(orig_h / scale)  # 비율 유지
    rx = int(cx * (orig_w / display_w))
    ry = int(cy * (orig_h / display_h))

    matched = []
    for region, (bx, by, bw, bh) in REGIONS.items():
        if bx <= rx <= bx + bw and by <= ry <= by + bh:
            matched.append((bw * bh, region))
    if matched:
        matched.sort()   # 면적 작은(더 세밀한) 지역 우선
        return matched[0][1]
    return None

# 지도를 표시할 고정 너비 (px) — 이 값을 streamlit_image_coordinates 에도 동일하게 전달
MAP_DISPLAY_WIDTH = 600

# ─────────────────────────────────────────────
# 저장
# ─────────────────────────────────────────────
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.region_data, f, ensure_ascii=False, indent=4)

# ─────────────────────────────────────────────
# 제목 & 통계
# ─────────────────────────────────────────────
st.title("🗺️ 대한민국 행정구역 업체관리")

total_regions  = len([r for r, c in st.session_state.region_data.items() if c])
total_companies = sum(len(c) for c in st.session_state.region_data.values())

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="stat-num">{total_regions}</div><div class="stat-label">등록 지역</div></div>
  <div class="stat-card"><div class="stat-num">{total_companies}</div><div class="stat-label">전체 업체 수</div></div>
  <div class="stat-card"><div class="stat-num">{len(REGIONS)}</div><div class="stat-label">관리 가능 지역</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 레이아웃
# ─────────────────────────────────────────────
col_map, col_panel = st.columns([3, 2], gap="large")

# ══════════════════════════════════════════════
# 지도 영역
# ══════════════════════════════════════════════
with col_map:
    st.markdown("#### 📍 지도에서 지역을 클릭하세요")
    st.markdown('<div class="info-box">지도를 클릭하면 해당 시·군이 선택됩니다.</div>', unsafe_allow_html=True)

    img_path = "FullSizeRender.jpg"
    if not os.path.exists(img_path):
        st.warning(f"지도 이미지를 찾을 수 없습니다: `{img_path}`")
        orig_img = None
    else:
        orig_img = load_image(img_path)

    if orig_img is not None:
        display_img = draw_overlay(orig_img, st.session_state.selected_region)

        try:
            from streamlit_image_coordinates import streamlit_image_coordinates

            coords = streamlit_image_coordinates(display_img, key="korea_map", width=MAP_DISPLAY_WIDTH)

            if coords and coords != st.session_state.last_click:
                st.session_state.last_click = coords
                detected = detect_region(
                    coords["x"], coords["y"],
                    MAP_DISPLAY_WIDTH,
                    orig_img.width, orig_img.height
                )
                if detected:
                    st.session_state.selected_region = detected
                    st.rerun()

        except ImportError:
            st.image(display_img, use_container_width=True)
            st.warning("`pip install streamlit-image-coordinates` 후 재실행하세요.")

    # selectbox fallback
    st.markdown("##### 또는 목록에서 선택")
    region_list = sorted(REGIONS.keys())
    sel_idx = region_list.index(st.session_state.selected_region) if st.session_state.selected_region in region_list else 0
    chosen = st.selectbox("행정구역", region_list, index=sel_idx, label_visibility="collapsed")
    if chosen != st.session_state.selected_region:
        st.session_state.selected_region = chosen
        st.rerun()

# ══════════════════════════════════════════════
# 업체 관리 패널
# ══════════════════════════════════════════════
with col_panel:
    region = st.session_state.selected_region
    st.markdown(f'<div class="region-badge">📌 {region}</div>', unsafe_allow_html=True)
    st.markdown("#### 업체 목록")

    if region not in st.session_state.region_data:
        st.session_state.region_data[region] = []

    companies = st.session_state.region_data[region]

    if not companies:
        st.info("등록된 업체가 없습니다. 아래 버튼으로 추가하세요.")

    to_delete = None
    for idx, company in enumerate(companies):
        st.markdown(f'<div class="company-card">', unsafe_allow_html=True)

        name    = st.text_input("업체명 *",  value=company.get("name", ""),    key=f"name_{region}_{idx}",  placeholder="예) 홍길동 전자")
        address = st.text_input("위치",       value=company.get("address", ""), key=f"addr_{region}_{idx}",  placeholder="예) 서울시 중구 명동길 12")
        phone   = st.text_input("전화번호",   value=company.get("phone", ""),   key=f"phone_{region}_{idx}", placeholder="예) 02-1234-5678")

        st.session_state.region_data[region][idx] = {"name": name, "address": address, "phone": phone}

        if st.button("🗑️ 삭제", key=f"del_{region}_{idx}", use_container_width=True):
            to_delete = idx

        st.markdown('</div>', unsafe_allow_html=True)

    if to_delete is not None:
        st.session_state.region_data[region].pop(to_delete)
        save_data()
        st.rerun()

    st.markdown("---")
    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("➕ 업체 추가", use_container_width=True):
            st.session_state.region_data[region].append({"name": "", "address": "", "phone": ""})
            st.rerun()

    with btn2:
        if st.button("💾 저장", type="primary", use_container_width=True):
            valid = [c for c in st.session_state.region_data[region] if c.get("name", "").strip()]
            dropped = len(st.session_state.region_data[region]) - len(valid)
            st.session_state.region_data[region] = valid
            save_data()
            if dropped:
                st.warning(f"업체명 없는 항목 {dropped}개 제외 후 저장되었습니다.")
            else:
                st.success(f"✅ {region} 업체 정보 저장 완료!")

# ─────────────────────────────────────────────
# 전체 데이터 테이블
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📋 전체 등록 업체")

all_rows = []
for r, comps in st.session_state.region_data.items():
    for c in comps:
        if c.get("name", "").strip():
            all_rows.append({"지역": r, "업체명": c.get("name",""), "위치": c.get("address",""), "전화번호": c.get("phone","")})

if all_rows:
    df = pd.DataFrame(all_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 CSV 다운로드", data=csv, file_name="업체목록.csv", mime="text/csv")
else:
    st.info("아직 등록된 업체가 없습니다.")