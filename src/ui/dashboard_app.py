"""
네이버 키워드 도구 - 대시보드 형태 웹 애플리케이션

첨부된 스크린샷과 동일한 PC 16:9 비율 대시보드 레이아웃:
- 왼쪽: 입력 영역 (키워드, API 설정)
- 오른쪽 상단: 연관 키워드 분석 결과 테이블
- 오른쪽 하단: 상위 키워드 총 검색량 차트
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
from io import BytesIO
import time

# 프로젝트 모듈 import
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.api.naver_api import NaverKeywordAPI
    from src.data.keyword_processor import KeywordProcessor
    from src.utils.config_manager import ConfigManager
    from src.utils.common import (
        setup_korean_font, 
        format_number, 
        validate_keyword,
        get_competition_color
    )
except ImportError as e:
    # 상대 import로 시도
    sys.path.append(str(project_root / "src"))
    from api.naver_api import NaverKeywordAPI
    from data.keyword_processor import KeywordProcessor
    from utils.config_manager import ConfigManager
    from utils.common import (
        setup_korean_font, 
        format_number, 
        validate_keyword,
        get_competition_color
    )

# 로깅 설정
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="네이버 키워드 도구 v0.0.5",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 한글 폰트 설정
setup_korean_font()

def apply_dashboard_css():
    """shadcn/ui 스타일의 모던한 대시보드 CSS - v0.0.5"""
    st.markdown("""
    <style>
        /* 네이버 스타일 파스텔톤 색상 팔레트 */
        :root {
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --popover: 0 0% 100%;
            --popover-foreground: 222.2 84% 4.9%;
            --primary: 140 45% 65%;        /* 파스텔 초록색 */
            --primary-foreground: 0 0% 100%;
            --secondary: 200 80% 85%;      /* 포인트 하늘색 */
            --secondary-foreground: 222.2 84% 4.9%;
            --muted: 210 40% 96%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 10 65% 85%;          /* 연한 붉은색 포인트 */
            --accent-foreground: 222.2 84% 4.9%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 140 45% 65%;           /* 파스텔 초록색 */
            --radius: 0.5rem;
            --naver-green: #7fc93f;        /* 네이버 스타일 초록 */
            --naver-blue: #87ceeb;         /* 하늘색 */
            --naver-pink: #ffb3ba;         /* 연한 붉은색 */
        }
        
        /* 기본 레이아웃 초기화 */
        .main > div {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }
        
        .block-container {
            padding: 1.5rem !important;
            margin: 0rem !important;
            max-width: 100% !important;
        }
        
        /* Streamlit 요소 숨기기 */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        .stDeployButton {
            display: none !important;
        }
        
        div[data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Body 배경 */
        .stApp {
            background-color: hsl(var(--background));
        }
        

        
        /* shadcn/ui 카드 스타일 컬럼 - 2:4:4 비율 최적화 */
        div[data-testid="column"]:first-child {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: calc(var(--radius) + 2px);
            padding: 1.5rem;
            margin-right: 0.75rem;
            height: calc(100vh - 120px);
            overflow-y: auto;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            flex: 0 0 20% !important; /* 2/10 = 20% */
            max-width: 20% !important;
        }
        
        div[data-testid="column"]:last-child {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: calc(var(--radius) + 2px);
            padding: 1.5rem;
            margin-left: 0.75rem;
            height: calc(100vh - 120px);
            overflow-y: auto;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            flex: 0 0 80% !important; /* 8/10 = 80% */
            max-width: 80% !important;
        }
        
        /* 패널 div는 스타일 제거 */
        .left-panel {
            background: transparent;
            border: none;
            padding: 0;
            margin: 0;
        }
        
        .right-panel {
            background: transparent;
            border: none;
            padding: 0;
            margin: 0;
        }
        
        /* 테이블과 차트 섹션 간격 조정 */
        .table-section {
            background: transparent;
            border: none;
            border-right: 1px solid #d1d5db;
            padding: 0.5rem;
            padding-right: 1rem;
            margin-bottom: 1rem;
        }
        
        .chart-section {
            background: transparent;
            border: none;
            padding: 0.5rem;
            padding-left: 1rem;
            margin-top: 0.5rem;
        }
        
        /* 데이터프레임 컨테이너 스타일링 */
        div[data-testid="stDataFrame"] {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 0.5rem;
        }
        
        /* Plotly 차트 컨테이너 스타일링 */
        div[data-testid="stPlotlyChart"] {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 0.5rem;
        }
        
        /* shadcn/ui 입력 필드 스타일 */
        .stTextInput > div > div > input {
            border: 1px solid hsl(var(--input));
            border-radius: var(--radius);
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
            transition: all 0.2s ease-in-out;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: hsl(var(--ring));
            outline: 2px solid transparent;
            outline-offset: 2px;
            box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
        }
        
        /* shadcn/ui 버튼 스타일 */
        .stButton > button {
            background-color: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.875rem;
            width: 100%;
            margin: 0.25rem 0;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            background-color: hsl(var(--secondary) / 0.8);
            border-color: hsl(var(--border));
        }
        
        /* Primary 버튼 (검색 실행) - 네이버 브랜드 그린 #03C75A 세련된 그라데이션 */
        button.st-emotion-cache-3urvs.eacrzsf7,
        button[kind="primaryFormSubmit"],
        button[data-testid="baseButton-primaryFormSubmit"],
        div[data-testid="stForm"] button[kind="primary"],
        div[data-testid="stForm"] button[type="submit"],
        .search-button button,
        button[type="submit"],
        .stButton > button[kind="primary"],
        .stButton > button {
            background: linear-gradient(135deg, #03C75A 0%, #02B050 25%, #029943 75%, #028237 100%) !important;
            color: white !important;
            border: 1px solid #03C75A !important;
            font-weight: 600 !important;
            padding: 0.625rem 1rem !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 8px rgba(3, 199, 90, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        /* 버튼 내부 글로우 효과 */
        button.st-emotion-cache-3urvs.eacrzsf7::before,
        button[kind="primaryFormSubmit"]::before,
        button[data-testid="baseButton-primaryFormSubmit"]::before,
        div[data-testid="stForm"] button[kind="primary"]::before,
        div[data-testid="stForm"] button[type="submit"]::before,
        .search-button button::before,
        button[type="submit"]::before,
        .stButton > button[kind="primary"]::before,
        .stButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 100% !important;
            height: 100% !important;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
            transition: left 0.5s !important;
        }
        
        /* 호버 효과 - 더욱 세련된 애니메이션 */
        button.st-emotion-cache-3urvs.eacrzsf7:hover,
        button[kind="primaryFormSubmit"]:hover,
        button[data-testid="baseButton-primaryFormSubmit"]:hover,
        div[data-testid="stForm"] button[kind="primary"]:hover,
        div[data-testid="stForm"] button[type="submit"]:hover,
        .search-button button:hover,
        button[type="submit"]:hover,
        .stButton > button[kind="primary"]:hover,
        .stButton > button:hover {
            background: linear-gradient(135deg, #04D863 0%, #03C75A 25%, #02B050 75%, #029943 100%) !important;
            border-color: #04D863 !important;
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(3, 199, 90, 0.4), 0 0 20px rgba(3, 199, 90, 0.2) !important;
        }
        
        /* 호버 시 글로우 효과 활성화 */
        button.st-emotion-cache-3urvs.eacrzsf7:hover::before,
        button[kind="primaryFormSubmit"]:hover::before,
        button[data-testid="baseButton-primaryFormSubmit"]:hover::before,
        div[data-testid="stForm"] button[kind="primary"]:hover::before,
        div[data-testid="stForm"] button[type="submit"]:hover::before,
        .search-button button:hover::before,
        button[type="submit"]:hover::before,
        .stButton > button[kind="primary"]:hover::before,
        .stButton > button:hover::before {
            left: 100% !important;
        }
        
        /* 클릭 효과 */
        button.st-emotion-cache-3urvs.eacrzsf7:active,
        button[kind="primaryFormSubmit"]:active,
        button[data-testid="baseButton-primaryFormSubmit"]:active,
        div[data-testid="stForm"] button[kind="primary"]:active,
        div[data-testid="stForm"] button[type="submit"]:active,
        .search-button button:active,
        button[type="submit"]:active,
        .stButton > button[kind="primary"]:active,
        .stButton > button:active {
            transform: translateY(0) scale(0.98) !important;
            box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3) !important;
        }
        
        /* shadcn/ui 테이블 스타일 */
        .dataframe {
            font-size: 0.875rem;
            border-collapse: separate;
            border-spacing: 0;
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            overflow: hidden;
        }
        
        .dataframe th {
            background-color: hsl(var(--muted)) !important;
            color: hsl(var(--muted-foreground)) !important;
            font-weight: 600 !important;
            padding: 0.75rem 0.5rem !important;
            text-align: center !important;
            border-bottom: 1px solid hsl(var(--border)) !important;
            border-right: 1px solid hsl(var(--border)) !important;
        }
        
        .dataframe th:last-child {
            border-right: none !important;
        }
        
        .dataframe td {
            padding: 0.75rem 0.5rem !important;
            border-bottom: 1px solid hsl(var(--border)) !important;
            border-right: 1px solid hsl(var(--border)) !important;
            text-align: center !important;
            color: hsl(var(--foreground)) !important;
        }
        
        .dataframe td:last-child {
            border-right: none !important;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: hsl(var(--muted) / 0.3) !important;
        }
        
        .dataframe tr:hover {
            background-color: hsl(var(--muted) / 0.5) !important;
        }
        
        .dataframe tr:last-child td {
            border-bottom: none !important;
        }
        
        /* 메인 키워드 하이라이트 */
        .main-keyword-row {
            background-color: #fff2cc !important;
            font-weight: bold !important;
        }
        
        /* shadcn/ui 섹션 제목 */
        .section-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: hsl(var(--foreground));
            margin-bottom: 1rem;
            margin-top: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid hsl(var(--border));
            letter-spacing: -0.025em;
        }
        
        /* 설명 텍스트 */
        .description-text {
            font-size: 13px;
            color: #666;
            line-height: 1.4;
            margin-bottom: 20px;
        }
        
        /* 레이블 스타일 */
        .stTextInput > label {
            font-size: 14px;
            font-weight: 500;
            color: #333;
        }
        
        /* 메트릭 정보 */
        .metric-info {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 12px;
            color: #666;
        }
        
        /* 모든 Streamlit 버튼을 네이버 브랜드 그린으로 강제 변경 */
        button[class*="st-emotion-cache"] {
            background: linear-gradient(135deg, #03C75A 0%, #02B050 25%, #029943 75%, #028237 100%) !important;
            color: white !important;
            border: 1px solid #03C75A !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 8px rgba(3, 199, 90, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        button[class*="st-emotion-cache"]:hover {
            background: linear-gradient(135deg, #04D863 0%, #03C75A 25%, #02B050 75%, #029943 100%) !important;
            border-color: #04D863 !important;
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(3, 199, 90, 0.4), 0 0 20px rgba(3, 199, 90, 0.2) !important;
        }
        
        button[class*="st-emotion-cache"]:active {
            transform: translateY(0) scale(0.98) !important;
            box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3) !important;
        }
    </style>
    
    <script>
    // 버튼 색상을 네이버 초록색으로 강제 변경하는 JavaScript
    function applyGreenButtonStyle() {
        // 모든 버튼을 찾아서 색상 변경
        const buttons = document.querySelectorAll('button[kind="primary"], button[type="submit"], .stButton > button');
        buttons.forEach(button => {
            if (button.textContent.includes('검색') || 
                button.textContent.includes('분석') || 
                button.textContent.includes('실행') ||
                button.getAttribute('type') === 'submit') {
                button.style.background = 'linear-gradient(to bottom, #a8e6cf, #7fc93f)';
                button.style.color = 'white';
                button.style.border = '1px solid #7fc93f';
                button.style.fontWeight = '600';
                
                // 호버 효과
                button.addEventListener('mouseenter', function() {
                    this.style.background = 'linear-gradient(to bottom, #7fc93f, #6fb32a)';
                    this.style.borderColor = '#6fb32a';
                    this.style.transform = 'translateY(-1px)';
                    this.style.boxShadow = '0 4px 12px rgba(168, 230, 207, 0.4)';
                });
                
                button.addEventListener('mouseleave', function() {
                    this.style.background = 'linear-gradient(to bottom, #a8e6cf, #7fc93f)';
                    this.style.borderColor = '#7fc93f';
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = 'none';
                });
            }
        });
    }
    
    // 페이지 로드 후 실행
    document.addEventListener('DOMContentLoaded', applyGreenButtonStyle);
    
    // Streamlit 재렌더링 후에도 실행
    const observer = new MutationObserver(applyGreenButtonStyle);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // 주기적으로 실행 (Streamlit의 동적 렌더링 대응)
    setInterval(applyGreenButtonStyle, 1000);
    </script>
    """, unsafe_allow_html=True)

def create_left_panel():
    """왼쪽 패널 - 입력 영역"""
    
    # 설정 관리자 초기화
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    # Streamlit Secrets에서 API 키 가져오기 (우선순위)
    try:
        secrets_credentials = {
            'customer_id': st.secrets["api"]["CUSTOMER_ID"],
            'api_key': st.secrets["api"]["API_KEY"],
            'secret_key': st.secrets["api"]["SECRET_KEY"]
        }
        # secrets에 실제 값이 있는지 확인 (placeholder 값이 아닌지)
        if all(val and val != "your_customer_id_here" and val != "your_api_key_here" and val != "your_secret_key_here" 
               for val in secrets_credentials.values()):
            credentials = secrets_credentials
            use_secrets = True
        else:
            # 설정 관리자에서 저장된 인증 정보 가져오기 (fallback)
            credentials = st.session_state.config_manager.get_api_credentials()
            use_secrets = False
    except (KeyError, AttributeError):
        # Secrets가 없으면 설정 관리자에서 가져오기
        credentials = st.session_state.config_manager.get_api_credentials()
        use_secrets = False
    
    # 제목과 설명 - shadcn/ui 스타일
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.5rem; font-weight: 700; color: hsl(var(--foreground)); margin-bottom: 0.5rem; letter-spacing: -0.025em;">
            📊 네이버 키워드 도구 v0.0.5
        </h1>
        <p style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin: 0;">
            키워드 검색량과 경쟁정도를 분석합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 키워드 입력 (엔터키 지원)
    with st.form("search_form", clear_on_submit=False):
        keyword = st.text_input(
            "검색 키워드",
            placeholder="비타민",
            help="분석하려는 메인 키워드를 입력하세요 (엔터키로 검색 실행)",
            key="keyword_input"
        )
        # 숨겨진 submit 버튼 (엔터키용)
        form_submitted = st.form_submit_button("검색", type="primary", use_container_width=True)
    
    # API 인증 정보 표시
    if use_secrets and credentials.get('customer_id'):
        # Secrets에서 불러온 경우 안전하게 표시
        st.success("🔐 Streamlit Secrets에서 API 키를 자동으로 불러왔습니다.")
        
        st.text_input(
            "CUSTOMER_ID",
            value="*" * 8 + credentials['customer_id'][-4:] if len(credentials['customer_id']) > 4 else "****",
            disabled=True,
            help="Streamlit Secrets에서 자동으로 불러온 값입니다."
        )
        customer_id = credentials['customer_id']
        
        st.text_input(
            "API_KEY",
            value="*" * 20 + "...",
            disabled=True,
            help="Streamlit Secrets에서 자동으로 불러온 값입니다."
        )
        api_key = credentials['api_key']
        
        st.text_input(
            "SECRET_KEY",
            value="*" * 20 + "...",
            disabled=True,
            help="Streamlit Secrets에서 자동으로 불러온 값입니다."
        )
        secret_key = credentials['secret_key']
    else:
        # 수동 입력 모드
        st.info("💡 API 키를 직접 입력하거나 Streamlit Secrets를 설정하세요.")
        
        customer_id = st.text_input(
            "CUSTOMER_ID",
            value=credentials.get('customer_id', ''),
            type="password",
            help="네이버 검색광고 고객 ID를 입력하세요."
        )
        
        api_key = st.text_input(
            "API_KEY",
            value=credentials.get('api_key', ''),
            type="password",
            help="네이버 검색광고 API 키를 입력하세요."
        )
        
        secret_key = st.text_input(
            "SECRET_KEY",
            value=credentials.get('secret_key', ''),
            type="password",
            help="네이버 검색광고 시크릿 키를 입력하세요."
        )
    
    # 버튼 영역
    col1, col2 = st.columns(2)
    
    with col1:
        save_clicked = st.button("설정 저장")
        
    with col2:
        load_clicked = st.button("설정 불러오기")
    
    # 검색 실행 버튼 (추가 검색용)
    st.markdown('<div class="search-button">', unsafe_allow_html=True)
    search_clicked = st.button("추가 분석 실행")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 엑셀 다운로드 버튼
    excel_clicked = st.button("엑셀 다운로드")
    
    # 설정 저장/불러오기 처리
    if save_clicked:
        if customer_id and api_key and secret_key:
            success = st.session_state.config_manager.set_api_credentials(
                customer_id, api_key, secret_key
            )
            if success:
                st.success("설정이 저장되었습니다!")
            else:
                st.error("설정 저장에 실패했습니다.")
        else:
            st.warning("모든 API 정보를 입력해주세요.")
    
    if load_clicked:
        credentials = st.session_state.config_manager.get_api_credentials()
        if all(credentials.values()):
            st.success("설정을 불러왔습니다!")
            st.rerun()
        else:
            st.warning("저장된 설정이 없습니다.")
    
    return {
        'keyword': keyword,
        'customer_id': customer_id,
        'api_key': api_key,
        'secret_key': secret_key,
        'search_clicked': search_clicked or form_submitted,  # 폼 제출도 검색으로 처리
        'excel_clicked': excel_clicked
    }

def create_results_table(df, main_keyword):
    """결과 테이블 생성"""
    if df.empty:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #888;">
            검색 결과가 없습니다. 키워드를 입력하고 분석을 실행하세요.
        </div>
        """, unsafe_allow_html=True)
        return

    # 테이블 정보
    search_date = datetime.now().strftime("%Y-%m-%d ~ %Y-%m-%d")
    st.markdown(f"""
    <div style="font-size: 12px; color: #666; margin-bottom: 10px;">
    최종 기준: {search_date} &nbsp;&nbsp;&nbsp;&nbsp; 검색 결과를 클릭하여 정렬할 수 있습니다
    </div>
    """, unsafe_allow_html=True)
    
    # 표시할 컬럼만 선택
    display_columns = ['키워드', '총 검색량', 'PC', 'MOBILE', '경쟁정도', '월평균 노출 광고수']
    display_df = df[display_columns].copy()
    
    # 인덱스를 1부터 시작하도록 설정
    display_df.index = range(1, len(display_df) + 1)
    
    # 테이블 표시 - 높이를 고정하고 스크롤 가능하게
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,  # 차트와 동일한 높이로 조정
        column_config={
            "키워드": st.column_config.TextColumn("키워드", width="medium"),
            "총 검색량": st.column_config.NumberColumn("총 검색량", format="%d"),
            "PC": st.column_config.NumberColumn("PC", format="%d"),
            "MOBILE": st.column_config.NumberColumn("MOBILE", format="%d"),
            "경쟁정도": st.column_config.TextColumn("경쟁정도", width="small"),
            "월평균 노출 광고수": st.column_config.NumberColumn("월평균 노출 광고수", format="%.2f")
        }
    )

def create_keyword_chart(df, main_keyword):
    """키워드 차트 생성 - 스크린샷과 동일한 스타일"""
    if df.empty:
        return
    

    
    # 상위 15개 키워드만 선택
    top_df = df.head(15).copy()
    
    # 네이버 스타일 파스텔톤 색상
    colors = []
    for keyword in top_df['키워드']:
        if keyword.lower() == main_keyword.lower():
            colors.append('#ffb3ba')  # 연한 붉은색 포인트 (메인 키워드)
        else:
            colors.append('#87ceeb')  # 포인트 하늘색
    
    # 막대 차트 생성
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_df['키워드'],
        y=top_df['총 검색량'],
        marker_color=colors,
        text=[format_number(val) for val in top_df['총 검색량']],
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{x}</b><br>검색량: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e2e8f0',
            tickfont=dict(size=10)
        ),
        height=400,
        margin=dict(l=60, r=30, t=30, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", size=10)
    )
    
    # shadcn/ui 스타일 그리드
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
    fig.update_xaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

