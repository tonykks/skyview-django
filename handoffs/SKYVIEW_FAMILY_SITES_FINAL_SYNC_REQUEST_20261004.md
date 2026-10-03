# Skyview Family Sites 정리 및 Local/PythonAnywhere 동기화 작업지시

## 목적
Skyview의 Family Sites 목록을 최종 정리하고, GitHub 원격과 Owner 로컬/PythonAnywhere 배포본의 상태를 일치시킨다.

## Owner 확정사항
1. Family Sites 목록에서 **English Study Site** 항목만 제거한다.
2. 기존 English Study Site 저장소/파일 자체는 삭제하지 않는다. 이번 작업은 **Skyview 목록에서 링크만 제거**하는 작업이다.
3. 현재 유지할 Family Sites:
   - Hallim Youth English
   - Knowledge Library
   - English Shadowing
4. 표시명은 위와 같이 짧게 유지한다.
5. 각 실제 사이트 내부의 정식 이름에는 Tony's 등의 기존 브랜딩을 그대로 유지한다.

## 작업 순서

### 1. 원격/로컬 상태 확인
- 대상 repo: `tonykks/skyview-django`
- Owner PC의 로컬 `skyview-django` checkout이 있다면:
  - `git status`
  - 로컬 미커밋 변경이 없는지 확인
  - 안전하면 `git pull --ff-only`
- GitHub 원격에 이미 반영된 Toby 변경사항을 로컬에 동기화한다.
- 로컬에 예상치 못한 미커밋 변경이 있으면 덮어쓰지 말고 중단 원인을 보고한다.

### 2. Family Sites 목록 수정
현재 Skyview에서 보이는 Family Sites 중 **English Study Site**를 제거한다.

중요:
- `Hallim Youth English` 유지
- `Knowledge Library` 유지
- `English Shadowing` 유지
- 링크 URL은 기존 정상 URL 그대로
- English Study Site repo나 서비스 자체를 삭제하지 않는다.

Family Sites가 DB `family_sites`에서 공급되는 항목이라면 실제 source를 찾아 해당 항목만 제거/비활성화한다.
템플릿에 하드코딩된 항목이면 해당 링크만 제거한다.
구현 편의상 다른 Family Site까지 재구성하지 않는다.

### 3. 검증
로컬 또는 테스트 환경에서 Family Sites dropdown을 확인:
- English Study Site 없음
- Hallim Youth English 있음
- Knowledge Library 있음
- English Shadowing 있음
- 링크 정상

### 4. GitHub 반영
- 변경 commit/push
- 기존 원격 변경과 충돌 없이 main 최신 상태 유지

### 5. PythonAnywhere 반영
Owner가 현재 `skyview.pythonanywhere.com`에 로그인되어 있다.

#### Browser MCP/Computer automation이 현재 로그인 세션에 접근 가능한 경우
지니가 직접:
1. PythonAnywhere Consoles로 이동
2. 사용 중인 Bash console을 열거나 새 console 사용
3. 아래 실행
   ```bash
   cd ~/skyview-django
   git status
   git pull --ff-only
   ```
4. PythonAnywhere Web 탭으로 이동
5. `skyview.pythonanywhere.com` 앱의 **Reload** 실행
6. 실제 사이트에서 Family Sites dropdown 검증

#### 로그인 세션에 접근할 수 없는 경우
- 로그인 우회/재인증을 시도하지 않는다.
- GitHub/로컬 변경까지만 완료하고,
- Owner에게 아래 수동 2단계만 요청한다:
  ```bash
  cd ~/skyview-django
  git pull --ff-only
  ```
  이후 Web 탭 → Reload.

### 6. 최종 성공조건
- Skyview Family Sites에서 English Study Site 제거
- 나머지 3개 정상
- Owner 로컬 checkout과 GitHub 원격 동기화
- 가능하면 PythonAnywhere까지 pull + Reload + 실제 화면 검증
- 기존 영어 사이트 저장소/파일은 삭제하지 않음

## 결과 기록
`handoffs/RESULT_20261004_SKYVIEW_FAMILY_SITES_FINAL_SYNC.md` 작성 및 commit.

## 채팅 보고
채팅에는 길게 쓰지 말고 다음만 보고:
1. 완료 상태
2. RESULT MD 링크
3. PythonAnywhere 실제 반영 여부
4. Owner 수동 조치가 남았으면 딱 그 한 가지
