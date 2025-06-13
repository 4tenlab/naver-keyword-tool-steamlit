import streamlit as st
import json
import requests
import hmac, hashlib, base64, time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
import matplotlib as mpl

# 한글 폰트 설정
import platform
system = platform.system()
if system == "Windows":
    # Windows 환경 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    mpl.rc('font', family='Malgun Gothic')
elif system == "Darwin":
    # macOS 환경 한글 폰트 설정
    plt.rcParams['font.family'] = 'AppleGothic'
    mpl.rc('font', family='AppleGothic')
else:
    # Linux 등 기타 환경 한글 폰트 설정
    try:
        # 나눔 폰트 등 한글 지원 폰트가 있으면 사용
        plt.rcParams['font.family'] = 'NanumGothic, Nanum Gothic'
        mpl.rc('font', family='NanumGothic, Nanum Gothic')
    except:
        # 폰트 설정이 불가능하면 경고만 출력
        print("Warning: 한글 폰트를 설정할 수 없습니다. 그래프에서 한글이 깨질 수 있습니다.")

# matplotlib에서 음수 표시 문제 해결
mpl.rcParams['axes.unicode_minus'] = False

# 페이지 설정 - 와이드 모드로 설정하여 화면을 최대한 활용
st.set_page_config(
    page_title="네이버 키워드 도구 v0.0.5",
    page_icon="🔍",
    layout="wide",  # 와이드 모드로 설정
    initial_sidebar_state="collapsed"  # 사이드바 초기 상태 숨김
)

