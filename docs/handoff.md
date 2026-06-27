# SkyView Handoff

> 이 문서는 현재 상태와 설계 의도를 기록하는 문서이다.
>
> 여기에 기록된 '향후 작업', '아이디어', '미구현 사항'은 구현 요청이 아니며, 사용자의 명시적인 지시가 있기 전까지는 코드를 수정하지 않는다.

새 Cursor 세션에서 **문맥을 이어가기 위한** 인계 문서입니다.  
구현 지시서가 아닙니다 — 코드 변경은 주인님이 명확히 요청했을 때만 진행합니다.

*마지막 갱신: 2026-06-27*

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **이름** | Tony SkyView — 제주 드론 영상 아카이브 |
| **스택** | Django 6.0 + SQLite + Django Admin |
| **로컬** | `c:\Users\김광수\Desktop\skyview` |
| **GitHub** | `https://github.com/tonykks/skyview-django.git` |
| **운영** | `https://skyview.pythonanywhere.com/` |
| **PA** | 계정 `skyview`, 경로 `~/skyview-django`, venv `workon skyview-django-313` |

---

## 협업 방식

- **주인님(토비)** — 방향·검토·최종 결정, ChatGPT 친구와 주로 논의
- **GPT 친구** — 요청사항 정리·가교
- **Cursor Agent (지니)** — 구현·분석; 더 나은 방향 있으면 의견 제시
- **commit/push** — 주인님이 명시적으로 요청할 때만 (임의 금지)
- **범위** — 최소 scope, 한 단계씩 검증, 모바일 안정성 우선

### handoff.md 사용 규칙

- 이 문서를 읽거나 갱신할 때는 **문맥·진행 상황만** 정리합니다.
- 문서에 적힌 내용을 보고 **임의로 구현을 시작하지 않습니다**.
- 다음 작업은 주인님이 검토 후 직접 지시합니다.

---

## Git 체크포인트 (최신)

| commit | 제목 | 의미 |
|--------|------|------|
| `fb6def8` | Add session handoff doc for context continuity | 본 handoff 문서 추가 |
| `ea893a5` | Add SkyView favicon and mobile touch icons | 탭·북마크·모바일 아이콘 |
| `33c862f` | Add first Epilogue system with Hero popup and docs | Epilogue 1단계 + Hero 연동 |
| `e36639a` | Refine hero section layout… | Hero 2분할·비율 안정 저장점 |

`main` = `origin/main` 동기화됨 (아이콘 push 완료, PA에서도 배포 확인됨).

### Untracked (의도적 미포함)

- `docs/screenshots/` — hero 반응형 캡처
- `scripts/capture_hero.py`
- `scripts/check_epilogue_headers.py`

---

## Hero 영역 (현재 기준점)

### 구조 (768px+)

- **2분할:** 왼쪽 제목+bullet / 오른쪽 16:9 썸네일
- **비율:** 960px+ → **42:58**, 768~959px → **40:60**
- **제목 (desktop):** `섶섬 - 고난과 인내가 만든 아름다움` (hardcoded `{% with %}`)
- **bullet (의미 강조형):**
  - 제주 서귀포 앞바다 — 파도와 바람을 견딘 섶섬
  - 시간과 인내 — 침묵이 빚은 풍경
  - 거친 포말 — 바위에 새겨진 세월
  - 아름다움 — 하루아침에 만들어지지 않은 결과

### 동작

| 요소 | 동작 |
|------|------|
| **▶ 재생** | `<button>` + `lightbox.js` (썸네일 전체 클릭 **없음**) |
| **▶ 에필로그** | `epilogue.js` → iframe popup |
| **767px 이하** | `hero-copy` 숨김; overlay **2행** (제목 / 재생\|에필로그) |

### 주요 파일

- `skyview/templates/skyview/index.html`
- `skyview/static/skyview/css/styles.css`
- `skyview/static/skyview/js/lightbox.js`

---

## Epilogue 시스템 (1단계 완료)

상세: [`docs/epilogue.md`](epilogue.md)

### 설계 의도 (중요)

Epilogue는 **섶섬이라는 장소 전체의 설명이 아닙니다.**  
현재 Hero **대표 영상**에 대한 제작 에세이이며, 진입점은 Hero의 **▶ 에필로그** 버튼뿐입니다.

- Place detail 페이지 타이틀·소개 popup과 **연결하지 않음** (의미가 달라짐)
- Place detail 타이틀 → 외부 `intro_url` 소개 popup (기존 동작 유지)

### 구조 요약

