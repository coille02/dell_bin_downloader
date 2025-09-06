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
- Chromium 브라우저
- 인터넷 연결

## Ubuntu/Debian 시스템 설치 및 설정

### 1. 시스템 패키지 업데이트

```bash
sudo apt update
```

### 2. Chromium 브라우저 및 ChromeDriver 설치

```bash
sudo apt install chromium-browser chromium-chromedriver -y
```

### 3-A. Python 패키지 설치 (가상환경 사용)

```bash
# 가상환경 생성
python3 -m venv dell_env

# 가상환경 활성화
source dell_env/bin/activate

# 패키지 설치
pip install selenium requests
```

### 3-B. Python 패키지 설치 (시스템 전역 설치 - Jenkins용)

```bash
# 시스템 전역에 패키지 설치
sudo apt install python3-pip -y
pip3 install selenium requests

# 또는 시스템 패키지로 설치
sudo apt install python3-selenium python3-requests -y
```

## 사용법

### 로컬 환경 (가상환경 사용)

```bash
# 가상환경 활성화 (매번 실행 전 필요)
source dell_env/bin/activate

# 스크립트 실행
python dell_driver_r440_ubuntu_22.04_downloader.py
```

### Jenkins 환경 (시스템 전역 설치)

```bash
# 직접 실행
python3 dell_driver_r440_ubuntu_22.04_downloader.py

# 모든 운영체제 드라이버 다운로드
python3 dell_driver_r440_all_os_downloader.py
```

### Jenkins Pipeline 예제

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    sudo apt update
                    sudo apt install -y chromium-browser chromium-chromedriver python3-pip
                    pip3 install selenium requests
                '''
            }
        }
        
        stage('Download Dell Drivers') {
            steps {
                sh '''
                    python3 dell_driver_r440_ubuntu_22.04_downloader.py
                '''
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'downloads/**/*.BIN', fingerprint: true
            }
        }
    }
}
```

스크립트 실행 시 자동으로 `downloads/Ubuntu_Server_22.04_LTS/` 폴더에 .bin 파일들이 다운로드됩니다.

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
source dell_env/bin/activate

# 가상환경이 없는 경우 다시 생성
python3 -m venv dell_env
```

### ChromeDriver 오류
- Chromium 브라우저가 설치되어 있는지 확인
- 인터넷 연결 상태 확인
- 가상환경이 활성화되어 있는지 확인

```bash
# ChromeDriver 재설치
sudo apt install --reinstall chromium-chromedriver -y
```

### 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 재설치
pip install selenium requests
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
1. `dell_env` 폴더를 Python 인터프리터로 선택
2. 터미널에서 가상환경 활성화 확인

### 디버깅
- 스크립트 실행 중 오류 발생 시 터미널 출력 확인
- 네트워크 연결 및 Dell 웹사이트 접근 가능 여부 확인

## 주의사항

- Dell 웹사이트의 이용약관을 준수하세요
- 과도한 요청으로 서버에 부하를 주지 않도록 주의하세요
- 다운로드한 파일의 무결성을 확인하세요
- 가상환경 사용을 권장합니다

## 라이선스

이 스크립트는 개인 및 교육 목적으로만 사용하세요.
