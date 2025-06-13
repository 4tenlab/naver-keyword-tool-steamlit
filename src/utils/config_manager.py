"""
설정 관리 모듈

애플리케이션의 설정을 관리하는 모듈입니다.
환경변수, JSON 파일을 통한 설정 관리 기능을 제공합니다.
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 로깅 설정
logger = logging.getLogger(__name__)

class ConfigManager:
    """설정 관리 클래스"""
    
    def __init__(self, config_file: str = 'config.json'):
        """
        설정 관리자 초기화
        
        Args:
            config_file (str): 설정 파일 경로
        """
        self.config_file = config_file
        self.config_data = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        설정 파일 로드
        환경변수가 있으면 우선적으로 사용
        
        Returns:
            Dict: 설정 데이터
        """
        try:
            # 파일에서 기본 설정 로드
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}
            
            # 환경변수 우선 적용
            env_config = {
                'customer_id': os.getenv('NAVER_CUSTOMER_ID'),
                'api_key': os.getenv('NAVER_API_KEY'),
                'secret_key': os.getenv('NAVER_SECRET_KEY')
            }
            
            # 환경변수가 있는 경우만 업데이트
            for key, value in env_config.items():
                if value:
                    self.config_data[key] = value
                    logger.info(f"환경변수에서 {key} 설정을 로드했습니다.")
            
            return self.config_data
            
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            self.config_data = {}
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        설정 파일 저장
        
        Args:
            config (Dict): 저장할 설정 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            self.config_data.update(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"설정이 {self.config_file}에 저장되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def get_api_credentials(self) -> Dict[str, str]:
        """
        네이버 API 인증 정보 반환
        
        Returns:
            Dict: API 인증 정보
        """
        return {
            'customer_id': self.config_data.get('customer_id', ''),
            'api_key': self.config_data.get('api_key', ''),
            'secret_key': self.config_data.get('secret_key', '')
        }
    
    def set_api_credentials(self, customer_id: str, api_key: str, secret_key: str) -> bool:
        """
        네이버 API 인증 정보 설정
        
        Args:
            customer_id (str): 고객 ID
            api_key (str): API 키
            secret_key (str): 시크릿 키
            
        Returns:
            bool: 설정 성공 여부
        """
        credentials = {
            'customer_id': customer_id,
            'api_key': api_key,
            'secret_key': secret_key
        }
        
        return self.save_config(credentials)
    
    def get_default_api_credentials(self) -> Dict[str, str]:
        """
        기본 API 인증 정보 반환 (테스트용)
        실제 운영에서는 환경변수나 안전한 방법으로 관리해야 함
        
        Returns:
            Dict: 기본 API 인증 정보
        """
        return {
            'customer_id': '',
            'api_key': '',
            'secret_key': ''
        }
    
    def validate_api_credentials(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """
        API 인증 정보 유효성 검사
        
        Args:
            credentials (Dict, optional): 검사할 인증 정보
            
        Returns:
            bool: 유효성 검사 결과
        """
        if credentials is None:
            credentials = self.get_api_credentials()
        
        required_fields = ['customer_id', 'api_key', 'secret_key']
        
        for field in required_fields:
            if not credentials.get(field):
                logger.warning(f"필수 인증 정보 '{field}'가 누락되었습니다.")
                return False
        
        return True
    
    def get_app_settings(self) -> Dict[str, Any]:
        """
        앱 일반 설정 반환
        
        Returns:
            Dict: 앱 설정
        """
        return {
            'theme': self.config_data.get('theme', 'light'),
            'language': self.config_data.get('language', 'ko'),
            'max_keywords': self.config_data.get('max_keywords', 100),
            'cache_enabled': self.config_data.get('cache_enabled', True),
            'auto_save': self.config_data.get('auto_save', True)
        }
    
    def update_app_settings(self, settings: Dict[str, Any]) -> bool:
        """
        앱 일반 설정 업데이트
        
        Args:
            settings (Dict): 업데이트할 설정
            
        Returns:
            bool: 업데이트 성공 여부
        """
        return self.save_config(settings)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정 값 가져오기
        
        Args:
            key (str): 설정 키
            default (Any): 기본값
            
        Returns:
            Any: 설정 값
        """
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        설정 값 설정
        
        Args:
            key (str): 설정 키
            value (Any): 설정 값
            
        Returns:
            bool: 설정 성공 여부
        """
        return self.save_config({key: value})
