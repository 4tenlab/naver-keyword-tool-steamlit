import streamlit as st

st.set_page_config(
    page_title="테스트 앱",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Streamlit Cloud 테스트")
st.write("이 메시지가 보이면 배포가 성공한 것입니다!")

# Secrets 테스트
try:
    customer_id = st.secrets["api"]["CUSTOMER_ID"]
    st.success(f"✅ Secrets 정상 로드: Customer ID 끝자리 {customer_id[-4:]}")
except Exception as e:
    st.error(f"❌ Secrets 로드 실패: {str(e)}")

st.info("main.py로 다시 변경하여 테스트하세요!") 