def perform_search(inputs):
    """검색 실행"""
    keyword = inputs['keyword']
    customer_id = inputs['customer_id']
    api_key = inputs['api_key']
    secret_key = inputs['secret_key']
    
    # 입력값 검증
    if not validate_keyword(keyword):
        st.error("올바른 키워드를 입력해주세요.")
        return None
    
    if not all([customer_id, api_key, secret_key]):
        st.error("모든 API 인증 정보를 입력해주세요.")
        return None
    
    try:
        # API 호출
        with st.spinner("키워드 검색 중..."):
            api = NaverKeywordAPI(customer_id, api_key, secret_key)
            keyword_list = api.search_keywords(keyword)
        
        if not keyword_list:
            st.warning("검색 결과가 없습니다.")
            return None
        
        # 데이터 처리
        processor = KeywordProcessor()
        df = processor.process_keyword_data(keyword_list, keyword)
        
        st.success(f"✅ '{keyword}' 검색 완료! {len(df)}개의 연관 키워드를 찾았습니다.")
        return df
        
    except ValueError as e:
        st.error(f"🔐 API 인증 오류: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ 검색 중 오류 발생: {str(e)}")
        logger.error(f"검색 오류: {str(e)}")
        return None

def handle_excel_download(df):
    """엑셀 다운로드 처리"""
    if df is None or df.empty:
        st.warning("다운로드할 데이터가 없습니다.")
        return
    
    try:
        processor = KeywordProcessor()
        processor.data = df
        
        excel_buffer, filename = processor.export_to_excel()
        
        st.download_button(
            label="📊 Excel 파일 다운로드",
            data=excel_buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.success("Excel 파일이 준비되었습니다!")
        
    except Exception as e:
        st.error(f"Excel 파일 생성 중 오류: {str(e)}")

def run_dashboard():
    """대시보드 메인 실행 함수"""
    
    # CSS 적용
    apply_dashboard_css()
    
    # JavaScript로 버튼 색상 강제 변경
    st.markdown("""
    <script>
    function forceNaverGreenButtons() {
        // 모든 버튼을 찾아서 네이버 브랜드 그린으로 변경
        const buttons = document.querySelectorAll('button, .stButton > button, button[class*="st-emotion-cache"]');
        buttons.forEach(button => {
            // 네이버 브랜드 그린 세련된 그라데이션 적용
            button.style.setProperty('background', 'linear-gradient(135deg, #03C75A 0%, #02B050 25%, #029943 75%, #028237 100%)', 'important');
            button.style.setProperty('color', 'white', 'important');
            button.style.setProperty('border', '1px solid #03C75A', 'important');
            button.style.setProperty('font-weight', '600', 'important');
            button.style.setProperty('border-radius', '8px', 'important');
            button.style.setProperty('box-shadow', '0 2px 8px rgba(3, 199, 90, 0.25)', 'important');
            button.style.setProperty('transition', 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', 'important');
            button.style.setProperty('position', 'relative', 'important');
            button.style.setProperty('overflow', 'hidden', 'important');
            
            // 호버 이벤트 추가 - 세련된 애니메이션
            button.addEventListener('mouseenter', function() {
                this.style.setProperty('background', 'linear-gradient(135deg, #04D863 0%, #03C75A 25%, #02B050 75%, #029943 100%)', 'important');
                this.style.setProperty('border-color', '#04D863', 'important');
                this.style.setProperty('transform', 'translateY(-2px) scale(1.02)', 'important');
                this.style.setProperty('box-shadow', '0 8px 25px rgba(3, 199, 90, 0.4), 0 0 20px rgba(3, 199, 90, 0.2)', 'important');
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.setProperty('background', 'linear-gradient(135deg, #03C75A 0%, #02B050 25%, #029943 75%, #028237 100%)', 'important');
                this.style.setProperty('border-color', '#03C75A', 'important');
                this.style.setProperty('transform', 'translateY(0) scale(1)', 'important');
                this.style.setProperty('box-shadow', '0 2px 8px rgba(3, 199, 90, 0.25)', 'important');
            });
            
            // 클릭 이벤트 추가
            button.addEventListener('mousedown', function() {
                this.style.setProperty('transform', 'translateY(0) scale(0.98)', 'important');
                this.style.setProperty('box-shadow', '0 2px 8px rgba(3, 199, 90, 0.3)', 'important');
            });
            
            button.addEventListener('mouseup', function() {
                this.style.setProperty('transform', 'translateY(-2px) scale(1.02)', 'important');
                this.style.setProperty('box-shadow', '0 8px 25px rgba(3, 199, 90, 0.4), 0 0 20px rgba(3, 199, 90, 0.2)', 'important');
            });
        });
    }
    
         // 즉시 실행
     forceNaverGreenButtons();
     
     // 500ms 후 다시 실행
     setTimeout(forceNaverGreenButtons, 500);
     
     // 1초 후 다시 실행
     setTimeout(forceNaverGreenButtons, 1000);
     
     // 2초 후 다시 실행
     setTimeout(forceNaverGreenButtons, 2000);
     
     // MutationObserver로 DOM 변경 감지
     const observer = new MutationObserver(forceNaverGreenButtons);
    observer.observe(document.body, { 
        childList: true, 
        subtree: true, 
        attributes: true, 
        attributeFilter: ['class', 'style'] 
    });
    </script>
    """, unsafe_allow_html=True)
    
    # 전체 컨테이너에 최소 패딩 추가
    st.markdown('<div style="padding: 0.5rem;">', unsafe_allow_html=True)
    
    # 레이아웃: 왼쪽(2) + 오른쪽(8) = 2:4:4 비율 (오른쪽은 내부에서 4:4로 분할)
    left_col, right_col = st.columns([2, 8])
    
    # 왼쪽 패널
    with left_col:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)
        inputs = create_left_panel()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 오른쪽 패널
    with right_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        
        # 검색 실행 (버튼 클릭 또는 엔터키)
        if inputs['search_clicked']:
            df = perform_search(inputs)
            if df is not None:
                st.session_state.search_results = df
                st.session_state.search_keyword = inputs['keyword']
        
        # 엑셀 다운로드
        if inputs['excel_clicked']:
            if 'search_results' in st.session_state:
                handle_excel_download(st.session_state.search_results)
            else:
                st.warning("다운로드할 검색 결과가 없습니다.")
        
        # 결과 표시
        if 'search_results' in st.session_state:
            df = st.session_state.search_results
            keyword = st.session_state.search_keyword
            
            # 분석 결과 레이아웃 설정
            st.markdown("### 📊 분석 결과")
            
            # 중앙:우측 = 4:4 비율로 컬럼 생성
            table_col, chart_col = st.columns([4, 4])
            
            with table_col:
                st.markdown('<div class="table-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🗂️ 연관 키워드 분석결과 (키워드 리스트)</div>', unsafe_allow_html=True)
                create_results_table(df, keyword)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with chart_col:
                st.markdown('<div class="chart-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📈 상위 키워드별 총 검색량 (그래프)</div>', unsafe_allow_html=True)
                create_keyword_chart(df, keyword)
                st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # 초기 상태 - shadcn/ui 스타일
            st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; color: hsl(var(--muted-foreground));">
                <div style="background-color: hsl(var(--muted) / 0.3); border-radius: var(--radius); padding: 2rem; border: 1px dashed hsl(var(--border));">
                    <h4 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: hsl(var(--foreground));">🔍 키워드 분석 준비</h4>
                    <p style="font-size: 0.875rem; margin: 0;">키워드와 API 정보를 입력 후 분석을 실행하세요.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 전체 컨테이너 닫기
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_dashboard() 