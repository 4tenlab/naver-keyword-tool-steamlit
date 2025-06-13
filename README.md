# 네이버 키워드 도구 (naver-keyword-tool-steamlit) v0.0.5 – Streamlit Edition

> **이 저장소는 네이버 키워드 도구의 Streamlit(steamlit) 기반 v0.0.5 공식 버전입니다.**
> - Repository: naver-keyword-tool-steamlit
> - PC 16:9 환경에 최적화된 웹 대시보드 버전

네이버 검색광고 API를 활용한 키워드 분석 도구입니다. PC 16:9 비율에 최적화된 대시보드 형태의 웹 인터페이스를 제공하며, 모듈화된 구조로 개선되었습니다.

## 기능

- 키워드 및 연관 키워드 검색량 조회
- 검색어 트렌드 그래프 시각화
- 검색 결과 엑셀/CSV 파일로 저장
- API 설정 저장 및 불러오기
- 키워드 검색 기록 관리
- 직관적인 대시보드 UI

## 설치 방법

### 1. GitHub 저장소 클론

```
git clone https://github.com/your-username/naver-keyword-tool.git
cd naver-keyword-tool
```

### 2. 소스 코드에서 실행 (PySide6 버전)

1. Python 3.6 이상 설치
2. 필요 라이브러리 설치: 
   ```
   pip install PySide6 requests matplotlib pandas openpyxl
   ```
3. `네이버_키워드_도구.py` 실행:
   ```
   python 네이버_키워드_도구.py
   ```

### 3. 웹 대시보드 실행 (권장)

1. Python 3.8 이상 설치
2. 필요 라이브러리 설치:
   ```
   pip install -r requirements.txt
   ```
3. 대시보드 실행:
   ```
   python main.py
   ```
   또는 직접 Streamlit 실행:
   ```
   streamlit run src/ui/dashboard_app.py
   ```
4. 웹 브라우저에서 http://localhost:8501 접속

## EXE 파일 생성 방법

프로그램을 EXE 파일로 변환하려면 다음 단계를 따르세요:

1. PyInstaller 설치:
   ```
   pip install pyinstaller
   ```

2. 빌드 스크립트 실행:
   ```
   python build_exe.py
   ```

3. 빌드가 완료되면 `dist` 폴더에 EXE 파일이 생성됩니다.

## 네이버 API 설정

프로그램 실행을 위해 네이버 검색광고 API 정보가 필요합니다:
- CUSTOMER_ID: 네이버 광고 계정 ID
- API_KEY: 발급받은 API 키
- SECRET_KEY: 발급받은 비밀키

### API 키 발급 방법

