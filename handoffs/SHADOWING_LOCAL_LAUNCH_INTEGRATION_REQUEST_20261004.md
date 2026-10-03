# Shadowing Local Admin — Skyview 원클릭 실행 연동 작업지시

## 선택 템플릿
**추가수정 작업지시**

## 0. Toby 판단
이 작업은 새 제품 기획이 필요한 난도가 아니라,
이미 구현된 `지식 도서관`의 로컬 실행 패턴을
`Tony's English Shadowing`에 동일하게 적용하는 **중간 난도 통합 작업**이다.

따라서 별도 기획 단계 없이 바로 구현한다.

### 역할/모델
- **Geni**: 작업 관리, 저장소 상태 확인, 결과 통합
- **Tody**: 실제 코드 구현 담당 — **GPT-6 Astra**
  - 이유: Windows URL Protocol + Python launcher + Django UI의 cross-repo 통합이므로 단순 CSS 수정보다 난도가 높지만, 기존 검증된 패턴을 재사용할 수 있어 Astra 1회 구현이 적절함.
- **Any**: 독립 검증 — **사용 가능한 Gemini 최고 성능 모델**
- **Hank**: 이번 작업에는 기본적으로 사용하지 않음. Tody가 구조적 문제를 발견했을 때만 추가 검토.

Owner는 아래 범위 전체를 승인했다. 중간 승인 없이 완료까지 진행한다.

---

## 1. 목적
Skyview Owner 전용 Portal에서 **「영어 쉐도잉」** 버튼을 누르면,
Owner PC의 `Tony's English Shadowing` Local Admin이 자동으로 실행되고
브라우저에서 `http://127.0.0.1:8765`가 열리도록 한다.

이 Local Admin에서 YouTube URL을 입력하여 새 Shadowing 콘텐츠를 생성할 수 있어야 한다.

현재 Shadowing Local Admin 자체는 이미 구현되어 있으나,
Skyview에서 여는 **원클릭 진입 버튼/launcher/protocol 연동이 없는 상태**다.

---

## 2. 기준이 되는 기존 구현
반드시 기존 YouTube Knowledge Agent의 검증된 구현을 우선 참조한다.

Repository:
- `tonykks/youtube-knowledge-agent`

참조 파일:
- `scripts/library_launcher.py`
- `scripts/register_protocol.py`
- `scripts/register_protocol.bat`
- `scripts/unregister_protocol.py`
- `scripts/unregister_protocol.bat`

기존 Knowledge Library:
- Protocol: `tony-library://open`
- Local URL: `http://127.0.0.1:8080`
- Skyview 버튼: `지식 도서관 📚`

Shadowing은 이 구조를 복제하되 서로 충돌하지 않는 별도 protocol/port를 사용한다.

---

## 3. Shadowing 쪽 구현

대상 Repository:
- `tonykks/english-shadowing-agent`

### 3.1 Protocol
새 custom URL protocol:
- **`tony-shadowing://open`**

허용 command:
- `open`만 허용
- 임의 인자/경로/shell injection 차단

Windows 등록 위치:
- `HKEY_CURRENT_USER\Software\Classes\tony-shadowing`
- 관리자 권한 불필요

### 3.2 Local Server
현재 Shadowing Local Admin:
- URL: `http://127.0.0.1:8765`
- 실행 진입점: `run.py`

기존 `run.py` 구조를 확인하고,
launcher가 서버를 정확히 실행하도록 한다.

### 3.3 Launcher
권장 파일:
- `scripts/shadowing_launcher.py`
- `scripts/register_protocol.py` 또는 기존 파일명 충돌이 있으면 `register_shadowing_protocol.py`
- register/unregister BAT 포함

기능:
1. 127.0.0.1:8765가 이미 실행 중인지 확인
2. 실행 중이면 추가 프로세스 없이 브라우저만 오픈
3. 꺼져 있으면 `pythonw.exe` 우선으로 Local Admin 서버 무음 실행
4. 검은 콘솔창 0개를 목표
5. 서버 응답 확인 후 브라우저 오픈
6. 실패 시 무한대기/중복 프로세스 금지

Knowledge Library launcher의 보안/무음 원칙을 그대로 재사용한다.

---

## 4. Skyview 버튼 추가

대상 Repository:
- `tonykks/skyview-django`

대상 Owner Portal:
- `skyview/templates/skyview/private_reports.html`
- `skyview/templates/skyview/toss_reports.html`

현재 서비스 전환 바:
- Email
- Market
- Invest ⚡
- 지식 도서관 📚
- Admin
- 로그아웃

여기에 아래 버튼 추가:

### 표시명
**영어 쉐도잉 🎧**

### 링크
`tony-shadowing://open`

### 목적
Owner PC의 Shadowing Local Admin 자동 실행 및 새 탭/브라우저 진입.

