# 네이버 키워드 도구 v0.0.5 - Streamlit Edition

> **네이버 검색광고 API를 활용한 키워드 분석 웹 애플리케이션**
> - 🎯 연관 키워드 자동 분석
> - 📊 검색량 데이터 시각화  
> - 💾 Excel 다운로드 지원
> - 🔒 보안 강화된 API 키 관리

## 🚀 빠른 시작

### 1. 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/4tenlab/naver-keyword-tool-steamlit.git
cd naver-keyword-tool-steamlit

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run src/ui/streamlit_app.py
```

브라우저에서 `http://localhost:8501` 접속

### 2. Streamlit Cloud 배포

1. **GitHub 저장소 연결**
   - Repository: `4tenlab/naver-keyword-tool-steamlit`
   - Branch: `main`
   - Main file path: `streamlit_app.py` (또는 비워두기)

2. **API 키 설정** (Settings → Secrets)
   ```toml
   [api]
   CUSTOMER_ID = "your_actual_customer_id"
   API_KEY = "your_actual_api_key"
   SECRET_KEY = "your_actual_secret_key"
   ```

## 🔑 네이버 API 설정

### API 키 발급 방법

1. [네이버 검색광고](https://searchad.naver.com/) 로그인
2. **관리 도구** → **API 관리** → **비밀키 발급 및 관리**
3. API 키와 Secret 키 생성

### 🔐 보안 강화된 API 키 관리

#### 로컬 개발용
`.streamlit/secrets.toml` 파일 생성:
```toml
[api]
CUSTOMER_ID = "your_actual_customer_id"
API_KEY = "your_actual_api_key"
SECRET_KEY = "your_actual_secret_key"
```

#### 프로덕션 배포용
- **Streamlit Cloud**: Settings → Secrets에서 설정
- **환경변수**: `NAVER_CUSTOMER_ID`, `NAVER_API_KEY`, `NAVER_SECRET_KEY`
- **로컬 파일**: 자동 암호화 저장 (Base64)

> **보안 특징**: API 키는 암호화되어 저장되며, 민감한 정보는 Git에 업로드되지 않습니다.

## ✨ 주요 기능

### 🎯 키워드 분석
- **연관 키워드 자동 추출**: 메인 키워드 기반 관련 키워드 발견
- **검색량 데이터**: PC/모바일별 월간 검색량 조회
- **경쟁도 분석**: 키워드별 광고 경쟁 정도 분석

### 📊 데이터 시각화
- **인터랙티브 차트**: Plotly 기반 동적 차트
- **상위 키워드 분석**: 검색량 기준 TOP 10 시각화
- **경쟁도 분포**: 키워드별 경쟁 정도 분석

### 💾 데이터 내보내기
- **Excel 다운로드**: 분석 결과를 Excel 파일로 저장
- **스타일링 적용**: 네이버 브랜드 컬러로 포맷팅
- **즉시 다운로드**: 원클릭 파일 저장

### 🎨 사용자 경험
- **2:8 레이아웃**: 입력(20%) + 결과(80%) 최적 비율
- **네이버 브랜드 디자인**: 일관된 그린 컬러 테마
- **반응형 UI**: 다양한 화면 크기 지원

## 🏗️ 프로젝트 구조

```
naver-keyword-tool-steamlit/
├── 📄 streamlit_app.py          # 🎯 메인 애플리케이션 (유일한 실행 파일)
├── 📄 requirements.txt          # 의존성 패키지
├── 📄 README.md                 # 프로젝트 문서
├── 📄 Procfile                  # Heroku 배포 설정
├── 📁 .streamlit/
│   └── secrets.toml             # API 키 (로컬용, Git 제외)
├── 📁 src/
│   ├── 📁 api/
│   │   └── naver_api.py         # 네이버 API 통신
│   ├── 📁 data/
│   │   └── keyword_processor.py # 데이터 처리
│   ├── 📁 ui/
│   │   └── streamlit_app.py     # 메인 UI (심볼릭 링크)
│   └── 📁 utils/
│       ├── config_manager.py    # 설정 관리 (암호화 지원)
│       ├── common.py            # 공통 유틸리티
│       └── visualization.py     # 시각화 도구
└── 📁 logs/                     # 로그 파일
```

### 🔧 모듈별 역할

| 모듈 | 책임 | 주요 기능 |
|------|------|-----------|
| `streamlit_app.py` | 메인 애플리케이션 | UI, 사용자 인터랙션, 전체 흐름 제어 |
| `naver_api.py` | API 통신 | 네이버 검색광고 API 호출, 인증 처리 |
| `keyword_processor.py` | 데이터 처리 | 키워드 분석, 데이터 변환, 통계 계산 |
| `config_manager.py` | 설정 관리 | API 키 암호화 저장, 환경변수 처리 |
| `common.py` | 공통 기능 | 유틸리티 함수, 검증, 포맷팅 |

## 🔒 보안 기능

### 다층 보안 구조
1. **1순위**: Streamlit Cloud Secrets (프로덕션)
2. **2순위**: 환경변수 (서버 배포)  
3. **3순위**: 암호화된 로컬 파일 (개발)

### 보안 특징
- ✅ **API 키 암호화**: Base64 인코딩으로 로컬 저장
- ✅ **입력 검증**: XSS/스크립트 공격 방지
- ✅ **민감 정보 차단**: .gitignore로 완전 보호
- ✅ **UI 마스킹**: API 키 화면 표시 시 마스킹 처리

## 🎯 사용 방법

### 1. 키워드 입력
- 분석하고 싶은 메인 키워드 입력
- 예: "다이어트", "운동", "요리" 등

### 2. API 설정
- 네이버 검색광고 API 키 입력
- 또는 Streamlit Secrets에서 자동 로드

### 3. 분석 실행
- "🚀 키워드 분석 실행" 버튼 클릭
- 연관 키워드 자동 추출 및 검색량 조회

### 4. 결과 확인
- **테이블**: 키워드별 상세 데이터
- **차트**: 상위 키워드 검색량 시각화
- **다운로드**: Excel 파일로 저장

## 📊 분석 결과 예시

### 키워드: "다이어트"
| 키워드 | 월간 검색량 | PC | 모바일 | 경쟁정도 |
|--------|-------------|----|---------|---------| 
| 다이어트 | 1,234,567 | 456,789 | 777,778 | 높음 |
| 다이어트 식단 | 987,654 | 321,098 | 666,556 | 중간 |
| 다이어트 운동 | 765,432 | 234,567 | 530,865 | 중간 |

### 차트 기능
- 📈 상위 10개 키워드 검색량 바차트
- 🎨 네이버 브랜드 그린 컬러 적용
- 🔍 호버 시 상세 정보 표시

## 🚀 배포 옵션

### Streamlit Cloud (권장)
```bash
# 1. GitHub에 푸시
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main

# 2. Streamlit Cloud에서 배포
# - Repository: 4tenlab/naver-keyword-tool-steamlit
# - Main file: streamlit_app.py
```

### Heroku
```bash
# Heroku CLI로 배포
heroku create naver-keyword-tool
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "src/ui/streamlit_app.py"]
```

## 🔧 개발 환경 설정

### 필수 요구사항
- **Python**: 3.8 이상
- **패키지**: requirements.txt 참조
- **API**: 네이버 검색광고 API 키

### 개발 모드 실행
```bash
# 개발 서버 실행 (핫 리로드)
streamlit run src/ui/streamlit_app.py --server.runOnSave true

# 디버그 모드
streamlit run src/ui/streamlit_app.py --logger.level debug
```

## 📝 업데이트 내역

### v0.0.5 (현재)
- ✅ **단일 파일 구조**: `streamlit_app.py` 하나로 통합
- ✅ **보안 강화**: API 키 암호화 저장
- ✅ **UI 개선**: shadcn/ui 디자인 시스템 적용
- ✅ **성능 최적화**: 모듈화된 구조로 개선

### 이전 버전 대비 개선사항
- 🔄 **파일 구조 단순화**: 3개 실행 파일 → 1개 통합
- 🔒 **보안 강화**: 평문 저장 → 암호화 저장
- 🎨 **디자인 개선**: 기본 UI → 네이버 브랜드 디자인
- ⚡ **성능 향상**: 중복 코드 제거, 최적화

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

- **이메일**: 4tenlab@gmail.com
- **GitHub Issues**: [문제 신고](https://github.com/4tenlab/naver-keyword-tool-steamlit/issues)
- **Live Demo**: [https://naver-keyword-tool-4tenlab.streamlit.app/](https://naver-keyword-tool-steamlit-4tenlab.streamlit.app/)

---

**Made with ❤️ by 4tenlab**