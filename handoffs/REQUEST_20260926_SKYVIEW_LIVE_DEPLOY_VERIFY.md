# Skyview 운영 배포 반영 및 실화면 검증 요청

- 대상: `tonykks/skyview-django` (별도 YouTube Agent 저장소 아님)
- Owner 승인: 기존 메뉴 변경을 운영 웹사이트에 반영하고 실제 화면에서 검증하는 범위. 기존 서비스·데이터 보존.
- 기준 수정 커밋: `e6269d7b509b046a9aaca0cd3da19bb5c6c4984d`
- 현재 증상: GitHub main에는 `H P L S ⓘ A` 수정이 있으나 Owner의 Skyview 운영 화면에는 여전히 `H P L S A M` 표시.

## 지니에게 위임하는 작업

1. Skyview 실제 운영 URL과 배포 환경/연결 브랜치/실제 배포 커밋을 확인하여 코드 Push와 운영 반영 상태를 구분한다.
2. 승인된 기존 배포 절차에 따라 해당 메뉴 변경을 운영에 반영한다. 필요한 경우 재배포한다. 새로운 서비스나 공개 범위 변경은 하지 않는다.
3. 캐시 문제 가능성까지 확인하되 캐시라고 추정만 하지 말고 **실제 운영 URL의 브라우저 화면**에서 로그인 Owner 상태의 메뉴 `H P L S ⓘ A`를 검증한다. 비로그인 상태에서도 마지막 버튼이 Admin `A`인지, About `ⓘ` 링크와 Admin 링크가 기존 목적지로 정상 작동하는지 확인한다.
4. 기존 Email Agent Portal, 보고서, 인증, 데이터 및 나머지 메뉴 기능을 보존한다. YouTube 콘텐츠·로컬 데이터에는 접근/변경하지 않는다.
5. 배포 실패나 권한 부재 등 실제 차단 사유가 있으면 실패를 PASS로 보고하지 말고 원인과 Owner가 해야 할 결정 한 가지만 명시한다.

## 완료 Evidence

운영 URL, 실제 배포된 commit SHA, 배포 시각/상태, 운영 브라우저 확인 결과(가능하면 캡처), 기능 회귀 여부를 `handoffs/RESULT_20260926_SKYVIEW_LIVE_DEPLOY_VERIFY.md`에 기록하고 `agent-collab-kit/STATE.md`를 최신화한다. GitHub commit/push 후 채팅에는 완료 상태·RESULT 링크·실제 운영 확인 결과만 간단히 보고한다.
