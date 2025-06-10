"""
네이버 검색어 도구를 EXE 파일로 빌드하는 스크립트
"""
import os
import sys
import shutil
import subprocess

def build_executable():
    print("네이버 검색어 도구 EXE 빌드를 시작합니다...")
    
    # 필요한 라이브러리 설치 확인
    print("필요한 라이브러리를 설치합니다...")
    os.system("pip install pyinstaller")
    os.system("pip install matplotlib pandas openpyxl")
    
    # 이전 빌드 폴더 정리
    if os.path.exists("dist"):
        print("이전 빌드 폴더를 정리합니다...")
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    
    # PyInstaller 경로 찾기 (사용자 설치 디렉토리)
    user_scripts_dir = os.path.expanduser("~\\AppData\\Roaming\\Python\\Python313\\Scripts")
    pyinstaller_path = os.path.join(user_scripts_dir, "pyinstaller.exe")
    
    if not os.path.exists(pyinstaller_path):
        print(f"PyInstaller를 찾을 수 없습니다: {pyinstaller_path}")
        print("대체 경로 시도중...")
        # 다른 가능한 경로들 시도
        possible_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\Python\\Python311\\Scripts\\pyinstaller.exe"),
            os.path.expanduser("~\\AppData\\Roaming\\Python\\Python310\\Scripts\\pyinstaller.exe"),
            os.path.expanduser("~\\AppData\\Roaming\\Python\\Python39\\Scripts\\pyinstaller.exe"),
            "pyinstaller.exe"  # 마지막 수단으로 PATH에서 찾기 시도
        ]
        
        for path in possible_paths:
            if os.path.exists(path) or path == "pyinstaller.exe":
                pyinstaller_path = path
                print(f"PyInstaller 경로: {pyinstaller_path}")
                break
    
    # PyInstaller 명령 실행
    print("EXE 파일을 빌드합니다...")
    pyinstaller_cmd = f'"{pyinstaller_path}" --name "네이버 키워드 도구 v0.0.4" --windowed --onefile "네이버_키워드_도구.py"'
    
    # 아이콘 파일이 있으면 추가
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        pyinstaller_cmd = pyinstaller_cmd.replace('--onefile', f'--icon="{icon_path}" --onefile')
    
    # PyInstaller 실행
    print(f"실행 명령: {pyinstaller_cmd}")
    result = os.system(pyinstaller_cmd)
    
    if result == 0:
        print("\n빌드 성공! 다음 위치에서 EXE 파일을 찾을 수 있습니다:")
        print(f"  {os.path.abspath('dist')}")
        print("\n이 파일을 다른 컴퓨터에 복사하여 실행할 수 있습니다.")
    else:
        print("\n빌드 실패! 오류를 확인하세요.")
        
        # 대체 방법으로 subprocess 사용 시도
        print("\n대체 방법으로 빌드를 시도합니다...")
        try:
            result = subprocess.run(
                [
                    sys.executable, 
                    "-m", 
                    "PyInstaller", 
                    "--name", 
                    "네이버 키워드 도구 v0.0.4", 
                    "--windowed", 
                    "--onefile", 
                    "네이버_키워드_도구.py"
                ],
                check=True
            )
            print("\n빌드 성공! 다음 위치에서 EXE 파일을 찾을 수 있습니다:")
            print(f"  {os.path.abspath('dist')}")
        except subprocess.CalledProcessError as e:
            print(f"\n대체 방법도 실패했습니다: {e}")
            print("python -m PyInstaller 명령어를 직접 실행해보세요.")
    
    return result

if __name__ == "__main__":
    sys.exit(build_executable()) 