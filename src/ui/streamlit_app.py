"""
네이버 키워드 도구 Streamlit 웹 애플리케이션

PC 16:9 비율에 최적화된 대시보드 형태의 GUI를 제공합니다.
왼쪽 패널: 검색 설정 및 API 인증 정보 입력
오른쪽 패널: 검색 결과 테이블과 차트 시각화
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from datetime import datetime
from io import BytesIO
import time

# 프로젝트 모듈 import
from src.api.naver_api import NaverKeywordAPI
from src.data.keyword_processor import KeywordProcessor
from src.utils.config_manager import ConfigManager
from src.utils.common import (
    setup_korean_font, 
    format_number, 
    validate_keyword,
    get_competition_color,
    create_excel_buffer
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 페이지 설정 - 16:9 비율 최적화
st.set_page_config(
    page_title="네이버 키워드 분석 도구",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 한글 폰트 설정
setup_korean_font()

def apply_custom_css():
    """커스텀 CSS 스타일 적용"""
    st.markdown("""
    <style>
        /* 전체 레이아웃 */
        .main > div {
            padding-top: 1rem !important;
        }
        
        .block-container {
            padding: 1rem 1.5rem !important;
            max-width: 100% !important;
        }
        
        /* 헤더 스타일 */
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .sub-title {
            font-size: 1rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* 패널 스타일 */
        .left-panel {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: calc(100vh - 120px);
            overflow-y: auto;
        }
        
        .right-panel {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: calc(100vh - 120px);
            overflow-y: auto;
        }
        
        /* 입력 필드 스타일 */
        .stTextInput > div > div > input {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* 버튼 스타일 */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        /* 검색 버튼 강조 */
        div[data-testid="column"]:nth-child(1) .stButton:last-child > button {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            font-size: 1.1rem;
            padding: 1rem;
            margin-top: 1rem;
        }
        
        div[data-testid="column"]:nth-child(1) .stButton:last-child > button:hover {
            background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        }
        
        /* 메트릭 카드 스타일 */
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* 테이블 스타일 */
        .dataframe {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e5e7eb;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* 섹션 제목 */
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #374151;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* 작은 텍스트 */
        .small-text {
            font-size: 0.875rem;
            color: #6b7280;
        }
        
        /* 성공 메시지 */
        .success-message {
            background: #d1fae5;
            color: #065f46;
            padding: 0.75rem;
            border-radius: 6px;
            border-left: 4px solid #10b981;
            margin: 1rem 0;
        }
        
        /* 에러 메시지 */
        .error-message {
            background: #fee2e2;
            color: #991b1b;
            padding: 0.75rem;
            border-radius: 6px;
            border-left: 4px solid #ef4444;
            margin: 1rem 0;
        }
        
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
        }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar_inputs():
    """왼쪽 패널 입력 영역 생성"""
    
    # 설정 관리자 초기화
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    # 기본값 로드
    credentials = st.session_state.config_manager.get_api_credentials()
    
    st.markdown('<div class="section-title">🔍 키워드 검색</div>', unsafe_allow_html=True)
    
    # 키워드 입력
    keyword = st.text_input(
        "검색 키워드",
        placeholder="분석하려는 메인 키워드를 입력하세요 (예: 비타민, 노트북)",
        help="연관 키워드를 분석할 메인 키워드를 입력하세요."
    )
    
    st.markdown('<div class="section-title">🔐 API 인증 정보</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-text">네이버 검색광고 API 인증 정보를 입력하세요.</div>', unsafe_allow_html=True)
    
    # API 인증 정보 입력
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
    
    st.markdown('<div class="section-title">⚙️ 설정 관리</div>', unsafe_allow_html=True)
    
    # 설정 관리 버튼
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("설정 저장", help="현재 입력된 API 정보를 저장합니다."):
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
    
    with col2:
        if st.button("설정 불러오기", help="저장된 API 정보를 불러옵니다."):
            credentials = st.session_state.config_manager.get_api_credentials()
            if all(credentials.values()):
                st.success("설정을 불러왔습니다!")
                st.rerun()
            else:
                st.warning("저장된 설정이 없습니다.")
    
    # 검색 실행 버튼
    search_clicked = st.button("🔍 키워드 분석 실행", help="입력된 키워드로 검색을 시작합니다.")
    
    return {
        'keyword': keyword,
        'customer_id': customer_id,
        'api_key': api_key,
        'secret_key': secret_key,
        'search_clicked': search_clicked
    }

def create_metrics_section(stats):
    """메트릭 섹션 생성"""
    if not stats:
        return
    
    st.markdown('<div class="section-title">📊 검색 결과 요약</div>', unsafe_allow_html=True)
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 키워드 수",
            value=format_number(stats.get('총 키워드 수', 0)),
            help="검색된 연관 키워드의 총 개수"
        )
    
    with col2:
        st.metric(
            label="총 검색량",
            value=format_number(stats.get('총 검색량 합계', 0)),
            help="모든 키워드의 월간 검색량 합계"
        )
    
    with col3:
        st.metric(
            label="평균 검색량",
            value=format_number(stats.get('평균 검색량', 0)),
            help="키워드당 평균 월간 검색량"
        )
    
    with col4:
        st.metric(
            label="PC 검색 비율",
            value=f"{stats.get('PC 검색 비율', 0):.1f}%",
            help="PC에서의 검색 비율"
        )

def create_keyword_chart(df, main_keyword):
    """키워드 차트 생성"""
    if df.empty:
        return
    
    st.markdown('<div class="section-title">📈 상위 키워드 검색량 분석</div>', unsafe_allow_html=True)
    
    # 상위 15개 키워드만 선택
    top_df = df.head(15).copy()
    
    # 메인 키워드 색상 구분
    colors = ['#ef4444' if keyword.lower() == main_keyword.lower() else '#3b82f6' 
              for keyword in top_df['키워드']]
    
    # 막대 차트 생성
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_df['키워드'],
        y=top_df['총 검색량'],
        marker_color=colors,
        text=[format_number(val) for val in top_df['총 검색량']],
        textposition='auto',
        textfont=dict(size=10, color='white'),
        hovertemplate='<b>%{x}</b><br>검색량: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"상위 키워드별 총 검색량",
            font=dict(size=16, color='#374151'),
            x=0.5
        ),
        xaxis=dict(
            title="키워드",
            title_font=dict(size=12),
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="검색량",
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        height=400,
        margin=dict(l=60, r=30, t=50, b=100),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    
    st.plotly_chart(fig, use_container_width=True)

def create_device_distribution_chart(df):
    """기기별 검색량 분포 차트"""
    if df.empty:
        return
    
    # PC와 모바일 검색량 합계 계산
    pc_total = df['PC'].sum()
    mobile_total = df['MOBILE'].sum()
    total = pc_total + mobile_total
    
    if total == 0:
        return
    
    # 도넛 차트 생성
    fig = go.Figure(data=[go.Pie(
        labels=['PC', 'Mobile'],
        values=[pc_total, mobile_total],
        hole=.3,
        marker_colors=['#3b82f6', '#10b981'],
        textinfo='label+percent',
        textfont=dict(size=12),
        hovertemplate='<b>%{label}</b><br>검색량: %{value:,}<br>비율: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="기기별 검색량 분포",
            font=dict(size=16, color='#374151'),
            x=0.5
        ),
        height=350,
        margin=dict(l=30, r=30, t=50, b=30),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_competition_chart(df):
    """경쟁정도 분포 차트"""
    if df.empty or '경쟁정도' not in df.columns:
        return
    
    # 경쟁정도별 개수 계산
    competition_counts = df['경쟁정도'].value_counts()
    
    if competition_counts.empty:
        return
    
    # 색상 매핑
    colors = [get_competition_color(comp) for comp in competition_counts.index]
    
    # 막대 차트 생성
    fig = go.Figure(data=[go.Bar(
        x=competition_counts.index,
        y=competition_counts.values,
        marker_color=colors,
        text=competition_counts.values,
        textposition='auto',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{x}</b><br>키워드 수: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="경쟁정도별 키워드 분포",
            font=dict(size=16, color='#374151'),
            x=0.5
        ),
        xaxis=dict(
            title="경쟁정도",
            title_font=dict(size=12),
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title="키워드 수",
            title_font=dict(size=12),
            tickfont=dict(size=11)
        ),
        height=350,
        margin=dict(l=60, r=30, t=50, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    
    st.plotly_chart(fig, use_container_width=True)

def create_results_table(df, main_keyword):
    """결과 테이블 생성"""
    if df.empty:
        return
    
    st.markdown('<div class="section-title">📋 연관 키워드 분석 결과</div>', unsafe_allow_html=True)
    
    # 표시할 컬럼 선택
    display_columns = ['키워드', '총 검색량', 'PC', 'MOBILE', '경쟁정도', '월평균 노출 광고수']
    display_df = df[display_columns].copy()
    
    # 메인 키워드 하이라이트를 위한 스타일 함수
    def highlight_main_keyword(row):
        if row['키워드'].lower() == main_keyword.lower():
            return ['background-color: #fef3c7; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    # 스타일 적용된 테이블 표시
    styled_df = display_df.style.apply(highlight_main_keyword, axis=1)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        column_config={
            "키워드": st.column_config.TextColumn("키워드", width="medium"),
            "총 검색량": st.column_config.NumberColumn("총 검색량", format="%d"),
            "PC": st.column_config.NumberColumn("PC", format="%d"),
            "MOBILE": st.column_config.NumberColumn("MOBILE", format="%d"),
            "경쟁정도": st.column_config.TextColumn("경쟁정도", width="small"),
            "월평균 노출 광고수": st.column_config.NumberColumn("월평균 노출 광고수", format="%.2f")
        }
    )
    
    # 다운로드 버튼
    if st.button("📊 Excel 파일 다운로드", help="검색 결과를 Excel 파일로 다운로드합니다."):
        try:
            processor = KeywordProcessor()
            processor.data = df
            
            excel_buffer, filename = processor.export_to_excel()
            
            st.download_button(
                label="다운로드 시작",
                data=excel_buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("Excel 파일이 준비되었습니다!")
            
        except Exception as e:
            st.error(f"Excel 파일 생성 중 오류가 발생했습니다: {str(e)}")

def perform_keyword_search(inputs):
    """키워드 검색 실행"""
    keyword = inputs['keyword']
    customer_id = inputs['customer_id']
    api_key = inputs['api_key']
    secret_key = inputs['secret_key']
    
    # 입력값 유효성 검사
    if not validate_keyword(keyword):
        st.error("올바른 키워드를 입력해주세요.")
        return None, None
    
    if not all([customer_id, api_key, secret_key]):
        st.error("모든 API 인증 정보를 입력해주세요.")
        return None, None
    
    try:
        # API 호출
        with st.spinner("키워드 검색 중..."):
            api = NaverKeywordAPI(customer_id, api_key, secret_key)
            keyword_list = api.search_keywords(keyword)
        
        if not keyword_list:
            st.warning("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
            return None, None
        
        # 데이터 처리
        processor = KeywordProcessor()
        df = processor.process_keyword_data(keyword_list, keyword)
        stats = processor.get_keyword_stats()
        
        # 세션에 저장
        st.session_state.last_search_keyword = keyword
        st.session_state.last_search_time = datetime.now()
        
        st.success(f"✅ '{keyword}' 검색 완료! {len(df)}개의 연관 키워드를 찾았습니다.")
        
        return df, stats
        
    except ValueError as e:
        st.error(f"🔐 인증 오류: {str(e)}")
        return None, None
    except ConnectionError as e:
        st.error(f"🌐 네트워크 오류: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"❌ 검색 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"키워드 검색 오류: {str(e)}")
        return None, None

def run_app():
    """메인 애플리케이션 실행"""
    
    # 커스텀 CSS 적용
    apply_custom_css()
    
    # 헤더
    st.markdown('<div class="main-title">🔍 네이버 키워드 분석 도구</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">네이버 검색광고 API를 활용한 키워드 트렌드 분석 및 시각화</div>', unsafe_allow_html=True)
    
    # 레이아웃: 왼쪽(입력) + 오른쪽(결과)
    left_col, right_col = st.columns([1, 2])
    
    # 왼쪽 패널: 입력 영역
    with left_col:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)
        inputs = create_sidebar_inputs()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 오른쪽 패널: 결과 영역
    with right_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        
        # 검색 실행
        if inputs['search_clicked']:
            df, stats = perform_keyword_search(inputs)
            
            if df is not None and not df.empty:
                # 세션에 결과 저장
                st.session_state.search_results = df
                st.session_state.search_stats = stats
                st.session_state.search_keyword = inputs['keyword']
        
        # 저장된 결과가 있으면 표시
        if 'search_results' in st.session_state and not st.session_state.search_results.empty:
            df = st.session_state.search_results
            stats = st.session_state.search_stats
            keyword = st.session_state.search_keyword
            
            # 메트릭 섹션
            create_metrics_section(stats)
            
            # 차트 섹션
            col1, col2 = st.columns(2)
            
            with col1:
                create_device_distribution_chart(df)
            
            with col2:
                create_competition_chart(df)
            
            # 키워드 차트
            create_keyword_chart(df, keyword)
            
            # 결과 테이블
            create_results_table(df, keyword)
            
        else:
            # 초기 상태 메시지
            st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; color: #6b7280;">
                <h3>🔍 키워드 분석을 시작하세요</h3>
                <p>왼쪽 패널에서 키워드와 API 정보를 입력한 후<br>
                '키워드 분석 실행' 버튼을 클릭하세요.</p>
                <br>
                <p><strong>📝 분석 가능한 정보:</strong></p>
                <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                    <li>연관 키워드별 월간 검색량</li>
                    <li>PC/모바일 기기별 검색 분포</li>
                    <li>키워드별 경쟁 정도</li>
                    <li>월평균 노출 광고수</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
