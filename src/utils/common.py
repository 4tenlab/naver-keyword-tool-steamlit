"""
공통 유틸리티 모듈

애플리케이션 전반에서 사용되는 공통 함수들을 제공합니다.
"""
import platform
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging
from typing import Any, Union
import pandas as pd

# 로깅 설정
logger = logging.getLogger(__name__)

def setup_korean_font():
    """
    한글 폰트 설정
    운영체제별로 적절한 한글 폰트를 설정합니다.
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows 환경 한글 폰트 설정
            plt.rcParams['font.family'] = 'Malgun Gothic'
            mpl.rc('font', family='Malgun Gothic')
            logger.info("Windows 한글 폰트 설정 완료: Malgun Gothic")
            
        elif system == "Darwin":
            # macOS 환경 한글 폰트 설정
            plt.rcParams['font.family'] = 'AppleGothic'
            mpl.rc('font', family='AppleGothic')
            logger.info("macOS 한글 폰트 설정 완료: AppleGothic")
            
        else:
            # Linux 등 기타 환경 한글 폰트 설정
            try:
                # 나눔 폰트 등 한글 지원 폰트가 있으면 사용
                plt.rcParams['font.family'] = 'NanumGothic'
                mpl.rc('font', family='NanumGothic')
                logger.info("Linux 한글 폰트 설정 완료: NanumGothic")
            except:
                # 폰트 설정이 불가능하면 경고만 출력
                logger.warning("한글 폰트를 설정할 수 없습니다. 그래프에서 한글이 깨질 수 있습니다.")
        
        # matplotlib에서 음수 표시 문제 해결
        mpl.rcParams['axes.unicode_minus'] = False
        
    except Exception as e:
        logger.error(f"한글 폰트 설정 중 오류 발생: {str(e)}")

def safe_convert_to_int(value: Any) -> int:
    """
    값을 안전하게 정수로 변환
    
    Args:
        value (Any): 변환할 값
        
    Returns:
        int: 변환된 정수 값
    """
    if value is None:
        return 0
    
    # 이미 정수인 경우
    if isinstance(value, int):
        return value
    
    # 문자열인 경우
    if isinstance(value, str):
        # '< 10'과 같은 값 처리
        if '<' in value:
            try:
                # 숫자 부분만 추출하여 절반 값으로 반환
                num_part = value.replace('<', '').strip()
                return int(int(num_part) / 2)
            except:
                return 0
        
        # 일반 숫자 문자열인 경우
        try:
            return int(float(value))  # float를 거쳐서 변환 (소수점 문자열 대응)
        except:
            return 0
    
    # float인 경우
    if isinstance(value, float):
        return int(value)
    
    # 그 외 케이스
    try:
        return int(value)
    except:
        return 0

def safe_convert_to_float(value: Any) -> float:
    """
    값을 안전하게 실수로 변환
    
    Args:
        value (Any): 변환할 값
        
    Returns:
        float: 변환된 실수 값
    """
    if value is None:
        return 0.0
    
    # 이미 실수인 경우
    if isinstance(value, (int, float)):
        return float(value)
    
    # 문자열인 경우
    if isinstance(value, str):
        # '< 10'과 같은 값 처리
        if '<' in value:
            try:
                num_part = value.replace('<', '').strip()
                return float(num_part) / 2
            except:
                return 0.0
        
        try:
            return float(value)
        except:
            return 0.0
    
    # 그 외 케이스
    try:
        return float(value)
    except:
        return 0.0

def format_number(value: Union[int, float], decimal_places: int = 0) -> str:
    """
    숫자를 읽기 쉬운 형태로 포맷팅
    
    Args:
        value (Union[int, float]): 포맷팅할 숫자
        decimal_places (int): 소수점 자릿수
        
    Returns:
        str: 포맷팅된 숫자 문자열
    """
    try:
        if decimal_places > 0:
            return f"{value:,.{decimal_places}f}"
        else:
            return f"{int(value):,}"
    except:
        return str(value)

def calculate_percentage(part: Union[int, float], total: Union[int, float], decimal_places: int = 1) -> float:
    """
    백분율 계산
    
    Args:
        part (Union[int, float]): 부분 값
        total (Union[int, float]): 전체 값
        decimal_places (int): 소수점 자릿수
        
    Returns:
        float: 백분율
    """
    if total == 0:
        return 0.0
    
    try:
        percentage = (part / total) * 100
        return round(percentage, decimal_places)
    except:
        return 0.0

def validate_keyword(keyword: str) -> bool:
    """
    키워드 유효성 검사
    
    Args:
        keyword (str): 검사할 키워드
        
    Returns:
        bool: 유효성 검사 결과
    """
    if not keyword or not isinstance(keyword, str):
        return False
    
    # 공백 제거 후 길이 확인
    keyword = keyword.strip()
    if len(keyword) == 0:
        return False
    
    # 너무 긴 키워드 제한
    if len(keyword) > 100:
        return False
    
    return True

def truncate_text(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """
    텍스트를 지정된 길이로 자르기
    
    Args:
        text (str): 자를 텍스트
        max_length (int): 최대 길이
        suffix (str): 줄임표시
        
    Returns:
        str: 잘린 텍스트
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def get_competition_color(competition: str) -> str:
    """
    경쟁정도에 따른 색상 반환
    
    Args:
        competition (str): 경쟁정도 ('높음', '중간', '낮음')
        
    Returns:
        str: 색상 코드
    """
    color_map = {
        '높음': '#ff4444',  # 빨강
        '중간': '#ffaa00',  # 주황
        '낮음': '#44aa44'   # 초록
    }
    
    return color_map.get(competition, '#888888')  # 기본 회색

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    데이터프레임 정리
    
    Args:
        df (pd.DataFrame): 정리할 데이터프레임
        
    Returns:
        pd.DataFrame: 정리된 데이터프레임
    """
    if df.empty:
        return df
    
    # 복사본 생성
    cleaned_df = df.copy()
    
    # 빈 문자열을 NaN으로 변환
    cleaned_df = cleaned_df.replace('', pd.NA)
    
    # 중복 행 제거
    cleaned_df = cleaned_df.drop_duplicates()
    
    # 인덱스 재설정
    cleaned_df = cleaned_df.reset_index(drop=True)
    
    return cleaned_df

def create_excel_buffer() -> tuple:
    """
    엑셀 파일 생성을 위한 버퍼 생성
    
    Returns:
        tuple: (BytesIO 객체, 파일명)
    """
    from io import BytesIO
    from datetime import datetime
    
    buffer = BytesIO()
    filename = f"naver_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return buffer, filename 