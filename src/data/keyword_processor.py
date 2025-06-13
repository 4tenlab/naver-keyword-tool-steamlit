"""
키워드 데이터 처리 모듈

네이버 키워드 API로부터 받은 데이터를 처리하고 분석하는 기능을 제공합니다.
데이터 정제, 변환, 그리고 간단한 분석 기능을 포함합니다.
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
from io import BytesIO
from datetime import datetime

# 로깅 설정
logger = logging.getLogger(__name__)

class KeywordProcessor:
    """키워드 데이터 처리 클래스"""
    
    def __init__(self):
        """데이터 처리 클래스 초기화"""
        self.data = None
        self.main_keyword = None
    
    def process_keyword_data(self, keyword_list: List[Dict[str, Any]], main_keyword: str) -> pd.DataFrame:
        """
        키워드 목록 데이터를 처리하여 DataFrame으로 변환
        
        Args:
            keyword_list (List[Dict]): 네이버 API로부터 받은 키워드 목록
            main_keyword (str): 검색에 사용된 메인 키워드
            
        Returns:
            pd.DataFrame: 처리된 키워드 데이터
        """
        if not keyword_list:
            logger.warning("처리할 키워드 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 메인 키워드 저장
        self.main_keyword = main_keyword.lower()
        
        # 데이터 처리
        data = []
        try:
            for item in keyword_list:
                # 안전하게 값 추출 및 정수 변환
                pc_count = self._safe_convert_to_int(item.get('monthlyPcQcCnt', 0))
                mobile_count = self._safe_convert_to_int(item.get('monthlyMobileQcCnt', 0))
                rel_keyword = item.get('relKeyword', '')
                
                # 검색어 경쟁정도
                competition = item.get('compIdx', '-')
                
                # 월평균 노출 광고수
                avg_depth = self._safe_convert_to_int(item.get('plAvgDepth', 0))
                
                # 검색어 클릭률 (있는 경우에만)
                ctr = item.get('monthlyAveCtr', '-')
                
                # 클릭수 (있는 경우에만)
                clicks = self._safe_convert_to_int(item.get('monthlyAvePcClkCnt', 0))
                
                # 총 검색량 계산
                total_search = pc_count + mobile_count
                
                # 메인 키워드 여부
                is_main = rel_keyword.lower() == self.main_keyword
                
                # 데이터 행 생성
                row = {
                    '키워드': rel_keyword,
                    '총 검색량': total_search,
                    'PC': pc_count,
                    'MOBILE': mobile_count,
                    '경쟁정도': competition,
                    '월평균 노출 광고수': avg_depth,
                    '클릭률': ctr if ctr != '-' else '-',
                    '클릭수': clicks,
                    'PC 비율': round(pc_count / total_search * 100, 1) if total_search > 0 else 0,
                    '모바일 비율': round(mobile_count / total_search * 100, 1) if total_search > 0 else 0,
                    '메인키워드': is_main
                }
                data.append(row)
                
            # DataFrame 생성
            df = pd.DataFrame(data)
            
            # 검색량 기준 내림차순 정렬
            if not df.empty and '총 검색량' in df.columns:
                df = df.sort_values(by='총 검색량', ascending=False)
            
            # 처리된 데이터 저장
            self.data = df.copy()
            
            return df
            
        except Exception as e:
            logger.error(f"데이터 처리 중 오류 발생: {str(e)}")
            raise ValueError(f"키워드 데이터 처리 중 오류가 발생했습니다: {str(e)}")
    
    def _safe_convert_to_int(self, value: Any) -> int:
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
                return int(value)
            except:
                return 0
        
        # 그 외 케이스
        try:
            return int(value)
        except:
            return 0
    
    def get_top_keywords(self, n: int = 15) -> pd.DataFrame:
        """
        상위 n개 키워드 추출
        
        Args:
            n (int): 추출할 키워드 수 (기본: 15)
            
        Returns:
            pd.DataFrame: 상위 n개 키워드
        """
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        
        return self.data.head(n).copy()
    
    def get_keyword_stats(self) -> Dict[str, Any]:
        """
        키워드 데이터 기본 통계 계산
        
        Returns:
            Dict: 통계 정보
        """
        if self.data is None or self.data.empty:
            return {}
        
        stats = {
            '총 키워드 수': len(self.data),
            '총 검색량 합계': int(self.data['총 검색량'].sum()),
            '평균 검색량': round(self.data['총 검색량'].mean(), 1),
            '중앙값 검색량': int(self.data['총 검색량'].median()),
            '최대 검색량': int(self.data['총 검색량'].max()),
            '최소 검색량': int(self.data['총 검색량'].min()),
            'PC 검색 비율': round(self.data['PC'].sum() / (self.data['PC'].sum() + self.data['MOBILE'].sum()) * 100, 1),
            '모바일 검색 비율': round(self.data['MOBILE'].sum() / (self.data['PC'].sum() + self.data['MOBILE'].sum()) * 100, 1),
        }
        
        # 경쟁정도 분포 계산
        if '경쟁정도' in self.data.columns:
            competition_counts = self.data['경쟁정도'].value_counts()
            for comp in ['높음', '중간', '낮음']:
                if comp in competition_counts:
                    stats[f'경쟁정도 {comp}'] = int(competition_counts[comp])
        
        return stats
    
    def export_to_excel(self, filename: Optional[str] = None) -> Tuple[BytesIO, str]:
        """
        키워드 데이터를 엑셀 파일로 내보내기
        
        Args:
            filename (str, optional): 파일명. 지정하지 않으면 자동 생성
            
        Returns:
            Tuple[BytesIO, str]: 엑셀 파일 객체와 파일명
        """
        if self.data is None or self.data.empty:
            raise ValueError("내보낼 데이터가 없습니다.")
        
        # 파일명 생성
        if filename is None:
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            keyword_part = self.main_keyword.replace(' ', '_') if self.main_keyword else 'keywords'
            filename = f"네이버_키워드_분석_{keyword_part}_{now}.xlsx"
        
        # 내보내기용 데이터 준비 (메인키워드 열 제외)
        export_df = self.data.drop(columns=['메인키워드']) if '메인키워드' in self.data.columns else self.data.copy()
        
        # 엑셀 파일 생성
        excel_file = BytesIO()
        
        try:
            # 엑셀 파일로 저장
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='키워드 분석', index=False)
                
                # 통계 시트 추가
                stats = self.get_keyword_stats()
                if stats:
                    stats_df = pd.DataFrame(list(stats.items()), columns=['지표', '값'])
                    stats_df.to_excel(writer, sheet_name='통계 요약', index=False)
            
            # 파일 포인터 처음으로 이동
            excel_file.seek(0)
            
            return excel_file, filename
            
        except Exception as e:
            logger.error(f"엑셀 파일 생성 중 오류 발생: {str(e)}")
            raise ValueError(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")
    
    def get_device_distribution(self) -> Dict[str, float]:
        """
        PC와 모바일 검색 비율 계산
        
        Returns:
            Dict: PC와 모바일 검색 비율
        """
        if self.data is None or self.data.empty:
            return {'PC': 0, 'MOBILE': 0}
        
        pc_sum = self.data['PC'].sum()
        mobile_sum = self.data['MOBILE'].sum()
        total = pc_sum + mobile_sum
        
        if total == 0:
            return {'PC': 0, 'MOBILE': 0}
        
        return {
            'PC': round(pc_sum / total * 100, 1),
            'MOBILE': round(mobile_sum / total * 100, 1)
        }
    
    def filter_keywords(self, min_search: int = 0, competition: Optional[List[str]] = None) -> pd.DataFrame:
        """
        키워드 필터링
        
        Args:
            min_search (int): 최소 검색량
            competition (List[str], optional): 포함할 경쟁정도 목록 (예: ['낮음', '중간'])
            
        Returns:
            pd.DataFrame: 필터링된 키워드 데이터
        """
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        
        # 필터링 조건 구성
        conditions = []
        
        # 최소 검색량 조건
        if min_search > 0:
            conditions.append(self.data['총 검색량'] >= min_search)
        
        # 경쟁정도 조건
        if competition and '경쟁정도' in self.data.columns:
            conditions.append(self.data['경쟁정도'].isin(competition))
        
        # 조건 적용
        if conditions:
            # 모든 조건을 AND로 결합
            mask = conditions[0]
            for condition in conditions[1:]:
                mask = mask & condition
            
            return self.data[mask].copy()
        
        return self.data.copy() 