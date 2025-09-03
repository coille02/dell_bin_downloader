# Dell PowerEdge R440 드라이버 다운로더

Dell PowerEdge R440 서버의 모든 운영체제에 대한 .bin 파일들을 자동으로 다운로드하는 Python 스크립트입니다.

## 기능

- 모든 지원 운영체제 자동 감지
- Ubuntu 22.04 LTS 전용 다운로더 포함
- .bin 파일만 선택적으로 다운로드
- 운영체제별 폴더 자동 생성
- 다운로드 진행 상황 로깅
- 중복 다운로드 방지
- 다운로드 정보 JSON 파일 생성

## 요구사항

- Python 3.8 이상
- Chrome 브라우저
- 인터넷 연결

## 설치 및 설정

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source .venv/bin/activate
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. Chrome 브라우저 확인

Chrome 브라우저가 설치되어 있는지 확인하세요.

## 사용법

### 모든 운영체제 드라이버 다운로드

```bash
python dell_driver_r440_all_os_downloader.py
```

### Ubuntu 22.04 LTS 전용 드라이버 다운로드

```bash
python dell_driver_r440_ubuntu_22.04_downloader.py
```

실행하면 다운로드 디렉토리를 입력하라는 메시지가 나타납니다. 
Enter를 누르면 기본값인 "downloads" 폴더가 사용됩니다.

## 출력 파일

- `downloads/`: 다운로드된 파일들이 저장되는 폴더
- `downloads/OS_[운영체제값]/`: 운영체제별 하위 폴더
- `downloads/download_info.json`: 다운로드 정보 파일
- `dell_download.log`: 로그 파일
- `page_source.html`: 디버깅용 페이지 소스 (필요시)

## 주요 특징

### 자동화 기능
- ChromeDriver 자동 다운로드 및 관리
- 웹페이지 자동 탐색
- 운영체제 드롭다운 자동 감지
- .bin 파일 링크 자동 추출

### 안정성
- 페이지 로딩 대기
- 네트워크 오류 처리
- 중복 다운로드 방지
- 상세한 로깅

### 사용자 친화적
- 진행 상황 실시간 표시
- 오류 메시지 한글화
- 다운로드 정보 JSON 저장

## 스크립트 설명

### dell_driver_r440_all_os_downloader.py
- 모든 지원 운영체제의 드라이버를 자동으로 다운로드
- 운영체제별로 폴더를 자동 생성
- 각 운영체제의 .bin 파일들을 수집

### dell_driver_r440_ubuntu_22.04_downloader.py
- Ubuntu 22.04 LTS 전용 드라이버 다운로더
- Ubuntu 서버에 특화된 드라이버만 다운로드
- 더 빠른 실행 속도

## 문제 해결

### 가상환경 관련
```bash
# 가상환경이 활성화되지 않는 경우
# Windows PowerShell에서 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ChromeDriver 오류
- Chrome 브라우저가 최신 버전인지 확인
- 인터넷 연결 상태 확인
- 가상환경이 활성화되어 있는지 확인

### 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 캐시 클리어 후 재설치
pip cache purge
pip install -r requirements.txt
```

### 페이지 로딩 실패
- 네트워크 연결 확인
- Dell 웹사이트 접근 가능 여부 확인
- `page_source.html` 파일 확인하여 페이지 구조 분석

### 다운로드 실패
- 로그 파일(`dell_download.log`) 확인
- 파일 권한 확인
- 디스크 공간 확인

## 개발 환경 설정

### IDE 설정 (VS Code)
1. `.venv` 폴더를 Python 인터프리터로 선택
2. 터미널에서 가상환경 활성화 확인

### 디버깅
- `page_source.html` 파일을 생성하여 웹페이지 구조 분석
- 로그 파일을 통해 실행 과정 추적

## 주의사항

- Dell 웹사이트의 이용약관을 준수하세요
- 과도한 요청으로 서버에 부하를 주지 않도록 주의하세요
- 다운로드한 파일의 무결성을 확인하세요
- 가상환경 사용을 권장합니다

## 라이선스

이 스크립트는 개인 및 교육 목적으로만 사용하세요.
