"""
설정 관리 모듈

애플리케이션의 설정을 관리하는 모듈입니다.
환경변수, JSON 파일을 통한 설정 관리 기능을 제공합니다.
"""
import json
import os
import logging
import base64
import re
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
    
    def _simple_encrypt(self, text: str) -> str:
        """
        간단한 Base64 인코딩 (기본적인 보안)
        실제 운영에서는 더 강력한 암호화 사용 권장
        
        Args:
            text (str): 암호화할 텍스트
            
        Returns:
            str: 인코딩된 텍스트
        """
        try:
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        except Exception:
            return text
    
    def _simple_decrypt(self, encoded_text: str) -> str:
        """
        간단한 Base64 디코딩
        
        Args:
            encoded_text (str): 디코딩할 텍스트
            
        Returns:
            str: 디코딩된 텍스트
        """
        try:
            return base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
        except Exception:
            return encoded_text
    
    def _validate_api_key_format(self, api_key: str, key_type: str) -> bool:
        """
        API 키 형식 검증
        
        Args:
            api_key (str): 검증할 API 키
            key_type (str): 키 타입 (customer_id, api_key, secret_key)
            
        Returns:
            bool: 유효성 검사 결과
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # 기본 보안 검사
        if len(api_key.strip()) < 8:
            return False
        
        # 특수문자나 스크립트 공격 방지
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, api_key, re.IGNORECASE):
                logger.warning(f"위험한 패턴이 감지되었습니다: {key_type}")
                return False
        
        return True
    
    def _sanitize_input(self, text: str) -> str:
        """
        입력값 정제
        
        Args:
            text (str): 정제할 텍스트
            
        Returns:
            str: 정제된 텍스트
        """
        if not text:
            return ""
        
        # 기본적인 HTML/스크립트 태그 제거
        text = re.sub(r'<[^>]*>', '', text)
        # 특수문자 이스케이프
        text = text.strip()
        
        return text

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
                    file_data = json.load(f)
                    
                # 암호화된 데이터 복호화
                self.config_data = {}
                for key, value in file_data.items():
                    if key in ['customer_id', 'api_key', 'secret_key'] and value:
                        self.config_data[key] = self._simple_decrypt(value)
                    else:
                        self.config_data[key] = value
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
                    # 환경변수도 검증
                    if self._validate_api_key_format(value, key):
                        self.config_data[key] = self._sanitize_input(value)
                        logger.info(f"환경변수에서 {key} 설정을 로드했습니다.")
                    else:
                        logger.warning(f"환경변수 {key}의 형식이 올바르지 않습니다.")
            
            return self.config_data
            
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            self.config_data = {}
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        설정 파일 저장 (API 키는 암호화하여 저장)
        
        Args:
            config (Dict): 저장할 설정 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            self.config_data.update(config)
            
            # 저장용 데이터 준비 (API 키는 암호화)
            save_data = {}
            for key, value in self.config_data.items():
                if key in ['customer_id', 'api_key', 'secret_key'] and value:
                    save_data[key] = self._simple_encrypt(value)
                else:
                    save_data[key] = value
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"설정이 {self.config_file}에 암호화되어 저장되었습니다.")
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
        네이버 API 인증 정보 설정 (입력 검증 포함)
        
        Args:
            customer_id (str): 고객 ID
            api_key (str): API 키
            secret_key (str): 시크릿 키
            
        Returns:
            bool: 설정 성공 여부
        """
        # 입력 검증
        if not self._validate_api_key_format(customer_id, 'customer_id'):
            logger.error("고객 ID 형식이 올바르지 않습니다.")
            return False
        
        if not self._validate_api_key_format(api_key, 'api_key'):
            logger.error("API 키 형식이 올바르지 않습니다.")
            return False
        
        if not self._validate_api_key_format(secret_key, 'secret_key'):
            logger.error("시크릿 키 형식이 올바르지 않습니다.")
            return False
        
        # 입력값 정제
        credentials = {
            'customer_id': self._sanitize_input(customer_id),
            'api_key': self._sanitize_input(api_key),
            'secret_key': self._sanitize_input(secret_key)
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
            value = credentials.get(field)
            if not value:
                logger.warning(f"필수 인증 정보 '{field}'가 누락되었습니다.")
                return False
            
            if not self._validate_api_key_format(value, field):
                logger.warning(f"인증 정보 '{field}'의 형식이 올바르지 않습니다.")
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
        # 입력값 정제
        if isinstance(value, str):
            value = self._sanitize_input(value)
        
        return self.save_config({key: value})
