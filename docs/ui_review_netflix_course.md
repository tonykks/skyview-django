# Netflix 강의 UI 검토 — Skyview 반영 참고 (2026-07-05)

React 강의(Netflix 클론)와 현재 Skyview(Django)를 비교·검토한 내용입니다.  
**전면 개편·UI 개선을 검토할 때** 이 문서를 기준으로 삼습니다. 당장 구현을 전제하지 않습니다.

---

## 참고 링크

| 항목 | URL |
|------|-----|
| 강사 GitHub | https://github.com/jaewonhimnae/react-netflix |
| 강사 배포 사이트 | https://jaewonhimnae.github.io/react-netflix/ |
| 로컬 비교 폴더 (GitHub 다운로드) | `react-netflix-main/` |
| 로컬 비교 폴더 (강의교안) | `react-netflix-app/` |

---

## 검토 배경

- Skyview는 Netflix **UI 패턴**을 참고했으나, 스택은 **Django + 템플릿 + CSS/JS**입니다.
- React 강의에서 Swiper, Styled Components 등으로 UI를 다듬는 방법을 배웠고, **React 없이도 반영 가능한지**를 확인하는 것이 목적이었습니다.
- 2026-07-05 Row 화살표를 급히 적용했다가 **동작·설계 미완**으로 판단, **로컬 변경은 전부 되돌림**. 운영(PythonAnywhere)에는 미배포.

---

## `react-netflix-main` vs `react-netflix-app`

### 결론

**실제 UI·기능 소스는 거의 동일**합니다. 차이는 환경·교안용 부가 파일 위주입니다.

| 항목 | `react-netflix-main` (GitHub) | `react-netflix-app` (강의교안) |
|------|------------------------------|-------------------------------|
| 용량 (node_modules 제외) | 약 0.53MB | 약 1.59MB |
| React | 17 | 18 |
| react-scripts | 5.0.0 | 5.0.1 |
| `yarn.lock` | 없음 | 있음 (약 430KB) |
| `package-lock.json` | 약 490KB | 약 1.15MB |
| `gh-pages` | package.json에 없음 | dependencies에 포함 |
| `Row.js` | Swiper만 사용 | Swiper + **예전 slider 코드 주석** (~45줄) |
| `index.js` | React 17 `ReactDOM.render` | React 18 `createRoot` + StrictMode |

### 용량 차이 이유

1. **`yarn.lock`** — 교안 폴더에만 존재
2. **`package-lock.json`** — React·testing-library 버전 차이로 의존성 트리 크기 상이
3. **교안 `Row.js` 주석** — Swiper 도입 전 수동 slider 예제가 주석으로 남음
4. **`gh-pages` 패키지** — 교안 쪽에만 명시

`npm install` 후 `node_modules`는 수백 MB까지 커지나, 이는 **설치본**이며 소스 폴더 용량과는 별개입니다.

---

## 강의에서 UI를 세련되게 만든 핵심 기법

### 1. Swiper — Row 캐러셀 (마지막 강의 핵심)

- `Navigation`, `Pagination`, `loop`, **breakpoint**별 `slidesPerView` / `slidesPerGroup`
- 화면 너비에 따라 한 번에 보이는 포스터 수 자동 조절 (예: 1378px → 6개, 998px → 5개 …)
- 좌우 화살표·페이지네이션 내장

**Skyview와의 격차:** 그리드(데스크톱) + 태블릿 이하 가로 스크롤. Netflix식 Row 탐색 UX와 가장 차이가 큰 부분.

### 2. CSS 마이크로 인터랙션 — Row 포스터

- `transition: transform 450ms`
- hover 시 `scale(1.08)` / 대형 Row `scale(1.1)`
- Skyview에도 `scale(1.03)` hover 있음 → 방향은 유사, 강의 쪽이 transition·크기 조정이 더 Netflix스러움

### 3. Styled Components — Banner / Footer

- **Banner Play 후:** 전체 화면 iframe + `opacity: 0.65` 오버레이 (`styled-components`)
- **Footer:** 반응형 링크 그리드
- **Django 대안:** 동일 연출은 **일반 CSS**로 충분히 가능. Styled Components 필수 아님

