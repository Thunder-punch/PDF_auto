import os
import shutil
import zipfile
import subprocess

APP_NAME = "PDF사무자동화"
VERSION = "v1.2.4"
ROOT_DIR = os.getcwd()
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BUILD_DIR = os.path.join(ROOT_DIR, f"{APP_NAME}_{VERSION}")
ZIP_PATH = os.path.join(ROOT_DIR, f"{APP_NAME}_{VERSION}.zip")

def build_executable():
    print("📦 실행파일 빌드 중...")
    subprocess.run([
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "main.py"
    ])
    print("✅ 실행파일 생성 완료.")

def prepare_package():
    print("📁 배포용 폴더 구성 중...")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

    # 실행파일
    exe_name = f"{APP_NAME}.exe"
    shutil.copy(os.path.join(DIST_DIR, "main.exe"), os.path.join(BUILD_DIR, "실행파일.exe"))
    os.rename(os.path.join(BUILD_DIR, "실행파일.exe"), os.path.join(BUILD_DIR, exe_name))

    # 소스코드
    src_code_dir = os.path.join(BUILD_DIR, "소스코드")
    os.makedirs(src_code_dir)
    for folder in ["pdf", "ui", "utils", "resources"]:
        shutil.copytree(os.path.join(ROOT_DIR, folder), os.path.join(src_code_dir, folder))
    shutil.copy(os.path.join(ROOT_DIR, "main.py"), src_code_dir)

    # 문서
    for doc in ["README.md", "requirements.txt"]:
        src = os.path.join(ROOT_DIR, doc)
        if os.path.exists(src):
            shutil.copy(src, BUILD_DIR)

    print("✅ 폴더 구성 완료.")

def zip_package():
    print("🗜 압축파일 생성 중...")
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BUILD_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, BUILD_DIR)
                zipf.write(abs_path, rel_path)
    print(f"✅ 압축 완료: {ZIP_PATH}")

if __name__ == "__main__":
    build_executable()
    prepare_package()
    zip_package()
