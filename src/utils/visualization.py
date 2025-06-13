"""
키워드 시각화 모듈

네이버 키워드 데이터의 다양한 시각화 기능을 제공합니다.
Matplotlib, Plotly를 활용한 차트 및 그래프 생성 기능을 포함합니다.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Optional, Dict, List, Any, Tuple, Union

# 로깅 설정
logger = logging.getLogger(__name__)

class KeywordVisualizer:
    """키워드 데이터 시각화 클래스"""
    
    def __init__(self):
        """시각화 클래스 초기화"""
        # 기본 색상 설정
        self.main_color = '#FF5555'  # 메인 키워드 색상 (빨간색)
        self.secondary_color = '#a6dcef'  # 일반 키워드 색상 (하늘색)
        self.chart_colors = ['#a6dcef', '#88d8b0', '#ffd3b6', '#ffaaa5', '#d9b3ff']
    
    def draw_search_volume_chart(self, df: pd.DataFrame, main_keyword: str) -> go.Figure:
        """
        키워드 검색량 막대 차트 생성 (Plotly)
        
        Args:
            df (pd.DataFrame): 키워드 데이터
            main_keyword (str): 메인 키워드
            
        Returns:
            go.Figure: Plotly 그래프 객체
        """
        if df.empty:
            return self._create_empty_chart("데이터가 없습니다.")
        
        # 상위 15개 키워드만 사용
        top_df = df.head(15).copy()
        
        # 메인 키워드 확인 (대소문자 구분 없이)
        main_keyword = main_keyword.lower()
        
        # 색상 배열 생성
        colors = []
        for keyword in top_df['키워드']:
            if keyword.lower() == main_keyword:
                colors.append(self.main_color)
            else:
                colors.append(self.secondary_color)
        
        # 그래프 생성
        fig = go.Figure()
        
        # 막대 추가
        fig.add_trace(go.Bar(
            x=top_df['키워드'],
            y=top_df['총 검색량'],
            marker_color=colors,
            text=top_df['총 검색량'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>검색량: %{y}<extra></extra>'
        ))
        
        # 레이아웃 설정
        fig.update_layout(
            title='상위 키워드별 총 검색량',
            xaxis_title='키워드',
            yaxis_title='검색량',
            xaxis=dict(
                tickangle=45,
                tickmode='array',
                tickvals=list(range(len(top_df))),
                ticktext=top_df['키워드'].tolist()
            ),
            plot_bgcolor='white',
            yaxis=dict(gridcolor='lightgray'),
            hoverlabel=dict(bgcolor='white', font_size=14),
            margin=dict(t=80, b=120, l=60, r=40),
            height=500
        )
        
        return fig
    
    def draw_device_distribution_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        PC/모바일 분포 파이 차트 생성 (Plotly)
        
        Args:
            df (pd.DataFrame): 키워드 데이터
            
        Returns:
            go.Figure: Plotly 그래프 객체
        """
        if df.empty:
            return self._create_empty_chart("데이터가 없습니다.")
        
        # PC와 모바일 검색량 합계
        pc_sum = df['PC'].sum()
        mobile_sum = df['MOBILE'].sum()
        total = pc_sum + mobile_sum
        
        if total == 0:
            return self._create_empty_chart("검색량이 없습니다.")
        
        # 비율 계산
        pc_ratio = pc_sum / total
        mobile_ratio = mobile_sum / total
        
        # 그래프 데이터
        labels = ['PC', 'MOBILE']
        values = [pc_ratio * 100, mobile_ratio * 100]
        
        # 그래프 생성
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=['#4e79a7', '#f28e2c']),
            textinfo='label+percent',
            texttemplate='%{label}: %{percent:.1f}%',
            hovertemplate='<b>%{label}</b><br>비율: %{percent:.1f}%<extra></extra>'
        )])
        
        # 레이아웃 설정
        fig.update_layout(
            title='PC vs 모바일 검색 비율',
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
            margin=dict(t=80, b=80, l=40, r=40),
            height=400
        )
        
        return fig
    
    def draw_competition_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        경쟁정도 분포 차트 생성 (Plotly)
        
        Args:
            df (pd.DataFrame): 키워드 데이터
            
        Returns:
            go.Figure: Plotly 그래프 객체
        """
        if df.empty or '경쟁정도' not in df.columns:
            return self._create_empty_chart("경쟁정도 데이터가 없습니다.")
        
        # 경쟁정도 분포 계산
        competition_counts = df['경쟁정도'].value_counts().reset_index()
        competition_counts.columns = ['경쟁정도', '키워드 수']
        
        # 경쟁정도 순서 설정
        order = {'높음': 3, '중간': 2, '낮음': 1, '-': 0}
        competition_counts['순서'] = competition_counts['경쟁정도'].map(order)
        competition_counts = competition_counts.sort_values('순서', ascending=False)
        
        # 색상 매핑
        color_map = {'높음': '#ff7e7e', '중간': '#ffcc66', '낮음': '#88d8b0', '-': '#cccccc'}
        colors = [color_map.get(comp, '#cccccc') for comp in competition_counts['경쟁정도']]
        
        # 그래프 생성
        fig = go.Figure()
        
        # 막대 추가
        fig.add_trace(go.Bar(
            x=competition_counts['경쟁정도'],
            y=competition_counts['키워드 수'],
            marker_color=colors,
            text=competition_counts['키워드 수'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>키워드 수: %{y}<extra></extra>'
        ))
        
        # 레이아웃 설정
        fig.update_layout(
            title='경쟁정도별 키워드 분포',
            xaxis_title='경쟁정도',
            yaxis_title='키워드 수',
            plot_bgcolor='white',
            yaxis=dict(gridcolor='lightgray'),
            hoverlabel=dict(bgcolor='white', font_size=14),
            margin=dict(t=80, b=80, l=60, r=40),
            height=400
        )
        
        return fig
    
    def draw_trend_simulation(self, df: pd.DataFrame, main_keyword: str, days: int = 30) -> go.Figure:
        """
        트렌드 시뮬레이션 차트 생성 (시간에 따른 가상의 검색량 변화)
        
        Args:
            df (pd.DataFrame): 키워드 데이터
            main_keyword (str): 메인 키워드
            days (int): 시뮬레이션 일수
            
        Returns:
            go.Figure: Plotly 그래프 객체
        """
        if df.empty:
            return self._create_empty_chart("데이터가 없습니다.")
        
        # 상위 5개 키워드 선택
        top_df = df.head(5).copy()
        
        # 키워드 목록
        keywords = top_df['키워드'].tolist()
        
        # 시간축 생성
        dates = [f'Day {i+1}' for i in range(days)]
        
        # 시뮬레이션 데이터 생성
        np.random.seed(42)  # 재현성을 위한 시드 설정
        
        # 그래프 생성
        fig = go.Figure()
        
        for i, keyword in enumerate(keywords):
            # 기준 검색량 (실제 월간 검색량을 30으로 나눈 값)
            base = top_df.iloc[i]['총 검색량'] / 30
            
            # 랜덤 변동 생성 (±20%)
            variations = np.random.uniform(0.8, 1.2, days)
            
            # 일별 검색량 계산
            daily_volume = [max(int(base * var), 0) for var in variations]
            
            # 추세선 추가
            fig.add_trace(go.Scatter(
                x=dates,
                y=daily_volume,
                mode='lines+markers',
                name=keyword,
                line=dict(
                    color=self.main_color if keyword.lower() == main_keyword.lower() else self.chart_colors[i % len(self.chart_colors)],
                    width=3 if keyword.lower() == main_keyword.lower() else 2
                ),
                marker=dict(
                    size=8 if keyword.lower() == main_keyword.lower() else 6
                ),
                hovertemplate='<b>%{x}</b><br>%{y:,d} 검색<extra></extra>'
            ))
        
        # 레이아웃 설정
        fig.update_layout(
            title='일별 키워드 검색량 추세 (시뮬레이션)',
            xaxis_title='날짜',
            yaxis_title='일별 검색량',
            plot_bgcolor='white',
            yaxis=dict(gridcolor='lightgray'),
            hoverlabel=dict(bgcolor='white', font_size=14),
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            margin=dict(t=80, b=100, l=60, r=40),
            height=400
        )
        
        return fig
    
    def _create_empty_chart(self, message: str = "데이터가 없습니다.") -> go.Figure:
        """
        데이터가 없을 때 표시할 빈 차트 생성
        
        Args:
            message (str): 표시할 메시지
            
        Returns:
            go.Figure: 빈 차트 객체
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=300
        )
        
        return fig
    
    def create_matplotlib_chart(self, df: pd.DataFrame, main_keyword: str) -> plt.Figure:
        """
        Matplotlib을 사용한 키워드 검색량 차트 생성 (PySide6용)
        
        Args:
            df (pd.DataFrame): 키워드 데이터
            main_keyword (str): 메인 키워드
            
        Returns:
            plt.Figure: Matplotlib 그림 객체
        """
        if df.empty:
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
            ax.text(0.5, 0.5, "데이터가 없습니다.", ha='center', va='center', fontsize=14)
            ax.axis('off')
            return fig
        
        # 상위 15개 키워드만 사용
        top_df = df.head(15).copy()
        
        # 메인 키워드 확인 (대소문자 구분 없이)
        main_keyword = main_keyword.lower()
        
        # 그래프 생성
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        
        # 데이터 준비
        keywords = top_df['키워드'].tolist()
        values = top_df['총 검색량'].tolist()
        
        # 막대 색상 설정
        bar_colors = []
        for keyword in keywords:
            if keyword.lower() == main_keyword:
                bar_colors.append(self.main_color)  # 메인 키워드는 빨간색
            else:
                bar_colors.append(self.secondary_color)  # 일반 키워드는 하늘색
        
        # 막대 그래프 생성
        bars = ax.bar(range(len(keywords)), values, color=bar_colors, width=0.6)
        
        # Y축 라벨에 천 단위 콤마 추가
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        # X축 레이블 설정
        plt.xticks(range(len(keywords)), keywords, rotation=45, ha='right', fontsize=10)
        
        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    '{:,}'.format(int(height)),
                    ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('총 검색량', fontsize=12)
        ax.set_title('상위 키워드별 총 검색량', fontsize=14, pad=15)
        
        # 그래프 레이아웃 여백 조정
        fig.tight_layout()
        
        return fig
