import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Streamlit Cloud용 인증 설정
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 로컬에서 실행할 때
    if os.path.exists("google_api_key.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_api_key.json", scope)
    # Streamlit Cloud에서 실행할 때
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["connections"]["gcp_service_account"], 
            scope
        )
    
    return gspread.authorize(creds)

# 🔄 데이터 로드 함수 (캐시 제거 가능)
@st.cache_data(ttl=60)  # 60초마다 자동 갱신
def load_data():
    """Google Sheets에서 데이터를 로드하는 함수"""
    client = init_connection()
    
    try:
        sheet = client.open("손익개선_분석결과").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 데이터가 비어있는지 확인
        if df.empty:
            return None, "📋 Google Sheets에 데이터가 없습니다."
        
        # 날짜 컬럼이 있는지 확인
        if '날짜' not in df.columns:
            return None, "📋 Google Sheets에 '날짜' 컬럼이 없습니다."
        
        # 날짜 변환
        try:
            df["날짜"] = pd.to_datetime(df["날짜"])
        except:
            return None, "📅 날짜 형식이 올바르지 않습니다."
            
        return df, "✅ 데이터 로드 성공"
        
    except gspread.SpreadsheetNotFound:
        return None, "📄 '손익개선_분석결과' 시트를 찾을 수 없습니다."
    except Exception as e:
        return None, f"❌ 오류가 발생했습니다: {str(e)}"

# UI 구성
st.title("📊 SK 손익개선 아이디어 대시보드")

# 🔄 새로고침 버튼 및 상태 표시
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    refresh_btn = st.button("🔄 새로고침", type="primary")

with col2:
    auto_refresh = st.checkbox("⚡ 자동 새로고침 (30초)")

with col3:
    # 마지막 업데이트 시간 표시
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    
    last_update = time.strftime('%H:%M:%S', time.localtime(st.session_state.last_update))
    st.caption(f"⏰ 마지막 업데이트: {last_update}")

# 🔄 새로고침 로직
if refresh_btn:
    st.cache_data.clear()  # 캐시 삭제
    st.session_state.last_update = time.time()
    st.success("🔄 데이터를 새로고침했습니다!")
    time.sleep(1)  # 1초 대기
    st.rerun()  # 페이지 새로고침

# ⚡ 자동 새로고침 로직
if auto_refresh:
    current_time = time.time()
    if current_time - st.session_state.last_update > 30:  # 30초마다
        st.cache_data.clear()
        st.session_state.last_update = current_time
        st.info("⚡ 자동으로 데이터를 새로고침했습니다!")
        st.rerun()

# 📊 데이터 로드
df, status_message = load_data()

# 상태 메시지 표시
if df is None:
    st.error(status_message)
    st.stop()
else:
    st.success(f"{status_message} | 총 {len(df)}개 데이터")

# 📅 날짜 필터
selected_date = st.date_input("📅 특정 날짜 이후 데이터 보기", value=pd.to_datetime("2025-07-01").date())
selected_datetime = pd.to_datetime(selected_date)
filtered_df = df[df["날짜"] >= selected_datetime]

# 📰 데이터 표시
st.subheader(f"📰 GPT 요약 기사 리스트 ({len(filtered_df)}건)")

# 실시간 데이터 개수 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 전체 데이터", len(df))
with col2:
    st.metric("🔍 필터된 데이터", len(filtered_df))
with col3:
    if len(df) > 0:
        latest_date = df["날짜"].max().strftime('%Y-%m-%d')
        st.metric("📅 최신 데이터", latest_date)

# 📋 데이터 테이블
st.dataframe(
    filtered_df[["날짜", "기사 제목", "GPT 요약", "원문 링크"]], 
    use_container_width=True,
    height=400
)

# 🔍 키워드 필터링
keyword = st.text_input("🔍 요약 키워드 필터링 (예: 설비, 구조조정 등)")
if keyword:
    keyword_df = filtered_df[filtered_df["GPT 요약"].str.contains(keyword, case=False, na=False)]
    st.write(f"🔎 '{keyword}' 포함된 요약 {len(keyword_df)}건")
    if len(keyword_df) > 0:
        st.dataframe(keyword_df, use_container_width=True)
    else:
        st.warning("🔍 해당 키워드가 포함된 데이터가 없습니다.")

# 📄 보고서 다운로드용 요약
st.subheader("📄 요약 보고서 텍스트")
summary = "\n\n".join([
    f"[{row['날짜'].strftime('%Y-%m-%d')}] {row['기사 제목']} → {row['GPT 요약']}"
    for idx, row in filtered_df.iterrows()
])
st.text_area("📋 복사용 요약 보고서", summary, height=300)

# 📌 사용 안내
st.sidebar.title("📖 사용 방법")
st.sidebar.info("""
**🔄 새로고침 기능:**
- **수동 새로고침**: 🔄 버튼 클릭
- **자동 새로고침**: ⚡ 체크박스 선택 (30초마다)

**📊 데이터 확인:**
- 실시간 데이터 개수 표시
- 마지막 업데이트 시간 표시
- 필터된 결과 개수 표시
""")

# 💡 개발자 노트
st.sidebar.title("💡 개발 정보")
st.sidebar.code("""
# Google Sheets 연결 상태
- 캐시 TTL: 60초
- 자동 새로고침: 30초
- 수동 새로고침: 즉시
""")
