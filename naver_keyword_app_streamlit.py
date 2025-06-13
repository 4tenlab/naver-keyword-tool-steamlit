import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
import hmac, hashlib, base64, time
import datetime
from io import BytesIO
import os

# 페이지 설정
st.set_page_config(
    page_title="네이버 키워드 분석 툴",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'keyword_history' not in st.session_state:
    st.session_state.keyword_history = []
if 'raw_keyword_data' not in st.session_state:
    st.session_state.raw_keyword_data = None

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

# 안전하게 정수로 변환하는 함수
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

# 데이터 처리 함수
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
        avg_ad_count = item.get('monthlyAvePcCtr', 0)
        avg_ad_count = safe_convert_to_int(avg_ad_count)
        
        row = {
            '키워드': item.get('relKeyword', ''),
            '총 검색량': pc_count + mobile_count,
            'PC': pc_count,
            'MOBILE': mobile_count,
            '경쟁정도': item.get('compIdx', '-'),
            '월평균 노출 광고수': avg_ad_count,
            # 검색 키워드와 동일한지 여부 저장
            '메인키워드': item.get('relKeyword', '').lower() == main_keyword.lower()
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    # 정렬
    df = df.sort_values(by='총 검색량', ascending=False)
    return df

# 키워드 시각화 함수
@st.cache_data(ttl=3600)
def create_keyword_trend_data(keyword, volume):
    """키워드 트렌드 데이터 생성 (시뮬레이션)"""
    # 실제 API에서는 이 함수를 실제 트렌드 데이터 호출로 대체해야 함
    end_date = datetime.datetime.now()
    dates = pd.date_range(end=end_date, periods=180)
    
    # 계절성과 약간의 랜덤 변동 추가
    base_volume = volume / 30  # 일 평균 검색량
    trend_data = []
    
    for i, date in enumerate(dates):
        # 계절성 + 랜덤 요소
        seasonal = np.sin(i * 0.1) * 0.3
        weekly = np.sin(i * 0.7) * 0.15  # 주간 패턴
        random_factor = np.random.uniform(0.7, 1.3)
        volume_i = int(base_volume * (1 + seasonal + weekly) * random_factor)
        trend_data.append({'date': date, 'volume': volume_i})
    
    return pd.DataFrame(trend_data)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }
    
    .api-config-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .search-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .keyword-list-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .keyword-item {
        padding: 1rem;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .keyword-item:last-child {
        border-bottom: none;
    }
    
    .keyword-item:hover {
        background-color: #f8fafc;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-success {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🔍 네이버 키워드 분석 툴</h1>
    <p>네이버 검색광고 API를 활용한 실시간 키워드 분석 대시보드</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🔧 API 설정")
    
    # 기본값 설정
    default_values = {
        "customer_id": "1606492",
        "api_key": "0100000000dc897c13f61383de5adb2ed865838918b6260db6710f1949dc74795da1b2e53e",
        "secret_key": "AQAAAADciXwT9hOD3lrbLthlg4kYTPfLKERBgDLqGB3VN4N08g=="
    }
    
    # 저장된 설정 불러오기
    config = load_config()
    if config:
        default_values.update(config)
    
    customer_id = st.text_input(
        "네이버 고객 ID",
        value=default_values["customer_id"],
        help="네이버 검색광고 고객 ID를 입력하세요"
    )
    
    api_key = st.text_input(
        "API KEY",
        value=default_values["api_key"],
        type="password",
        help="네이버 검색광고 API Key를 입력하세요"
    )
    
    secret_key = st.text_input(
        "SECRET KEY",
        value=default_values["secret_key"],
        type="password",
        help="네이버 검색광고 Secret Key를 입력하세요"
    )
    
    if st.button("API 설정 저장 및 확인"):
        if customer_id and api_key and secret_key:
            # 설정 저장
            new_config = {
                "customer_id": customer_id,
                "api_key": api_key,
                "secret_key": secret_key
            }
            save_config(new_config)
            st.session_state.api_configured = True
            st.success("✅ API 설정이 저장되었습니다!")
        else:
            st.error("❌ 모든 필드를 입력해주세요.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API 상태 표시
    if st.session_state.api_configured:
        st.markdown("""
        <div class="status-badge status-success">
            🟢 API 설정 완료
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge status-warning">
            ⚠️ API 설정 필요
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 검색 기록
    if st.session_state.keyword_history:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🕒 최근 검색")
        for keyword in st.session_state.keyword_history[-5:]:
            if st.button(f"📌 {keyword}", key=f"history_{keyword}"):
                st.session_state.current_keyword = keyword
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 메인 컨텐츠
# 키워드 검색 섹션
st.markdown('<div class="search-section">', unsafe_allow_html=True)
st.markdown("### 🔍 키워드 검색")

col1, col2 = st.columns([4, 1])

with col1:
    search_keyword = st.text_input(
        "",
        placeholder="분석하고 싶은 키워드를 입력하세요 (예: '스마트폰', '여행', '노트북')",
        key="keyword_input"
    )

with col2:
    search_button = st.button("🔍 분석하기", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# 검색 실행
if search_button and search_keyword:
    # 검색 기록 업데이트
    if search_keyword not in st.session_state.keyword_history:
        st.session_state.keyword_history.append(search_keyword)
    
    # 검색 진행 상태
    with st.spinner(f"'{search_keyword}' 키워드 분석 중..."):
        # 네이버 API 호출
        keyword_list = search_keywords(search_keyword, customer_id, api_key, secret_key)
        
        if keyword_list:
            # 원본 데이터 저장
            st.session_state.raw_keyword_data = keyword_list
            
            # 데이터 처리
            df = process_keyword_data(keyword_list, search_keyword)
            
            # 검색 결과 저장
            st.session_state.search_results = {
                'keyword': search_keyword,
                'df': df,
                'timestamp': datetime.datetime.now()
            }
            
            st.success(f"✅ '{search_keyword}' 키워드 분석이 완료되었습니다!")
        else:
            st.error("❌ 검색 결과가 없습니다. API 설정을 확인해주세요.")

# 검색 결과가 있는 경우 대시보드 표시
if st.session_state.search_results:
    data = st.session_state.search_results
    df = data['df']
    keyword = data['keyword']
    
    # 주요 지표 카드
    st.markdown("### 📊 주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    # 첫 번째 행의 데이터 가져오기 (메인 키워드)
    main_keyword_row = df[df['메인키워드'] == True].iloc[0] if any(df['메인키워드']) else df.iloc[0]
    total_keywords = len(df)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">월간 검색량</div>
            <div class="metric-value">{int(main_keyword_row['총 검색량']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PC 검색량</div>
            <div class="metric-value">{int(main_keyword_row['PC']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">모바일 검색량</div>
            <div class="metric-value">{int(main_keyword_row['MOBILE']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">연관 키워드</div>
            <div class="metric-value">{total_keywords}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 차트와 키워드 리스트
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📈 키워드 검색량 비교")
        
        # 상위 15개 키워드만 사용
        top_df = df.head(15).copy()
        
        # Plotly 그래프
        fig = px.bar(
            top_df, 
            x='키워드', 
            y='총 검색량',
            title=f"'{keyword}' 연관 키워드 검색량",
            color='메인키워드',
            color_discrete_map={True: '#FF5555', False: '#10b981'},
            labels={'총 검색량': '월간 검색량', '키워드': ''}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12),
            title_font_size=16,
            legend_title_text='',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                itemsizing='constant'
            ),
            xaxis=dict(
                tickangle=-45,
                tickmode='array',
                tickvals=list(range(len(top_df))),
                ticktext=top_df['키워드']
            )
        )
        
        # 바 위에 값 표시
        fig.update_traces(
            texttemplate='%{y:,}',
            textposition='outside'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 트렌드 차트 (시뮬레이션)
        if not df.empty and '총 검색량' in df.columns:
            main_volume = int(main_keyword_row['총 검색량'])
            trend_df = create_keyword_trend_data(keyword, main_volume)
            
            # 날짜 필터
            st.markdown("#### 📅 검색량 트렌드 (최근 6개월)")
            
            fig2 = px.line(
                trend_df, 
                x='date', 
                y='volume',
                labels={'volume': '일별 검색량', 'date': '날짜'}
            )
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                showlegend=False
            )
            
            fig2.update_traces(
                line_color='#10b981',
                line_width=3,
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="keyword-list-container">', unsafe_allow_html=True)
        st.markdown("#### 🔑 연관 키워드 목록")
        
        # 연관 키워드 목록 표시
        for i, (_, row) in enumerate(df.head(20).iterrows()):
            keyword_text = row['키워드']
            volume = int(row['총 검색량'])
            competition = row['경쟁정도']
            
            # 메인 키워드 강조
            if row['메인키워드']:
                keyword_text = f"<strong style='color: #FF5555;'>{keyword_text}</strong>"
            
            st.markdown(f"""
            <div class="keyword-item">
                <div>
                    {keyword_text}<br>
                    <small style="color: #64748b;">
                        검색량: {volume:,} | 경쟁: {competition}
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 상세 데이터 테이블
    st.markdown("### 📋 상세 데이터")
    st.dataframe(
        df.drop(columns=['메인키워드']).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )
    
    # 데이터 내보내기
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel 다운로드
        excel_file = BytesIO()
        df.drop(columns=['메인키워드']).to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)
        
        st.download_button(
            label="📊 Excel 다운로드",
            data=excel_file,
            file_name=f"네이버_키워드_분석_{keyword}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col2:
        # CSV 다운로드
        csv_file = BytesIO()
        df.drop(columns=['메인키워드']).to_csv(csv_file, index=False, encoding='utf-8-sig')
        csv_file.seek(0)
        
        st.download_button(
            label="📄 CSV 다운로드",
            data=csv_file,
            file_name=f"네이버_키워드_분석_{keyword}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
    <p>🔍 네이버 키워드 분석 툴 v1.0 | 
    <a href="https://github.com/4tenlab/naver-keyword-tool" target="_blank" style="color: #10b981;">GitHub</a> | 
    Made with ❤️ by 4tenlab</p>
</div>
""", unsafe_allow_html=True)

# 앱 실행 코드
if __name__ == "__main__":
    pass  # Streamlit이 직접 실행 