### 4. Banner 하단 fade

- `banner--fadeBottom` — `linear-gradient`로 Hero → 아래 Row로 자연스럽게 연결
- Skyview Hero 캡션에도 그라데이션 있으나, **섹션 전체 하단 fade**는 강의 쪽이 더 Netflix에 가깝다

### 5. Nav — 스크롤 시 배경 변화

- `scrollY > 50` → `.nav__black` (어두운 배경)
- Skyview: sticky 헤더는 있으나 **스크롤 연동 시각 변화 없음**

### 6. MovieModal — 재생 전 미리보기

- 카드 클릭 → 모달(포스터, 줄거리, 평점) → (선택) 상세 페이지
- `fadeIn` + `scale` 애니메이션, `useOnClickOutside`로 바깥 클릭 닫기
- Skyview: 카드 클릭 → **바로 YouTube lightbox** (흐름이 다름)

### 7. Search — debounce + hover

- `useDebounce(500ms)`로 API 호출 최적화
- 검색 결과 hover `scale(1.25)`
- Skyview: **검색 기능 없음** → 체감 개선 폭이 가장 큰 후보

### 8. 예전 수동 slider (교재 단계)

- `Row.css` / 교안 `Row.js` 주석: hover 시 화살표, `scrollLeft ± (window.innerWidth - 80)`
- GitHub `main`은 Swiper만 사용. 교안은 **이전 단계 코드가 주석으로 보존**됨

### 강의 코드에서 굳이 따라올 필요 없는 부분

- `console.log` 잔존
- `Nav.js` scroll listener `removeEventListener` 버그 가능
- `SwiperSlide`에 `key` prop 누락
- 접근성·로딩/에러 상태 부족

---

## Skyview vs 강의 Netflix — 비교표

| 영역 | 강의 Netflix | Skyview (현재) |
|------|-------------|----------------|
| Row 탐색 | Swiper (화살표·페이지·loop·breakpoint) | 그리드 / 모바일 가로 스크롤 |
| Hero | 랜덤 배경 + Play 시 전체화면 영상 | 대표 영상 + 재생/에필로그 (고유) |
| 카드 클릭 | Modal → 상세 | Lightbox 즉시 재생 |
| 검색 | debounce 검색 | 없음 |
| Nav | 스크롤 시 배경 변화 | 원형 메뉴 (브랜드 고유) |
| Modal 애니메이션 | fadeIn + scale | lightbox / epilogue |
| 접근성 | 약함 | aria, 키보드 등 **우수** |
| 콘텐츠·운영 | TMDB API 데모 | Django Admin, 장소, 에필로그, Shorts |

**강의가 세련해 보이는 이유:** React 자체보다 **Swiper + transition + fade + scroll Nav + Modal + Search**가 한 세트로 맞춰져 있기 때문.

**Skyview가 앞선 부분:** 운영 구조, 에필로그, 장소·지도, 16:9/9:16, 접근성, 실제 콘텐츠 관리.

---

## React 없이 반영 가능한가?

**가능합니다.** UI 패턴만 옮기면 Django + CSS + JS로 충분합니다.

| 강의 기법 | Skyview 적용 방법 |
|-----------|------------------|
| Swiper | CDN 또는 정적 파일로 vanilla JS 연동 |
| hover scale / transition | `styles.css` |
| Banner fade | CSS gradient |
| Nav scroll 효과 | 짧은 JS |
| Modal 미리보기 | `lightbox.js` / `epilogue.js` 패턴 확장 |
| Search debounce | Django view + JS debounce |
| Styled Components | **불필요** — CSS로 대체 |

React 전환은 **컴포넌트·상태·라우팅이 많은 SPA**에 유리하나, Skyview는 Django Admin·DB·운영이 잡혀 있어 **전면 React 전환은 비용·리스크 큼**.

---

## 권장 반영 우선순위 (검토용)