1. 네이버 검색광고 사이트(https://searchad.naver.com/)에 로그인
2. 관리 도구 > API 관리 > 비밀키 발급 및 관리
3. API 키와 Secret 키 생성 후 사용

## 개선된 기능 (v0.0.5)

> **본 버전은 Streamlit 기반 웹 대시보드 버전입니다.**
> - shadcn/ui 디자인 시스템 적용
> - PySide6 GUI 버전과 별도 관리

새로운 버전은 다음과 같은 개선사항을 제공합니다:

1. **shadcn/ui 디자인 시스템**
   - 모던하고 세련된 UI 컴포넌트
   - HSL 색상 팔레트 기반 일관된 테마
   - 부드러운 그림자와 테두리, 향상된 타이포그래피

2. **모듈화된 구조**
   - API 통신, 데이터 처리, 시각화 기능을 별도 모듈로 분리
   - 코드 재사용성과 유지보수성 향상
   - 단일 책임 원칙 적용

3. **PC 16:9 비율 최적화 대시보드**
   - 왼쪽: 키워드 입력 및 API 설정 패널
   - 오른쪽 상단: 연관 키워드 분석 결과 테이블
   - 오른쪽 하단: 키워드별 검색량 차트

4. **강화된 에러 처리**
   - 네트워크, 인증, HTTP 오류 등 상세한 예외 처리
   - API 요청 재시도 로직 구현
   - 사용자 친화적 오류 메시지

5. **환경변수 지원**
   - API 키를 환경변수로 안전하게 관리 가능
   - 설정 파일과 환경변수 우선순위 지원

6. **통합된 로깅 시스템**
   - 애플리케이션 전체에 걸친 표준화된 로깅
   - 디버깅과 모니터링 지원

## 웹 배포 방법

Streamlit 앱을 클라우드에 배포하려면 다음 방법을 사용할 수 있습니다:

### Streamlit Cloud 배포

1. GitHub에 코드를 푸시합니다.
2. [Streamlit Sharing](https://streamlit.io/sharing)에 가입합니다.
3. GitHub 저장소를 연결하고 배포합니다.

### Heroku 배포

1. Heroku CLI 설치 후 로그인:
   ```
   heroku login
   ```
2. requirements.txt 파일 확인:
   ```
   streamlit>=1.30.0
   pandas>=2.0.0
   plotly>=5.15.0
   requests>=2.30.0
   matplotlib>=3.7.0
   ```
3. 앱 배포:
   ```
   git init
   heroku create 네이버-키워드-도구
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## 프로젝트 구조

```
naver-keyword-tool/
├── main.py                   # 통합 메인 실행 파일
├── config.json               # 애플리케이션 설정 파일
├── requirements.txt          # 프로젝트 의존성
├── README.md                 # 프로젝트 설명서
├── logs/                     # 로그 파일 저장 디렉토리
└── src/                      # 모듈화된 소스 코드
    ├── api/                  # API 통신 관련 모듈
    │   └── naver_api.py      # 네이버 검색광고 API 클래스
    ├── data/                 # 데이터 처리 관련 모듈
    │   └── keyword_processor.py  # 키워드 데이터 처리 클래스
    ├── ui/                   # 사용자 인터페이스 관련 모듈
    │   ├── streamlit_app.py  # 기존 Streamlit 웹 애플리케이션
    │   └── dashboard_app.py  # 새로운 대시보드 애플리케이션
    └── utils/                # 유틸리티 모듈
        ├── config_manager.py # 설정 관리 클래스
        ├── common.py         # 공통 유틸리티 함수
        └── visualization.py  # 데이터 시각화 클래스
```

### 모듈별 책임 분리

- **`api/naver_api.py`**: 네이버 검색광고 API 통신 전담
  - 인증, 요청, 응답 처리
  - 오류 처리 및 재시도 로직

- **`data/keyword_processor.py`**: 키워드 데이터 처리 및 분석
  - 데이터 정제, 변환, 통계 계산
  - Excel 내보내기 기능

- **`utils/config_manager.py`**: 설정 및 인증 정보 관리
  - 환경변수 및 파일 기반 설정
  - API 인증 정보 안전 관리

- **`utils/common.py`**: 공통 유틸리티 함수
  - 한글 폰트 설정, 데이터 변환
  - 검증 및 포맷팅 함수

- **`ui/dashboard_app.py`**: PC 16:9 최적화 대시보드
  - 첨부된 스크린샷과 동일한 레이아웃
  - 모던한 UI/UX 디자인

## 참고사항

- 처음 실행 시 기본 API 정보가 제공되지만, 실제 사용 시에는 개인 API 키로 변경이 필요합니다.
- 검색 결과는 최근 30일 기준이며, 네이버 검색광고 API 정책에 따라 변경될 수 있습니다.
- 모듈화된 코드 구조로 유지보수 및 확장이 용이합니다.
- API 통신, 데이터 처리, 시각화, 설정 관리 등의 기능이 별도 모듈로 분리되어 있습니다.
- PySide6 기반 GUI 버전보다 Streamlit 웹 앱 버전(v0.0.5)이 권장됩니다.
- v0.0.5부터 shadcn/ui 디자인 시스템이 적용되어 웹 배포에 최적화되었습니다.