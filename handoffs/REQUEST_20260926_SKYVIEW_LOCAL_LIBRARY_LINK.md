# REQUEST — Skyview Admin에서 로컬 지식 도서관 열기

- 날짜: 2026-09-26
- Owner 승인: Skyview의 기존 Admin 화면에 개인 전용 로컬 YouTube Knowledge Agent 링크 추가 및 운영 반영
- 대상 저장소: `tonykks/skyview-django`
- 연계 대상: `tonykks/youtube-knowledge-agent`의 현재 로컬 웹 UI
- 현재 운영 URL: `https://skyview.pythonanywhere.com/`

## 목적 및 사용 장면

Owner가 Skyview에 로그인하여 상단 `A`(Admin)를 클릭한 뒤 **「지식 도서관」** 버튼을 누르면, Owner 자신의 PC에서 실행 중인 YouTube Knowledge Agent의 기존 화면이 **새 브라우저 탭**으로 열린다. 그 화면에서 영상 URL을 등록하고 로컬에서 생성·검색·열람한다.

**중요:** 이는 로컬 웹앱으로 이동하는 링크일 뿐이다. PythonAnywhere에서 Agent를 실행하거나 콘텐츠를 서비스하는 작업이 아니다. GitHub에 영상 원본·자막·요약·번역·카탈로그·큐 등 로컬 실데이터를 Push하지 않는다. Public 배포, 공개용 도서관, 외부 사용자 생성 기능을 만들지 않는다.

## 구현 범위

1. Skyview의 현재 Owner 전용 Admin/Private Reports 화면 구조와 인증을 확인하고, 기존 메뉴 `H P L S ⓘ A` 및 Email/Market/Invest 등 기능을 유지하면서 눈에 띄는 **「지식 도서관」** 버튼/링크를 추가한다. 기존 상단 원형 메뉴에 새 버튼을 만들지 않는다.
2. 링크는 새 탭(`target="_blank"`)으로 열고 `rel="noopener noreferrer"`를 적용한다. Agent의 실제 로컬 실행 주소/포트를 해당 저장소의 실행 설정·문서로 확인하여 사용한다. 확인 전 임의 포트를 확정하지 않는다. `localhost` 또는 `127.0.0.1`은 **클릭한 사용자의 PC**를 가리킨다는 점을 유지한다.
3. 버튼은 Owner 인증 화면에만 표시한다. 공개 페이지에서 로컬 서비스가 제공되는 것처럼 안내하지 않는다. 서버 측에서 로컬 Agent로 요청을 프록시하거나 외부 공개 포트를 열지 않는다.
4. 로컬 서버 미실행 시 연결 실패할 수 있음을 짧게 안내한다. 브라우저의 HTTPS→로컬 HTTP 이동 제한이 발생하면 실제 환경에서 확인하고 안전한 대안을 보고한다. 로컬 Agent의 기능·데이터는 변경하지 않는다.
5. Skyview 로컬 테스트 후 GitHub Private 코드/협업 문서만 Commit/Push한다. PythonAnywhere는 자동 배포가 아니므로 **운영 서버의 git pull 및 Web Reload가 별도로 필요**하다. 원격 접근 권한이 없다면 완료로 가장하지 말고 Owner용 정확한 명령과 Reload 절차를 결과에 기록한다.
6. 운영 반영 후 Owner 로그인 상태에서 버튼 표시·새 탭 목적지·기존 메뉴/보고서 정상 여부를 확인한다. 실제 로컬 Agent 연결은 Owner PC에서만 검증할 수 있으므로 실행하지 않았다면 미검증으로 명시한다.

## 결과 기록

`handoffs/RESULT_20260926_SKYVIEW_LOCAL_LIBRARY_LINK.md` 및 해당 프로젝트의 상태 문서에 실제 링크 주소, 수정 파일, 검증 범위, 배포 상태, 커밋 SHA, Owner가 해야 할 작업(있다면)을 기록한다. 채팅에는 통합 결과와 중요한 제한사항만 간단히 보고한다.
