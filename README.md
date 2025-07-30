기능 : 구글시트와 streamlit  연동,
구글시트에 정보 업데이트하면 대시보드로 볼 수 있음

후에 뉴스기사 등 수집한 것을 구글시트와 연동하게 한다면
유용할 것..

새로고침 버튼 추가 O

날짜 형식 "YYYY-MM-DD" 정확하게 맞춰야 오류 안 난다!

-----------------
사용한 api : Google Sheets API

Streamlit + gspread로 Google Sheets에서 데이터 읽기/쓰기는 완전히 무료입니다.

공식 답변 :
"All use of the Google Sheets API is available at no additional cost. Exceeding the quota request limits doesn't incur extra charges and your account is not billed."

제한 :
분당 500건(프로젝트), 분당 100건(유저) 정도 초과하면 잠깐 막힘