### 스타일
- 기존 버튼들과 높이/간격/폰트 통일
- Knowledge Library와 구분되지만 과도하게 튀지 않는 색
- 권장: blue/cyan 계열
- 버튼이 늘어나도 header가 깨지지 않도록 responsive 확인

### 공개 범위
- 현재 Owner 인증 Portal 안에서만 보이므로 그대로 유지
- 일반 공개 Skyview 화면에는 노출하지 않음

---

## 5. 설치/사용성
처음 1회만 protocol 등록이 필요하다.

Owner가 쉽게 실행할 수 있도록:
- BAT 또는 Python 등록 스크립트 제공
- 등록 후 Skyview의 `영어 쉐도잉 🎧` 버튼 클릭만으로 실행

가능하면 기존 Knowledge Library와 동일한 사용 경험으로 맞춘다.

---

## 6. 검증

### 6.1 Shadowing Agent
- protocol URL validation
- 8765 미실행 상태 → 버튼 클릭 → 서버 자동 기동
- 서버 기동 후 브라우저 `http://127.0.0.1:8765` 오픈
- 이미 서버 실행 상태 → 중복 서버 0개
- 잘못된 protocol command 차단
- 콘솔창 0개 또는 기존 Knowledge Library와 동등 수준

### 6.2 Local Admin 실제 기능
자동 실행된 화면에서:
- Local Admin 로드
- YouTube URL 입력 UI 확인
- 기존 POST `/api/videos` 경로 정상
- 실제 콘텐츠 생성 기능을 깨뜨리지 않음

새 실제 영상 생성은 비용/시간이 불필요하면 생략 가능하나,
최소 health/catalog/API smoke test는 수행한다.
기존 실제 생성 PASS 증거를 재사용할 수 있다.

### 6.3 Skyview
- Owner Portal에서 버튼 표시
- `href="tony-shadowing://open"` 정확
- Email/Market/Invest/지식 도서관 기존 기능 회귀 없음
- 화면 폭에서 버튼 overflow/깨짐 없음
- private_reports / toss_reports 둘 다 확인

### 6.4 Any 독립 검증
Any가 Tody 구현 후 다음을 독립 확인:
- protocol 보안
- 중복 프로세스 방지
- launcher 실제 실행
- Skyview 버튼 연결
- 기존 기능 회귀 없음

---

## 7. GitHub / Local Sync
이번 작업은 두 repo를 다룬다.

### `tonykks/english-shadowing-agent`
- launcher/protocol 코드
- test/문서
- commit/push

### `tonykks/skyview-django`
- Owner Portal 버튼
- 관련 test
- commit/push

각 repo 작업 시작 전에:
- `git status`
- `git pull --ff-only`
- 로컬 미커밋 변경이 있으면 덮어쓰지 말고 중단 조건으로 보고

---

## 8. PythonAnywhere
Skyview 코드 반영 후,
현재 로그인 세션에 Browser MCP가 접근 가능하면:
1. PythonAnywhere Console
2. `cd ~/skyview-django`
3. `git pull --ff-only`
4. Web 탭 → Reload
5. Owner Portal에서 `영어 쉐도잉 🎧` 버튼 표시 확인

단, PythonAnywhere에서 protocol 버튼을 실제 클릭해도
`tony-shadowing://`은 **그 브라우저를 실행 중인 Owner PC**에서 처리되는 구조임을 유지한다.

로그인 세션 접근이 불가능하면 Owner에게 pull + Reload만 요청한다.

---

## 9. 성공조건

### PASS
- Skyview Owner Portal에 `영어 쉐도잉 🎧` 버튼 존재
- 클릭 시 `tony-shadowing://open`
- Windows protocol 등록 성공
- Local Admin 8765 자동 기동
- 이미 실행 중이면 중복 기동 없음
- 브라우저 자동 오픈
- 기존 Knowledge Library/Invest 버튼 회귀 없음
- 두 repo GitHub 반영
- 가능하면 PythonAnywhere 반영까지 완료

### BLOCKED
- 필수 Windows registry 권한/로컬 실행 권한 부재
- Owner PC repo 경로 불명확
- protocol 등록이 기존 앱과 충돌
- PythonAnywhere 로그인 세션 접근 불가
  - 이 경우 로컬/GitHub 작업은 완료하고 PythonAnywhere pull/reload만 Owner 조치로 남긴다.

---

## 10. 결과 기록
각 상세 증거는 다음에 기록:
- `skyview-django/handoffs/RESULT_20261004_SHADOWING_LOCAL_LAUNCH_INTEGRATION.md`

필요하면 english-shadowing-agent에도 간단한 RESULT/STATE를 갱신하되,
중복 문서는 만들지 않는다.

## 11. 채팅 보고 규칙
채팅에는 아래만:
1. 완료 상태
2. RESULT MD 링크
3. Skyview/PythonAnywhere 반영 여부
4. Owner가 처음 1회 해야 할 protocol 등록 조치가 남았으면 그것만
