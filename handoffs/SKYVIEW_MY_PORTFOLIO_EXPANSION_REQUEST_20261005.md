# Skyview My Portfolio 메뉴 전환 및 Portfolio Site 2개 추가 작업지시

## 목적
Skyview 상단의 기존 **Family Sites** 메뉴를 **My Portfolio**로 변경하고,
Owner가 확정한 Portfolio Site 2개를 추가한다.

이번 작업은 기존 Family Sites 기능을 새로 설계하는 작업이 아니라,
현재 정상 동작 중인 목록/정렬 구조를 유지한 채 **표시명 변경 + 항목 2개 추가 + 순서 확정**만 수행한다.

## Owner 확정사항

### 1. 메뉴명 변경
- 기존: `Family Sites`
- 변경: `My Portfolio`

### 2. 최종 표시 항목과 순서
아래 순서를 정확히 유지한다.

1. `Knowledge Library`
2. `English Shadowing`
3. `Vibe Coding Guide`
4. `Pet-Friendly Jeju`
5. `Hallim Youth English`

### 3. 새로 추가할 2개 사이트

#### Vibe Coding Guide
- 표시명: `Vibe Coding Guide`
- URL: `https://tonykks.github.io/career-pathfinder-app-b/`
- 성격: 초·중등 학생용 Vibe Coding 수업 교안을 기반으로 하되,
  성인에게도 원하는 것을 AI와 함께 기획하고 구현하는 전체 과정을 보여주는 Portfolio 콘텐츠.

#### Pet-Friendly Jeju
- 표시명: `Pet-Friendly Jeju`
- URL: `https://tonykks.github.io/DANGJEJU_2/`
- 성격: 제주 반려동물 동반 여행 Web App 팀 프로젝트.
  Owner는 DB 및 사용자 기능 관련 부분에 참여했으며, Portfolio 가치가 있어 포함한다.

### 4. Hallim Youth English 고정 규칙
- 기존에 구현된 **`Hallim Youth English` 항상 마지막 배치 규칙은 절대 제거하거나 약화하지 않는다.**
- 앞으로 다른 Portfolio Site가 추가되어도 계속 마지막에 표시되어야 한다.
- 이번 작업에서는 기존 정렬 로직을 재설계하지 말고 현재 고정 규칙을 그대로 보존한다.

## 변경 범위

현재 구현을 먼저 읽고 실제 Source of Truth를 확인한 뒤 최소 수정한다.

우선 확인할 파일/영역:

1. `skyview/views.py`
   - 기존 `_family_sites` 또는 동일 목적의 목록 구성/정렬 로직
   - `Hallim Youth English` 마지막 고정 로직 보존

2. `skyview/templates/skyview/base.html`
   - Dropdown 버튼의 `Family Sites` 표시명을 `My Portfolio`로 변경
   - 목록 렌더링 순서 확인
   - 기존 마지막 고정 처리 보존

3. `skyview/management/commands/import_skyview_excel.py`
   - 기존 `FAMILY_SITE_SEED_DATA` 또는 동일한 Seed Source가 실제 운영 데이터 생성에 사용되는지 확인
   - 사용 중이라면 신규 2개 항목을 Seed에 추가
   - 기존 정상 항목은 변경/삭제하지 않음

4. Family Site DB
   - 실제 운영 목록이 DB 기반이면 신규 2개 Site를 안전하게 추가
   - 동일 URL/동일 title 중복 생성 방지
   - 기존 3개 Site 레코드 보존

5. `skyview/tests.py`
   - 기존 `TestFamilySites` 또는 관련 테스트를 확장
   - 최종 5개 항목과 순서 검증
   - `Hallim Youth English`가 마지막인지 반드시 검증
   - Dropdown 버튼명이 `My Portfolio`인지 검증 가능하면 포함

## 구현 원칙
1. 기존 정상 동작하는 다음 기능은 건드리지 않는다.
   - Knowledge Library 링크
   - English Shadowing 링크 및 Local Launch 연동
   - Hallim Youth English 링크
   - Hallim Youth English 마지막 고정 규칙
   - 다른 Skyview 기능

