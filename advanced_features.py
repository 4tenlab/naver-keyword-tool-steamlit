"""
네이버 키워드 분석 도구 - 고급 기능 모듈
Streamlit 앱에서 사용할 수 있는 추가 분석 기능을 제공합니다.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def calculate_keyword_metrics(df):
    """키워드 데이터에서 중요 메트릭 계산"""
    if df.empty:
        return {}
    
    # 총 검색량 합계 및 평균
    total_search = df['총 검색량'].sum()
    avg_search = df['총 검색량'].mean()
    
    # PC/모바일 비율
    pc_total = df['PC'].sum()
    mobile_total = df['MOBILE'].sum()
    pc_ratio = pc_total / (pc_total + mobile_total) if (pc_total + mobile_total) > 0 else 0
    mobile_ratio = 1 - pc_ratio
    
    # 경쟁정도 분포
    competition_counts = df['경쟁정도'].value_counts().to_dict()
    
    # 상위 10% 키워드의 검색량 점유율
    df_sorted = df.sort_values('총 검색량', ascending=False)
    top_10_percent = int(len(df) * 0.1) or 1  # 최소 1개
    top_10_volume = df_sorted.iloc[:top_10_percent]['총 검색량'].sum()
    top_10_share = top_10_volume / total_search if total_search > 0 else 0
    
    return {
        'total_search': total_search,
        'avg_search': avg_search,
        'pc_ratio': pc_ratio,
        'mobile_ratio': mobile_ratio,
        'competition_dist': competition_counts,
        'top_10_share': top_10_share
    }

def create_device_distribution_chart(df):
    """PC와 모바일 검색량 분포 차트 생성"""
    if df.empty:
        return None
    
    # 상위 10개 키워드만 사용
    top_df = df.head(10).copy()
    
    # 막대 그래프 데이터 준비
    pc_values = top_df['PC'].values
    mobile_values = top_df['MOBILE'].values
    keywords = top_df['키워드'].values
    
    # Plotly Figure 생성
    fig = go.Figure()
    
    # PC 검색량 추가
    fig.add_trace(go.Bar(
        y=keywords,
        x=pc_values,
        name='PC',
        orientation='h',
        marker=dict(color='rgba(58, 71, 80, 0.6)'),
        hovertemplate='PC 검색량: %{x:,.0f}<extra></extra>'
    ))
    
    # 모바일 검색량 추가
    fig.add_trace(go.Bar(
        y=keywords,
        x=mobile_values,
        name='Mobile',
        orientation='h',
        marker=dict(color='rgba(16, 185, 129, 0.6)'),
        hovertemplate='모바일 검색량: %{x:,.0f}<extra></extra>'
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        title='PC vs 모바일 검색량 분포',
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(title='검색량'),
        yaxis=dict(title='')
    )
    
    return fig

def create_competition_chart(df):
    """경쟁정도 분포 차트 생성"""
    if df.empty:
        return None
    
    # 경쟁정도별 키워드 수 계산
    competition_counts = df['경쟁정도'].value_counts().reset_index()
    competition_counts.columns = ['경쟁정도', '키워드 수']
    
    # 차트 생성
    fig = px.pie(
        competition_counts, 
        values='키워드 수', 
        names='경쟁정도',
        title='경쟁정도별 키워드 분포',
        color_discrete_sequence=px.colors.sequential.Viridis,
        hole=0.4
    )
    
    # 레이아웃 설정
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # 툴팁 커스터마이징
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>키워드 수: %{value}<br>비율: %{percent}<extra></extra>'
    )
    
    return fig

def perform_keyword_clustering(df, n_clusters=3):
    """키워드 데이터 클러스터링 (검색량과 경쟁정도 기준)"""
    if df.empty or len(df) < n_clusters:
        return df
    
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # 클러스터링에 사용할 특성 선택
        # 경쟁정도가 문자열인 경우 숫자로 변환
        numeric_df = df.copy()
        competition_map = {'낮음': 1, '중간': 2, '높음': 3}
        
        if '경쟁정도' in numeric_df.columns:
            if numeric_df['경쟁정도'].dtype == 'object':
                numeric_df['경쟁정도_numeric'] = numeric_df['경쟁정도'].map(competition_map).fillna(0)
            else:
                numeric_df['경쟁정도_numeric'] = numeric_df['경쟁정도']
        else:
            numeric_df['경쟁정도_numeric'] = 0
        
        # 클러스터링을 위한 데이터 추출
        features = numeric_df[['총 검색량', '경쟁정도_numeric']].values
        
        # 데이터 스케일링
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # K-means 클러스터링 적용
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        numeric_df['클러스터'] = kmeans.fit_predict(scaled_features)
        
        # 원본 데이터프레임에 클러스터 정보 추가
        result_df = df.copy()
        result_df['클러스터'] = numeric_df['클러스터']
        
        return result_df
    
    except ImportError:
        # scikit-learn이 설치되지 않은 경우
        print("scikit-learn 패키지가 필요합니다. 'pip install scikit-learn' 명령으로 설치하세요.")
        return df
    except Exception as e:
        print(f"클러스터링 중 오류 발생: {str(e)}")
        return df

def create_cluster_chart(clustered_df):
    """클러스터링 결과 시각화"""
    if clustered_df.empty or '클러스터' not in clustered_df.columns:
        return None
    
    # 경쟁정도를 숫자로 변환
    competition_map = {'낮음': 1, '중간': 2, '높음': 3}
    plot_df = clustered_df.copy()
    
    if '경쟁정도' in plot_df.columns and plot_df['경쟁정도'].dtype == 'object':
        plot_df['경쟁정도_numeric'] = plot_df['경쟁정도'].map(competition_map).fillna(1)
    else:
        plot_df['경쟁정도_numeric'] = 1
    
    # 클러스터별 색상 지정
    cluster_colors = {
        0: '#1f77b4',  # 파란색
        1: '#ff7f0e',  # 주황색
        2: '#2ca02c',  # 녹색
        3: '#d62728',  # 빨간색
        4: '#9467bd'   # 보라색
    }
    
    # 클러스터별 색상 매핑
    plot_df['color'] = plot_df['클러스터'].map(lambda x: cluster_colors.get(x, '#7f7f7f'))
    
    # 산점도 생성
    fig = px.scatter(
        plot_df,
        x='총 검색량',
        y='경쟁정도_numeric',
        color='클러스터',
        hover_name='키워드',
        size='총 검색량',
        size_max=30,
        title='키워드 클러스터링: 검색량 vs 경쟁도',
        labels={
            '총 검색량': '총 검색량',
            '경쟁정도_numeric': '경쟁정도',
            '클러스터': '클러스터'
        },
        color_discrete_map=cluster_colors
    )
    
    # Y축 눈금 레이블 변경
    yticks = {1: '낮음', 2: '중간', 3: '높음'}
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=list(yticks.keys()),
            ticktext=list(yticks.values())
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def suggest_keywords(df, metric='총 검색량', competition_filter=None, limit=5):
    """최적의 키워드 추천"""
    if df.empty:
        return pd.DataFrame()
    
    # 데이터 복사
    suggest_df = df.copy()
    
    # 경쟁도 필터링 (낮음, 중간, 높음)
    if competition_filter and '경쟁정도' in suggest_df.columns:
        suggest_df = suggest_df[suggest_df['경쟁정도'] == competition_filter]
    
    # 지정된 메트릭으로 정렬
    if metric in suggest_df.columns:
        suggest_df = suggest_df.sort_values(by=metric, ascending=False)
    
    # 상위 N개 반환
    return suggest_df.head(limit)

def calculate_keyword_difficulty(df):
    """키워드 난이도 계산 (검색량 대비 경쟁도)"""
    if df.empty:
        return df
    
    # 결과 데이터프레임 생성
    result_df = df.copy()
    
    # 경쟁정도 숫자로 변환
    competition_map = {'낮음': 1, '중간': 2, '높음': 3, '-': 1.5}
    
    if '경쟁정도' in result_df.columns:
        # 문자열 경쟁도를 숫자로 변환
        if result_df['경쟁정도'].dtype == 'object':
            result_df['경쟁정도_점수'] = result_df['경쟁정도'].map(competition_map).fillna(1.5)
        else:
            # 이미 숫자인 경우 그대로 사용
            result_df['경쟁정도_점수'] = result_df['경쟁정도']
    else:
        # 경쟁정도 열이 없으면 중간값 사용
        result_df['경쟁정도_점수'] = 1.5
    
    # 검색량에 로그 스케일 적용 (검색량이 0인 경우 방지)
    result_df['로그_검색량'] = np.log1p(result_df['총 검색량'])
    
    # 검색량과 경쟁도 기준으로 난이도 계산
    # 낮은 경쟁도와 높은 검색량이 좋은 점수를 받음
    max_log_volume = result_df['로그_검색량'].max() if not result_df.empty else 1
    result_df['검색량_점수'] = result_df['로그_검색량'] / max_log_volume if max_log_volume > 0 else 0
    
    # 난이도 점수 계산: (검색량 점수 * 0.7) - (경쟁정도 점수 * 0.3)
    # 높은 점수가 더 좋은 키워드를 의미
    result_df['키워드_점수'] = (result_df['검색량_점수'] * 0.7) - (result_df['경쟁정도_점수'] / 3 * 0.3)
    
    # 점수를 0~100 범위로 정규화
    min_score = result_df['키워드_점수'].min()
    max_score = result_df['키워드_점수'].max()
    score_range = max_score - min_score
    
    if score_range > 0:
        result_df['최종_점수'] = ((result_df['키워드_점수'] - min_score) / score_range * 100).round().astype(int)
    else:
        result_df['최종_점수'] = 50  # 모든 점수가 동일한 경우
    
    return result_df 