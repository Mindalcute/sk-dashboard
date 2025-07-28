import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 현재 스크립트가 있는 디렉토리 가져오기
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "google_api_key.json")

# Google Sheet 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

try:
    # Google Sheet 열기
    sheet = client.open("손익개선_분석결과").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 데이터가 비어있는지 확인
    if df.empty:
        st.error("📋 Google Sheets에 데이터가 없습니다. 샘플 데이터를 먼저 입력해주세요.")
        st.stop()
    
    # 날짜 컬럼이 있는지 확인
    if '날짜' not in df.columns:
        st.error("📋 Google Sheets에 '날짜' 컬럼이 없습니다. 헤더를 확인해주세요.")
        st.stop()
    
    # 날짜 변환 (에러 처리 포함)
    try:
        df["날짜"] = pd.to_datetime(df["날짜"])
    except:
        st.error("📅 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
        st.stop()
        
except gspread.SpreadsheetNotFound:
    st.error("📄 '손익개선_분석결과' 시트를 찾을 수 없습니다. 시트 이름을 확인해주세요.")
    st.stop()
except Exception as e:
    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
    st.stop()

# UI 구성
st.title("📊 SK 손익개선 아이디어 대시보드")

# 날짜 필터 (타입 오류 수정)
selected_date = st.date_input("📅 특정 날짜 이후 데이터 보기", value=pd.to_datetime("2025-07-01").date())
# 타입 통일: selected_date를 datetime으로 변환
selected_datetime = pd.to_datetime(selected_date)
filtered_df = df[df["날짜"] >= selected_datetime]

# 요약 테이블 출력
st.subheader("📰 GPT 요약 기사 리스트")
st.dataframe(filtered_df[["날짜", "기사 제목", "GPT 요약", "원문 링크"]])

# 키워드 필터링
keyword = st.text_input("🔍 요약 키워드 필터링 (예: 설비, 구조조정 등)")
if keyword:
    keyword_df = filtered_df[filtered_df["GPT 요약"].str.contains(keyword, case=False, na=False)]
    st.write(f"🔎 '{keyword}' 포함된 요약 {len(keyword_df)}건")
    st.dataframe(keyword_df)

# 보고서 다운로드용 요약
st.subheader("📄 요약 보고서 텍스트")
summary = "\n\n".join([
    f"[{row['날짜'].strftime('%Y-%m-%d')}] {row['기사 제목']} → {row['GPT 요약']}"
    for idx, row in filtered_df.iterrows()
])
st.text_area("📋 복사용 요약 보고서", summary, height=300)