2. 신규 2개 사이트는 일반 외부 HTTPS 링크로 연다.
   - `Vibe Coding Guide`
   - `Pet-Friendly Jeju`

3. 기존 Family Site 데이터 구조가 이미 재사용 가능하면 그대로 사용한다.
   - 별도 Portfolio 전용 Model을 새로 만들지 않는다.
   - DB migration은 꼭 필요한 경우가 아니면 만들지 않는다.

4. 단순 표시명 변경 때문에 내부 변수명/Model명까지 대규모 Rename하지 않는다.
   - 내부 코드의 `family_sites` 명칭은 기능상 문제가 없다면 유지 가능.
   - 사용자 화면에서 보이는 Label만 `My Portfolio`로 변경하면 충분하다.

## 지니 실행 흐름
1. 이 작업지시서를 읽고 Owner 요구사항을 자신의 말로 짧게 재정리해 **이해도 확인**을 먼저 남긴다.
2. 기존 코드와 데이터 흐름을 확인해 실제 수정 지점을 확정한다.
3. 필요한 수정만 수행한다.
4. Local test와 관련 회귀 테스트를 실행한다.
5. GitHub main에 commit/push 한다.
6. PythonAnywhere에 pull/reload 한다.
7. 실제 운영 사이트를 확인한다.
8. 최종 결과를 RESULT MD에 기록한다.

중간의 사소한 구현 선택은 Owner에게 다시 묻지 말고 승인된 범위에서 자율 진행한다.

## 검증

### Local
최종 Dropdown을 열어 아래 순서가 정확한지 확인한다.

1. Knowledge Library
2. English Shadowing
3. Vibe Coding Guide
4. Pet-Friendly Jeju
5. Hallim Youth English

추가 확인:
- 버튼명: `My Portfolio`
- 5개 링크 모두 정상
- `Hallim Youth English` 마지막
- 기존 English Shadowing Local Launch 기능 영향 없음
- 다른 Skyview 메뉴/페이지 회귀 없음

### GitHub / PythonAnywhere
기존 Skyview 배포 절차를 그대로 사용한다.

1. Local test PASS
2. 변경사항 commit
3. GitHub `main` push
4. PythonAnywhere:
   - `cd ~/skyview-django`
   - `git pull --ff-only`
   - Web App Reload
5. `https://skyview.pythonanywhere.com/` 실운영 화면에서 최종 검증

## 성공조건
- [ ] 상단 Dropdown 이름이 `My Portfolio`
- [ ] `Knowledge Library` 정상
- [ ] `English Shadowing` 정상
- [ ] `Vibe Coding Guide` 추가 및 URL 정상
- [ ] `Pet-Friendly Jeju` 추가 및 URL 정상
- [ ] `Hallim Youth English` 정상
- [ ] 표시 순서가 Owner 확정 순서와 일치
- [ ] `Hallim Youth English` 항상 마지막 고정 규칙 보존
- [ ] 기존 English Shadowing Local Launch 기능 영향 없음
- [ ] 전체 관련 Test PASS
- [ ] GitHub 반영
- [ ] PythonAnywhere Pull/Reload
- [ ] 실운영 화면 검증

## 결과 기록
작업 완료 후 다음 파일을 작성한다.

`handoffs/RESULT_20261005_SKYVIEW_MY_PORTFOLIO_EXPANSION.md`

결과 보고에는 최소한 다음을 포함한다.
1. 실제 수정 파일
2. 최종 메뉴 순서
3. 테스트 결과
4. Git commit SHA
5. PythonAnywhere 반영 여부
6. 실운영 화면 검증 결과
7. 알려진 제한사항이 있으면 해당 내용

## 채팅 보고
채팅에는 길게 설명하지 말고 다음만 보고한다.
1. 완료 상태
2. RESULT MD 링크
3. 최종 5개 메뉴 순서
4. PythonAnywhere 실운영 반영 여부
5. Owner 수동 조치가 남았으면 그것 한 가지
