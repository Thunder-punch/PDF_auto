# PDF 사무자동화

PDF 문서 자동화 도구입니다. 이 프로그램은 PDF 양식을 자동으로 채우고 관리하는 기능을 제공합니다.

## 주요 기능

- PDF 양식 자동 채우기
  - 템플릿 기반 자동 입력
  - 다중 PDF 동시 처리
  - 사용자 정의 필드 매핑
- 회사별 폴더 자동 생성 및 관리
  - 회사 정보 기반 폴더 구조화
  - 파일 자동 분류
- 라이선스 관리 시스템
  - 사용자 인증
  - 라이선스 키 관리
  - 사용 기간 제한
- 사용자 친화적인 GUI 인터페이스
  - 직관적인 작업 흐름
  - 진행 상황 실시간 표시
  - 오류 메시지 및 알림

## 설치 방법

1. 최신 릴리즈 버전을 다운로드합니다.
   - [릴리즈 페이지](https://github.com/Thunder-punch/PDF_auto/releases)에서 최신 버전 확인
2. 설치 파일을 실행합니다.
3. 설치 마법사의 지시를 따릅니다.

### 설치 실패 시 해결 방법

1. 관리자 권한으로 실행
2. 안티바이러스 프로그램 일시 중지
3. 이전 버전 완전 제거 후 재설치
4. [자세한 문제 해결 가이드](설치실패시_꼭_읽어_주세요.txt) 참조

## 시스템 요구사항

- Windows 10 이상
- 최소 4GB RAM
- 500MB 이상의 하드디스크 여유 공간
- Python 3.8 이상 (개발용)

## 개발 환경 설정

1. 저장소를 클론합니다:
```bash
git clone https://github.com/Thunder-punch/PDF_auto.git
```

2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

## 프로젝트 구조 및 데이터 흐름

### 디렉토리 구조

```
PDF_auto/
├── main.py              # 메인 실행 파일
├── utils/              # 유틸리티 함수들
├── ui/                 # 사용자 인터페이스 관련 코드
├── resources/          # 리소스 파일들 (로컬 전용)
├── pdf/               # PDF 관련 처리 코드
├── output/            # 생성된 PDF 저장 폴더
├── logs/              # 로그 파일 저장 폴더
└── config.json        # 설정 파일
```

### 파일 연결 구조도

```
main.py (메인 진입점)
├── utils/
│   ├── config.py          # 버전, 리소스 경로 등 설정
│   └── ...               # 기타 유틸리티 함수들
├── ui/
│   └── main_screen.py    # 메인 GUI 화면 (App 클래스)
├── resources/
│   └── fonts/           # 폰트 파일들 (NanumGothic.ttf 등)
└── 외부 라이브러리
    ├── reportlab        # PDF 생성 라이브러리
    ├── tkinter         # GUI 라이브러리
    └── logging         # 로깅 시스템
```

주요 기능 흐름:
1. 프로그램 시작 (main.py)
   - 하드웨어 ID 확인
   - 라이선스 검증
   - 로깅 시스템 초기화
2. GUI 실행 (ui/main_screen.py)
   - 메인 화면 표시
   - 사용자 입력 처리
3. PDF 처리 (pdf/ 디렉토리)
   - 템플릿 로드
   - 데이터 매핑
   - PDF 생성
4. 결과 저장 (output/ 디렉토리)
   - 생성된 PDF 저장
   - 로그 기록

### 데이터/파일 흐름도

```mermaid
flowchart TD
    A[사용자 입력<br>엑셀/수기 데이터] --> B[데이터 전처리 및 매핑<br>main.py, utils/]
    B --> C[PDF 템플릿 로드<br>pdf/]
    C --> D[PDF 자동 생성<br>reportlab, pdf/]
    D --> E[결과물 저장<br>output/]
    D --> F[로그 기록<br>logs/]
```

## 사용 방법

1. 프로그램 실행
2. 회사 정보 입력
3. PDF 템플릿 선택
4. 데이터 입력 또는 Excel 파일 업로드
5. 자동 생성 시작

## 문제 해결

- 로그 파일 확인: `logs/` 폴더
- 설정 파일 확인: `config.json`
- 자주 발생하는 오류와 해결 방법은 [문제 해결 가이드](설치실패시_꼭_읽어_주세요.txt) 참조

## 기여 방법

1. 이슈 등록
2. Fork 후 개발
3. Pull Request 생성

## 라이선스

이 프로젝트는 개인 및 기업용으로 사용 가능합니다.
- 상업적 사용 가능
- 수정 및 배포 가능
- 개인정보 보호 규정 준수

## 버전 정보

현재 버전: v1.2.5
- PDF 양식 자동 채우기 기능 개선
- 사용자 인터페이스 업데이트
- 성능 최적화

## [2024-05-14 업데이트]
- **UI/UX 개선**
  - 모든 입력란(Entry, DateEntry, Combobox 등) 가로 길이 통일, 우측 끝선 정렬
  - 분할 입력란(사업자등록번호, 주민등록번호, 전화번호, 유효기간)도 우측 끝선에 맞게 width 정수 조정
  - 입력란, 라벨, 버튼, 체크박스 등 폰트 Pretendard로 완전 통일
  - 라벨, 타이틀, 안내문 등 글씨 크기 일관성 유지 (타이틀: Pretendard 28 bold, 라벨: Pretendard 13)
  - "생성할 PDF 항목 선택" 라벨 스타일 개선
  - 인감 미리보기 상단 문구 "자문사 인감"으로 변경 및 중앙 정렬
  - 전체 화면 세로 크기, 입력란 세로 간격 등 컴팩트하게 조정

- **버그 수정**
  - Entry width에 소수점 사용 시 발생하는 오류 수정 (정수로만 지정)
  - 일부 화면에서 NanumGothic/NanumGothicBold → Pretendard로 일괄 변경

- **배포/실행파일**
  - PyInstaller로 단일 exe 생성 방법 안내 및 리소스 포함 옵션 추가

## 연락처
- 이메일: texclaim@naver.com
- GitHub: [Thunder-punch](https://github.com/Thunder-punch)

## 실행파일 생성 명령어

```
pyinstaller --noconsole --onefile main.py

# 또는
# pyinstaller --windowed --onefile main.py

# main.py 대신 실제 실행 진입점 파일명을 사용하세요.
# --noconsole 옵션을 사용하면 실행 시 터미널(검은 창)이 뜨지 않습니다.
```

## 최근 주요 수정 내역 (2024-05-17)

- 실행 오류 해결을 위해 requirements.txt에 다음 패키지 추가:
  - Pillow, tkcalendar, pdfrw
- PyInstaller 빌드 시 외부 라이브러리 누락 문제 해결
- Inno Setup(사무자동화.iss) 스크립트의 파일 경로를 절대경로(C:\Users\texcl\HaelfriendsApp)로 수정
- README.txt 파일이 없어도 설치가 되도록 Source 라인 삭제
- 기타: 빌드/설치 오류 발생 시, 관련 Source 라인 주석 처리 또는 빈 파일 생성으로 대응 

## 필요 패키지 설치

이 프로젝트에 필요한 모든 파이썬 패키지는 `requirements.txt` 파일에 정리되어 있습니다.
아래 명령어로 한 번에 설치할 수 있습니다.

```bash
pip install -r requirements.txt
``` 