"""
네이버 키워드 도구 메인 실행 파일

이 파일은 네이버 키워드 도구의 메인 진입점입니다.
Streamlit 웹 애플리케이션을 실행합니다.
"""
import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python Path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정 (Streamlit Cloud 환경 고려)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 콘솔 로깅만 사용
    ]
)

def main():
    """메인 실행 함수"""
    try:
        # logs 디렉토리 생성 (로컬 환경용)
        try:
            os.makedirs('logs', exist_ok=True)
        except (OSError, PermissionError):
            # Streamlit Cloud 등에서 디렉토리 생성이 안 될 경우 무시
            pass
        
        # Streamlit 서버 실행
        import subprocess
        cmd = [sys.executable, "-m", "streamlit", "run", "src/ui/dashboard_app.py"]
        
        # 환경변수 설정
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        logging.info("Streamlit 대시보드를 시작합니다...")
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        logging.info("사용자에 의해 애플리케이션이 종료되었습니다.")
    except Exception as e:
        logging.error(f"애플리케이션 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 