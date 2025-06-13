"""
네이버 검색광고 API 통신 모듈

네이버 검색광고 API와의 통신을 담당하는 모듈입니다.
키워드 도구에 필요한 API 호출 및 응답 처리 기능을 제공합니다.
"""
import requests
import hmac
import hashlib
import base64
import time
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class NaverKeywordAPI:
    """네이버 검색광고 API 클래스"""
    
    BASE_URL = 'https://api.searchad.naver.com'
    
    def __init__(self, customer_id=None, api_key=None, secret_key=None):
        """
        네이버 API 클래스 초기화
        
        Args:
            customer_id (str): 네이버 검색광고 고객 ID
            api_key (str): 네이버 검색광고 API 키
            secret_key (str): 네이버 검색광고 시크릿 키
        """
        self.customer_id = customer_id
        self.api_key = api_key
        self.secret_key = secret_key
    
    def set_credentials(self, customer_id, api_key, secret_key):
        """API 인증 정보 설정"""
        self.customer_id = customer_id
        self.api_key = api_key
        self.secret_key = secret_key
    
    def _generate_signature(self, timestamp, method, uri):
        """HMAC 서명 생성"""
        msg = f"{timestamp}.{method}.{uri}"
        hash_obj = hmac.new(self.secret_key.encode(), msg.encode(), hashlib.sha256)
        return base64.b64encode(hash_obj.digest()).decode()
    
    def _check_credentials(self):
        """API 인증 정보가 모두 설정되었는지 확인"""
        if not all([self.customer_id, self.api_key, self.secret_key]):
            raise ValueError("API 인증 정보가 설정되지 않았습니다. set_credentials() 메서드를 호출하세요.")
    
    def search_keywords(self, keyword):
        """
        키워드 검색 API 호출
        
        Args:
            keyword (str): 검색할 키워드
            
        Returns:
            list: 키워드 검색 결과 목록
            
        Raises:
            ValueError: API 인증 정보가 설정되지 않은 경우
            requests.HTTPError: API 요청 중 HTTP 오류 발생 시
            ConnectionError: 네트워크 연결 오류 발생 시
            TimeoutError: API 요청 시간 초과 시
            Exception: 기타 예외 발생 시
        """
        self._check_credentials()
        
        uri = '/keywordstool'
        url = self.BASE_URL + uri
        method = 'GET'
        
        # 키워드에서 공백 제거
        keyword_param = keyword.replace(' ', '')
        params = {'hintKeywords': keyword_param, 'showDetail': 1}
        
        # 타임스탬프 및 서명 생성
        timestamp = str(round(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, uri)
        
        # 헤더 설정
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': timestamp,
            'X-API-KEY': self.api_key,
            'X-Customer': str(self.customer_id),
            'X-Signature': signature
        }
        
        try:
            # 최대 3번 재시도
            for attempt in range(3):
                try:
                    response = requests.get(
                        url, 
                        params=params, 
                        headers=headers,
                        timeout=10  # 타임아웃 10초 설정
                    )
                    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
                    return response.json().get('keywordList', [])
                
                except requests.Timeout:
                    if attempt < 2:  # 마지막 시도가 아니면 재시도
                        logger.warning(f"API 요청 시간 초과, {attempt+1}번째 재시도 중...")
                        time.sleep(1)  # 1초 대기 후 재시도
                    else:
                        raise TimeoutError("API 요청이 반복적으로 시간 초과되었습니다.")
                
                except requests.HTTPError as http_err:
                    # HTTP 상태 코드에 따른 상세 오류 처리
                    if response.status_code == 401:
                        raise ValueError("API 인증에 실패했습니다. API 키와 시크릿 키를 확인하세요.")
                    elif response.status_code == 429:
                        raise ValueError("API 호출 한도를 초과했습니다. 잠시 후 다시 시도하세요.")
                    else:
                        raise requests.HTTPError(f"HTTP 오류 발생: {http_err} (상태 코드: {response.status_code})")
        
        except requests.ConnectionError:
            raise ConnectionError("네트워크 연결에 실패했습니다. 인터넷 연결을 확인하세요.")
        
        except (ValueError, requests.HTTPError, TimeoutError, ConnectionError):
            # 이미 처리된 예외는 그대로 전달
            raise
        
        except Exception as e:
            # 기타 예외 처리
            logger.error(f"API 호출 중 예기치 않은 오류 발생: {str(e)}")
            raise Exception(f"API 호출 중 오류가 발생했습니다: {str(e)}") 