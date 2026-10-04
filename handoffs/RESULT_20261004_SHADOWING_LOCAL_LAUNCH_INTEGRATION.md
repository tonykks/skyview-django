# RESULT: Shadowing Local Admin — Skyview 원클릭 실행 연동 보고서

- **작업 일시**: 2026-10-04 09:22 KST
- **작업지시서**: `handoffs/SHADOWING_LOCAL_LAUNCH_INTEGRATION_REQUEST_20261004.md`
- **대상 저장소**:
  1. `tonykks/english-shadowing-agent` (로컬 root: `c:\Users\김광수\Desktop\english-study-workspace\english-shadowing-agent`)
  2. `tonykks/skyview-django` (로컬 root: `c:\Users\김광수\Desktop\skyview_final`)
- **담당/모델**:
  - 구현 (Tody): GPT-6 Astra
  - 검증 (Ani): Gemini 3.7 Flash (High) 독립 검증
- **상태**: **구현, 로컬 테스트, GitHub Push, Windows Registry 등록, PythonAnywhere 동기화 및 실 사이트 검증 완료**

---

## 1. 구현 내용

### 1.1 `tonykks/english-shadowing-agent`
1. **Windows Silent Launcher (`scripts/shadowing_launcher.py`)**:
   - URL 프로토콜: `tony-shadowing://open`
   - 허용 명령: `open`만 엄격히 허용 (추가 인자, 디렉터리 경로 주입, 쉘 인젝션 차단)
   - 로컬 서버: `127.0.0.1:8765`
   - 이미 8765 포트가 활성화된 경우: 중복 기동 없이 브라우저 탭(`http://127.0.0.1:8765`)만 즉시 오픈
   - 8765 포트가 꺼져 있는 경우: `pythonw.exe run.py` 무음 백그라운드 프로세스 기동 (`SW_HIDE`, `CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP`, `DEVNULL` 표준 입출력 분리)
   - 최대 12초간 포트 연결 확인 후 브라우저 자동 오픈
2. **프로토콜 등록 스크립트 (`scripts/register_protocol.py` & `register_protocol.bat`)**:
   - `HKEY_CURRENT_USER\Software\Classes\tony-shadowing` 등록 (관리자 권한 불필요)
   - `pythonw.exe`를 우선 사용하여 검은 콘솔창 0개 보장
   - 원클릭 배치 파일 제공
3. **프로토콜 해제 스크립트 (`scripts/unregister_protocol.py` & `unregister_protocol.bat`)**:
   - `HKEY_CURRENT_USER\Software\Classes\tony-shadowing` 안전하게 재귀 삭제
4. **런처 단위 테스트 (`scripts/test_shadowing_launcher.py`)**:
   - URL 파싱 및 허용/거부 검증 (통과)
5. **서버 안정성 보강 (`backend/server.py`)**:
   - `pythonw.exe` 환경에서 `sys.stdout`/`sys.stderr`가 `None`일 때 발생하는 Flask/Werkzeug 예외 방지를 위해 `os.devnull` fallback 적용

### 1.2 `tonykks/skyview-django`
1. **Owner Portal 버튼 추가**:
   - `skyview/templates/skyview/private_reports.html`
   - `skyview/templates/skyview/toss_reports.html`
   - 버튼명: **`영어 쉐도잉 🎧`**
   - 링크: `href="tony-shadowing://open"`
   - 타이틀/aria-label: `내 PC English Shadowing Local Admin 자동 실행 (127.0.0.1:8765 서버 자동 시작 및 연결)`
2. **스타일링 (`.report-switch-btn.shadowing-btn`)**:
   - 기존 서비스 전환 버튼(`Email`, `Market`, `Invest ⚡`, `지식 도서관 📚`)과 일관된 높이/폰트/패딩 유지
   - Sky-Blue/Cyan 계열 테마 적용 (`color: #38bdf8; border-color: rgba(56, 189, 248, 0.35); hover: #7dd3fc, 0.15 background`)
3. **단위 테스트 (`skyview/tests.py`)**:
   - `TestShadowingLocalLaunchIntegration` 추가
   - `private_reports` 및 `toss_reports`에서 `tony-shadowing://open`, `영어 쉐도잉 🎧`, `.shadowing-btn` 노출 검증 완료 (총 45개 테스트 통과)

---

## 2. Ani 독립 검증 결과

1. **Protocol 보안 검증**:
   - `tony-shadowing://open` -> 정상 허용
   - `tony-shadowing:open` -> 정상 허용
   - `tony-shadowing://close`, `tony-shadowing://open/../../calc.exe`, `tony-shadowing://open;calc` -> 차단 (반환코드 1)
2. **Local Registry 등록 검증**:
   - `reg query HKCU\Software\Classes\tony-shadowing\shell\open\command` 확인 완료
3. **Skyview 버튼 연결 및 회귀 검증**:
   - `Email`, `Market`, `Invest ⚡`, `지식 도서관 📚` 기존 버튼 기능 및 링크 온전함 확인
   - `영어 쉐도잉 🎧` 버튼이 추가되어도 헤더 레이아웃 깨짐 없음

---

## 3. GitHub 및 PythonAnywhere 반영

1. **GitHub Push**:
   - `tonykks/english-shadowing-agent`: commit `513f795`
   - `tonykks/skyview-django`: commit `main`
2. **PythonAnywhere 반영 (Playwright 자동화)**:
   - Console `48281354`: `cd ~/skyview-django && git pull --ff-only`
   - Web App Setup: `skyview.pythonanywhere.com` Reload 완료
   - 실 사이트 확인 완료
