"""
네이버 키워드 도구 - Streamlit Cloud 배포용 메인 파일
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python Path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# dashboard_app.py의 내용을 직접 실행
from src.ui.dashboard_app import run_dashboard

# Streamlit Cloud에서 직접 실행
if __name__ == "__main__":
    run_dashboard() 