```
content/epilogues/{slug}.md          ← md 원본
        ↓ epilogue.py (loader)
┌──────────────────────────────────────────┐
│ /places/{slug}/epilogue/                 │  Django 직접 URL (북마크·검증·lightbox)
│ /places/{slug}/epilogue/popup/           │  정적 HTML iframe (SAMEORIGIN)
└──────────────────────────────────────────┘
        ↑ Hero [▶ 에필로그] 만
```

### popup이 정적 HTML인 이유

- Django 렌더 페이지는 `X-Frame-Options: DENY` → iframe 불가
- Place 소개 popup은 **외부** `intro_url`(GitHub Pages)이라 iframe 가능
- popup용: `skyview/static/skyview/epilogues/섶섬.html` + `place_epilogue_popup` view

### Hero Epilogue 연결

- Place slug: `hero_video.place` 우선, 없으면 `featured_place`
- `data-epilogue-url` = `build_absolute_uri` → `/places/섶섬/epilogue/popup/`

### 관련 영상

- **popup(정적 HTML):** YouTube **새 탭** (`card--link`)
- **직접 URL(Django):** `card--playable` + lightbox
- `← 섶섬 영상 보기` 링크는 **삭제됨** (iframe 내 DENY 이슈)

### md ↔ html 이중 관리

```bash
python scripts/generate_epilogue_static.py   # md 수정 후 popup HTML 재생성
```

### 주요 파일

- `skyview/epilogue.py`
- `skyview/views.py` (`place_epilogue`, `place_epilogue_popup`)
- `skyview/templates/skyview/includes/epilogue_modal.html`
- `skyview/static/skyview/js/epilogue.js`
- `scripts/generate_epilogue_static.py`

---

## Place detail (현재 동작)

- 타이틀 클릭 → `intro_url` 외부 소개 페이지를 **intro popup** (iframe)으로 표시
- **위치** 버튼 → 지도 modal
- Epilogue와 **무관**

주요 파일: `skyview/templates/skyview/place_detail.html`, `skyview/static/skyview/js/place.js`

---

## Favicon / 모바일 아이콘 (완료)

- **원본:** `skyview/static/skyview/images/icons/skyview-icon-master.png`
- **파생:** `favicon.ico`, `favicon-16/32.png`, `apple-touch-icon.png`, `icon-192/512.png`
- **템플릿:** `skyview/templates/skyview/includes/site_icons.html` → `base.html`, `epilogue.html`
- **미포함:** `maps.html` (독립 전체화면 템플릿, `base.html` 미사용)

- **manifest:** `skyview/static/skyview/site.webmanifest`
- **재생성:** `python scripts/generate_site_icons.py`

---

## PythonAnywhere 배포

```bash
cd ~/skyview-django
git pull
workon skyview-django-313
pip install -r requirements.txt          # markdown 등 변경 시
python manage.py migrate                 # migration 있을 때만
python manage.py collectstatic --noinput # static 변경 시 필수
# Web 탭 → Reload
```

- Django major upgrade 후: `collectstatic --clear --noinput`
- **`Reload`만으로는 부족** — `git pull` + `collectstatic` 필요

---

## 로컬 실행

```bash
cd c:\Users\김광수\Desktop\skyview
python manage.py runserver
# http://127.0.0.1:8000/
```

---

## 주요 URL

| URL | 설명 |
|-----|------|
| `/` | 메인 (Hero) |
| `/places/섶섬/epilogue/` | Epilogue 직접 (북마크·검증) |
| `/places/섶섬/epilogue/popup/` | Epilogue popup용 HTML (Hero iframe) |
| `/places/섶섬/` | 장소별 영상 |
| `/admin/` | Django Admin |

---

## 문서

| 파일 | 내용 |
|------|------|
| [`README.md`](../README.md) | 프로젝트 개요·배포 |
| [`docs/epilogue.md`](epilogue.md) | Epilogue 상세 |
| [`docs/troubleshooting.md`](troubleshooting.md) | Admin filter / collectstatic 등 |
| [`docs/deployment_report_2026_06_21.md`](deployment_report_2026_06_21.md) | 배포 기록 |

---

## 작업 규칙 (반복)

1. 최소 scope — **요청한 것만**
2. Hero desktop 수정 시 mobile 규칙 건드리지 않기 (필요 시 `@media`로 격리)
3. commit/push — 명시 요청 시만
4. `db.sqlite3` — GitHub 미포함
5. 단계별 검증 후 다음 단계
6. handoff 읽기/수정 ≠ 구현 착수
