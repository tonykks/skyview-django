# Epilogue 시스템 (2026-06-23)

SkyView의 첫 Epilogue 구축 단계 기록입니다. Hero 에필로그 버튼으로 장소별 제작 에세이를 popup으로 보여줍니다.

---

## 현재 구조 (요약)

```
content/epilogues/{slug}.md     ← 원본 (Git 관리)
        ↓
skyview/epilogue.py             ← loader (md → HTML)
        ↓
┌─────────────────────────────────────────────────────┐
│ 직접 URL: /places/{slug}/epilogue/                  │  Django 렌더 (북마크·검증용)
│ popup URL: /places/{slug}/epilogue/popup/           │  정적 HTML 파일 제공 (iframe용)
└─────────────────────────────────────────────────────┘
        ↑
Hero [▶ 에필로그] → epilogue.js → #epilogue-modal (iframe)
```

---

## Hero 에필로그 버튼

- **768px 이상:** 썸네일 overlay 좌 `▶ 재생` / 우 `▶ 에필로그`
- **767px 이하:** overlay 2행 — 1행 제목, 2행 재생 | 에필로그
- 재생: `lightbox.js` + `data-youtube-id` (썸네일 전체 클릭 아님)
- 에필로그: `data-epilogue-url` → popup modal

Place 연결: `hero_video.place` 우선, 없으면 `featured_place`(default_place).

---

## Popup 구조

Place 소개 popup(`intro-modal` + 외부 `intro_url`)과 **UX는 유사**, 구현은 다릅니다.

| | Place 소개 | Epilogue popup |
|---|-----------|----------------|
| 콘텐츠 | 외부 HTML (`intro_url`) | 프로젝트 내 정적 HTML |
| iframe 대상 | GitHub Pages 등 | `/places/{slug}/epilogue/popup/` |
| X-Frame-Options | 외부 정책 | `SAMEORIGIN` (view에서 허용) |

Django가 렌더한 `/places/{slug}/epilogue/`는 `X-Frame-Options: DENY`라 **iframe에 넣을 수 없음**. popup 전용 URL이 정적 HTML 파일을 읽어 제공합니다.

관련 파일:

- `skyview/templates/skyview/includes/epilogue_modal.html`
- `skyview/static/skyview/js/epilogue.js`
- `skyview/views.py` → `place_epilogue_popup`

---

## 콘텐츠 파일 위치

| 용도 | 경로 |
|------|------|
| **md 원본** | `content/epilogues/{slug}.md` |
| **popup용 정적 HTML** | `skyview/static/skyview/epilogues/{slug}.html` |
| **설정** | `settings.EPILOGUE_CONTENT_DIR` |

md 첫 줄 = 페이지 제목, 이후 본문. `1.` `2.` … 로 시작하는 줄은 섹션 제목(`h2`)으로 변환됩니다.

---

## 정적 HTML 재생성

md 수정 후 popup HTML을 맞추려면:

```bash
python scripts/generate_epilogue_static.py
```

- md + `epilogue.py` loader 결과를 바탕으로 `섶섬.html` 등을 덮어씁니다.
- **이중 관리:** 직접 URL(Django/md)과 popup(정적 HTML)이 당분간 별도입니다. DB 자동화 단계에서 통합 예정.

---

## 관련 영상 (현재)

- **popup(정적 HTML):** 썸네일 카드 클릭 → YouTube **새 탭** (`card--link`)
- **직접 URL(Django):** `card--playable` + lightbox (동일 사이트)

lightbox를 popup iframe 안에 통합하지 않음 — DB 자동화·fragment 방식 검토 시 재논의.

---

## 향후 방향

1. Place DB / Admin에서 Epilogue 본문 관리
2. md·정적 HTML 이중 관리 제거
3. fetch + fragment 또는 단일 렌더 파이프라인 검토
4. Place detail 타이틀 → Epilogue popup 연결 (선택)

---

## 배포 시

```bash
git pull
pip install -r requirements.txt    # markdown 패키지 포함
python manage.py collectstatic --noinput
# Reload
```

`content/epilogues/`와 `skyview/static/skyview/epilogues/` 모두 저장소에 포함되어야 합니다.