# 커스텀 CSS 추가
st.markdown("""
<style>
    /* 전체 앱 스타일 */
    .main > div {
        padding-top: 0.5rem !important;
    }
    
    /* 여백 제거 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
        max-width: 95% !important;
    }
    
    /* 헤더 스타일 */
    .main-header {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    
    /* 서브헤더 스타일 */
    .sub-header {
        font-size: 1.2rem;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-weight: bold;
        color: #333;
    }
    
    /* 왼쪽 패널 스타일 */
    .left-panel {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-right: 1rem;
    }
    
    /* 오른쪽 패널 스타일 */
    .right-panel {
        background-color: #fff;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 0.8rem;
    }
    
    /* 테이블 스타일 */
    .table-container {
        height: 300px;
        overflow-y: auto;
        border: 1px solid #e5e5e5;
        border-radius: 5px;
    }
    
    /* 그래프 컨테이너 스타일 */
    .graph-container {
        background-color: white;
        border: 1px solid #e5e5e5;
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border: 1.5px solid #d1d1d6;
        border-radius: 8px;
        padding: 8px 12px;
    }
    .stTextInput > div > div > input:focus {
        border: 1.5px solid #a6dcef;
        box-shadow: none;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(to bottom, #a6dcef, #7fbfe0);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: #7fbfe0;
    }
    
    /* 엑셀 다운로드 버튼 스타일 */
    .download-button {
        margin-top: 0.5rem;
    }
    .download-button > button {
        background: linear-gradient(to bottom, #a8e6cf, #88d8b0);
        color: white;
    }
    
    /* 간격 줄이기 */
    .row-widget {
        margin-bottom: 0.5rem !important;
    }
    
    /* 데이터프레임 스타일 */
    div[data-testid="stDataFrame"] {
        width: 100%;
    }
    
    /* DataEditor 높이 조정 */
    .stDataFrame > div:has(> iframe) {
        height: 300px !important;
    }
    
    /* 메시지 스타일 */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.5rem 0;
    }
    
    /* 정보 컨테이너 */
    .info-container {
        margin: 0.3rem 0 !important;
        padding: 0 !important;
    }
    
    /* 체크박스 마진 제거 */
    .stCheckbox {
        margin-bottom: 0 !important;
    }
    
    /* 텍스트 라벨 여백 줄이기 */
    p {
        margin-bottom: 0.3rem !important;
    }
    
    /* 헤더 여백 줄이기 */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0 !important;
        margin-bottom: 0.3rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 설정 파일 관련 함수
CONFIG_FILE = 'naver_keyword_config.json'

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

# 네이버 API 관련 함수
def generate_signature(timestamp, method, uri, secret_key):
    msg = f"{timestamp}.{method}.{uri}"
    hash = hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(hash.digest()).decode()

def search_keywords(keyword, customer_id, api_key, secret_key):
    BASE_URL = 'https://api.searchad.naver.com'
    uri = '/keywordstool'
    url = BASE_URL + uri
    method = 'GET'
    keyword_param = keyword.replace(' ', '')
    params = {'hintKeywords': keyword_param, 'showDetail': 1}
    timestamp = str(round(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri, secret_key)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }
    
    try:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json().get('keywordList', [])
    except Exception as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {str(e)}")
        return []

# 데이터 처리 및 시각화 함수
def process_keyword_data(keyword_list, main_keyword):
    if not keyword_list:
        return pd.DataFrame()
    
    data = []
    for item in keyword_list:
        # None 값이나 비 정수 값을 처리하기 위해 안전하게 가져오기
        pc_count = item.get('monthlyPcQcCnt', 0)
        mobile_count = item.get('monthlyMobileQcCnt', 0)
        
        # None 값 확인 및 정수 변환 (문자열 값도 처리)
        pc_count = safe_convert_to_int(pc_count)
        mobile_count = safe_convert_to_int(mobile_count)
        
        # 월평균 노출 광고수도 안전하게 처리
        avg_depth = item.get('plAvgDepth', 0)
        avg_depth = safe_convert_to_int(avg_depth)
        
        row = {
            '키워드': item.get('relKeyword', ''),
            '총 검색량': pc_count + mobile_count,
            'PC': pc_count,
            'MOBILE': mobile_count,
            '경쟁정도': item.get('compIdx', ''),
            '월평균 노출 광고수': avg_depth,
            # 검색 키워드와 동일한지 여부 저장
            '메인키워드': item.get('relKeyword', '') == main_keyword
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    # 정렬
    df = df.sort_values(by='총 검색량', ascending=False)
    return df

# 안전하게 정수로 변환하는 함수 추가
def safe_convert_to_int(value):
    if value is None:
        return 0
    
    # 이미 정수인 경우
    if isinstance(value, int):
        return value
    
    # 문자열인 경우
    if isinstance(value, str):
        # '< 10'과 같은 값 처리
        if '<' in value:
            # < 기호가 있으면 작은 값으로 처리 (예: '< 10'은 5로 처리)
            try:
                # 숫자 부분만 추출하여 절반 값으로 반환
                num_part = value.replace('<', '').strip()
                return int(int(num_part) / 2)
            except:
                return 0
        
        # 일반 숫자 문자열인 경우
        try:
            return int(value)
        except:
            return 0
    
    # 그 외 케이스
    try:
        return int(value)
    except:
        return 0

def draw_keyword_graph(df, main_keyword):
    if df.empty:
        return None
    
    # 상위 15개 키워드만 사용
    top_df = df.head(15).copy()
    
    # 그래프 생성 - 작은 크기로 조정
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # 데이터 시각화 - 메인 키워드와 나머지 키워드 구분
    bars = []
    for i, (_, row) in enumerate(top_df.iterrows()):
        if row['메인키워드']:
            bar = ax.bar(i, row['총 검색량'], color='red', width=0.7)
        else:
            bar = ax.bar(i, row['총 검색량'], color='blue', width=0.7)
        bars.append(bar)
    
    # 바 위에 값 표시
    for i, bar in enumerate(ax.patches):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height + 5,
            f'{int(height):,}',
            ha='center', 
            va='bottom',
            fontsize=8
        )
    
    # 축 레이블 및 타이틀 설정
    ax.set_title('상위 키워드별 총 검색량', fontsize=12, pad=10)
    ax.set_ylabel('검색량', fontsize=10)
    
    # X축 설정
    ax.set_xticks(range(len(top_df)))
    ax.set_xticklabels(top_df['키워드'], rotation=45, ha='right', fontsize=8)
    
    # 그리드 설정
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # 여백 최소화
    plt.tight_layout()
    
    return fig

# 앱 메인 코드
def main():
    # 기본값 설정
    default_values = {
        "customer_id": "1606492",
        "api_key": "0100000000dc897c13f61383de5adb2ed865838918b6260db6710f1949dc74795da1b2e53e",
        "secret_key": "AQAAAADciXwT9hOD3lrbLthlg4kYTPfLKERBgDLqGB3VN4N08g=="
    }
    
    # 앱 헤더 - 상단 중앙에 배치
    st.markdown('<h1 class="main-header" style="text-align: center;">네이버 키워드 도구 v0.0.5</h1>', unsafe_allow_html=True)
    
    # 좌우 2개 컬럼으로 나누기 (왼쪽 3, 오른쪽 7 비율)
    left_col, right_col = st.columns([3, 7])
    
    # 왼쪽 패널 (입력 폼)
    with left_col:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)
        
        # 검색 키워드 입력
        st.markdown('<h3 class="sub-header">검색 키워드</h3>', unsafe_allow_html=True)
        keyword = st.text_input("", placeholder="분석하려는 메인 키워드를 입력하세요", key="keyword_input", label_visibility="collapsed")
        
        # API 설정 섹션
        st.markdown('<h3 class="sub-header">API 설정</h3>', unsafe_allow_html=True)
        
        # 폼 입력 필드
        customer_id = st.text_input("CUSTOMER_ID", value=default_values["customer_id"])
        api_key = st.text_input("API_KEY", value=default_values["api_key"], type="password")
        secret_key = st.text_input("SECRET_KEY", value=default_values["secret_key"], type="password")
        
        # 버튼 그룹
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_btn = st.button("설정 저장", use_container_width=True)
        
        with col2:
            load_btn = st.button("설정 불러오기", use_container_width=True)
                
        with col3:
            analyze_btn = st.button("분석 실행", use_container_width=True)
        
        # 성공/경고 메시지 영역
        if save_btn:
            config = {
                "customer_id": customer_id,
                "api_key": api_key,
                "secret_key": secret_key
            }
            save_config(config)
            st.markdown('<div class="success-message">✅ 설정이 저장되었습니다.</div>', unsafe_allow_html=True)
        
        if load_btn:
            config = load_config()
            if config:
                st.session_state.customer_id = config.get("customer_id", "")
                st.session_state.api_key = config.get("api_key", "")
                st.session_state.secret_key = config.get("secret_key", "")
                st.experimental_rerun()
            else:
                st.warning("⚠️ 저장된 설정이 없습니다.")
        
        # 분석 실행 처리
        if analyze_btn:
            if not keyword:
                st.warning("⚠️ 키워드를 입력해주세요.")
            else:
                with st.spinner('키워드 데이터를 분석 중입니다...'):
                    # API 호출
                    keyword_list = search_keywords(keyword, customer_id, api_key, secret_key)
                    
                    if keyword_list:
                        # 데이터 처리
                        df = process_keyword_data(keyword_list, keyword)
                        
                        # 세션 상태에 저장
                        st.session_state.df = df
                        st.session_state.keyword = keyword
                        
                        # 성공 메시지
                        st.markdown(f'<div class="success-message">✅ \'{keyword}\' 키워드 분석이 완료되었습니다.</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ 검색 결과가 없습니다. API 설정을 확인해주세요.")
        
        # 키워드 분석 상태 표시
        if 'keyword' in st.session_state:
            st.markdown(f'<div class="success-message">✅ \'{st.session_state.keyword}\' 키워드 분석이 완료되었습니다.</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 오른쪽 패널 (결과 표시)
    with right_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        
        if 'df' in st.session_state and not st.session_state.df.empty:
            # 연관 키워드 분석 결과 헤더와 정보 표시
            result_cols = st.columns([2, 1, 1])
            with result_cols[0]:
                st.markdown('<h3 class="sub-header">연관 키워드 분석 결과</h3>', unsafe_allow_html=True)
            
            # 정보 표시 (조회 기간, 검색 키워드)
            now = datetime.datetime.now()
            thirty_days_ago = now - datetime.timedelta(days=30)
            with result_cols[1]:
                st.markdown(f'<div class="info-container">조회 기준: {thirty_days_ago.strftime("%Y-%m-%d")} ~ {now.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
            with result_cols[2]:
                st.markdown(f'<div class="info-container">검색 키워드: {st.session_state.keyword}</div>', unsafe_allow_html=True)
            
            # 그래프와 테이블 레이아웃
            # 그래프 표시
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            fig = draw_keyword_graph(st.session_state.df, st.session_state.keyword)
            if fig:
                st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 데이터 테이블 표시
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            
            # 데이터프레임 표시
            df_display = st.session_state.df.drop(columns=['메인키워드']).reset_index(drop=True)
            
            # 메인 키워드에 색상 추가를 위해 스타일 적용
            def highlight_main_keyword(row):
                if row.name < len(st.session_state.df) and st.session_state.df.iloc[row.name]['메인키워드']:
                    return ['color: red' if col == '키워드' else '' for col in row.index]
                return [''] * len(row)
            
            styled_df = df_display.style.apply(highlight_main_keyword, axis=1)
            
            # 높이 조정해서 표시
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=300
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 엑셀 다운로드 버튼
            excel_file = BytesIO()
            df_display.to_excel(excel_file, index=False, engine='openpyxl')
            excel_file.seek(0)
            
            st.markdown('<div class="download-button">', unsafe_allow_html=True)
            st.download_button(
                label="엑셀 다운로드",
                data=excel_file,
                file_name=f"네이버_키워드_분석_{st.session_state.keyword}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 결과가 없을 때 안내 메시지
            st.info("키워드를 입력하고 분석 실행 버튼을 클릭하면 결과가 여기에 표시됩니다.")
            
            # 사용 방법 안내
            st.markdown("""
            #### 네이버 키워드 도구 사용 방법
            
            1. **왼쪽 패널**에서 분석할 키워드를 입력하세요
            2. API 설정 정보를 확인하세요
            3. **분석 실행** 버튼을 클릭하세요
            4. 결과는 이 영역에 그래프와 테이블로 표시됩니다
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 