| 순서 | 항목 | 체감 | Django만 가능 | 비고 |
|------|------|------|---------------|------|
| 0 | **목표·기준 정하기** | — | — | 추천 Row 규칙, 검색 범위 등 |
| 1 | **Git 브랜치 + 로컬 검증** | — | — | main = 안정, 실험은 브랜치 |
| 2 | **검색** | 매우 큼 | ✅ | 설계가 비교적 명확 |
| 3 | **Swiper Row** | 큼 | ✅ | 전체 목록(`/videos/`, `/shorts/`), 장소별 |
| 4 | **카드 hover / transition** | 중 | ✅ | 낮은 리스크 |
| 5 | **Hero 하단 fade** | 중 | ✅ | |
| 6 | **Nav scroll 배경** | 작음 | ✅ | |
| 7 | **미리보기 Modal** | 중 | ✅ | |
| 8 | **Banner 인라인 autoplay** | 선택 | ✅ | lightbox가 더 깔끔할 수 있음 |

### 보류·주의 구간

| 구간 | 이유 |
|------|------|
| **추천 Row** (홈 5/7 고정) | `display_rank` 수동 큐레이션. Swiper·화살표는 **우선순위·자동화 기준** 정한 뒤 |
| **Row 화살표만 단독 추가** (2026-07 시도) | Row마다 영상 개수·비율·넘침 조건이 달라 **설계 없이 붙이기 어려움**. 되돌림 완료 |
| **PythonAnywhere 배포** | 로컬에서 충분히 확인 후 |

---

## Row 화살표 시도에서 배운 점 (2026-07-05)

- 홈 **추천**: 5 Landscape + 7 Shorts 고정 → 데스크톱에서 **넘침 없음** → 화살표 의미 없음
- 홈 **최신·장소별**: 역시 개수 제한(5 등)이면 데스크톱에서 화살표가 안 보이거나 효과 미미
- **`/videos/`, `/shorts/`** (전체 목록): 영상 많을 때 Swiper/화살표 **효과 큼**
- 강의 Swiper는 **고정 개수 그리드가 아니라** 항상 넘치는 Row 전제
- 화살표는 강의에서도 **Row hover 시** 표시되는 경우가 많음 (수동 slider 단계)

---

## 개발·운영 환경 참고

| 환경 | DB | 비고 |
|------|-----|------|
| 로컬 | `db.sqlite3` | PythonAnywhere Admin 데이터와 **자동 동기화 안 됨** |
| PythonAnywhere | 서버 DB | Admin 입력이 **운영 사이트에 반영** |

- UI/CSS/JS 작업: 로컬 DB가 달라도 **대부분 문제 없음**
- 검색·에필로그·실데이터 QA: 로컬 DB 맞추거나 테스트 데이터 필요
- 권장 흐름: **로컬(브랜치) → 검증 → push → PythonAnywhere pull → Reload**

### Git 브랜치 백업 (권장)

```powershell
cd "c:\Users\김광수\Desktop\skyview_final"
git status
git checkout -b feature/기능이름
# 작업 후
git add ...
git commit -m "..."
# 마음에 안 들면
git checkout main
```

---

## 개편 시작 전에 정하면 좋은 것

1. **가장 Netflix스럽게 바꾸고 싶은 화면 1~2개** (예: `/videos/` Row, Hero, 검색)
2. **React 전환 의사** — Django 유지 vs 프론트만 분리
3. **추천 Row 규칙** — 수동 `display_rank` 유지 vs 조회수 등 자동화
4. **모바일 vs PC** 중 우선 UX
5. 강사 배포 사이트에서 **특히 마음에 드는 화면** (스크린샷)

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| [README.md](../README.md) | 실행·배포·환경변수 |
| [deployment_report_2026_06_21.md](deployment_report_2026_06_21.md) | 배포 타임라인 |
| [epilogue.md](epilogue.md) | 에필로그 시스템 |
| [troubleshooting.md](troubleshooting.md) | 운영 트러블슈팅 |

---

*작성: 2026-07-05 — Cursor 검토 대화 기반. 구현 결정 시 이 문서를 업데이트할 것.*
