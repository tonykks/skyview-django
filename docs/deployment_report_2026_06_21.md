# SkyView 프로젝트 — 배포 작업 보고서

| 항목 | 내용 |
|------|------|
| 작성일 | 2026-06-21 |
| 프로젝트 | Tony Skyview (Django + SQLite 드론 영상 포트폴리오) |
| GitHub | [tonykks/skyview-django](https://github.com/tonykks/skyview-django.git) |
| 운영 URL | https://skyview.pythonanywhere.com/ |
| PythonAnywhere | `skyview` |

---

## 1. 프로젝트 개요

### 목적

Google Apps Script + Spreadsheet 기반 SkyView를 Django + SQLite + Django Admin 구조로 이전한 드론 영상 포트폴리오 웹사이트.

### 운영 구조 (최종)

```
로컬 Cursor 개발
  → GitHub (Django 소스만)
  → PythonAnywhere (git clone / pull)
  → Reload
```

### 데이터 분리

| 위치 | 내용 |
|------|------|
| **GitHub** | 코드, templates, static 소스, migrations, `.env.example` |
| **GitHub 제외** | `db.sqlite3`, `.env`, `archive/`, `skyview.xlsx`, `staticfiles/`, `venv/` |
| **PythonAnywhere** | `db.sqlite3` + `.env` + `collectstatic` 결과(`staticfiles/`) |

---

## 2. 작업 타임라인 요약

### Phase 0 — 구조 분석 (코드 수정 없음)

- 전체 폴더/파일 구조 분석
- Django 필수 파일, static/template, media, db 위치 파악
- 삭제 후보·위험 파일·GitHub 제외 대상 정리
- `Skyview-Netflix/` 폴더는 복사본에 없음 (README에만 언급)

### Phase 1 — 운영용 로컬 구조 정리

- `archive/`로 레거시 이동 (`places/`, `images/`, 개발 문서, 미사용 static)
- `__pycache__` 삭제
- `.gitignore` 생성
- `archive/README.md` 추가

### Phase 2 — 보안·환경변수

- `settings.py`: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` → 환경변수 + `python-dotenv`
- `.env` (로컬) / `.env.example` (GitHub) 생성
- `requirements.txt`에 `python-dotenv` 추가

### Phase 3 — README 현행화

- 운영 구조, 포함/제외 목록, env, 실행·배포 흐름 반영

### Phase 4 — Release Test (로컬)

- `manage.py check` 통과
- 주요 URL 뷰 200 확인
- DB Place 28 / Video 121 확인

### Phase 5 — Git / GitHub

- `git init`
- 첫 commit: `39d2dea` (42 files)
- `STATIC_ROOT` 추가: `6657e72`
- push 완료 (`main`)

### Phase 6 — PythonAnywhere 배포

- `git clone` → `~/skyview-django`
- virtualenv: `skyview-django-313` (Python 3.13)
- Django 5.2.15 설치
- `.env`, `db.sqlite3` 업로드, `collectstatic`
- Web 탭 WSGI·Static 설정 → Reload
- https://skyview.pythonanywhere.com/ 정상 동작
- `changepassword admin`으로 Admin 로그인

### Phase 7 — Admin UI 이슈 (2026-06-21 발견)

- PA Admin 필터가 오른쪽이 아닌 위쪽에 표시
- Admin CSS Network 전부 200 (당시 static 404는 아닌 것으로 추정)
- 초기 추정: 반응형 breakpoint 또는 Django 버전 차이

### Phase 8 — Admin 필터 레이아웃 해결 (2026-06-22)

- **원인:** Django 6.0.6 업그레이드 후 `staticfiles/`에 5.2 시절 admin CSS 잔존 (6.0 HTML + 5.2 CSS)
- **해결:** `python manage.py collectstatic --clear --noinput` → Reload → Admin 정상 복구
- **상세 기록:** [troubleshooting.md — 사례 1](troubleshooting.md#사례-1-django-admin-필터가-오른쪽이-아닌-위쪽에-표시됨)

---

## 3. 최종 프로젝트 구조 (로컬)

```
skyview/
├── manage.py
├── requirements.txt
├── README.md
├── docs/
│   ├── deployment_report_2026_06_21.md   ← 본 문서
│   └── troubleshooting.md                ← 트러블슈팅 기록
├── .gitignore
├── .env.example
├── .env                          (gitignore)
├── db.sqlite3                    (gitignore)
├── skyview.xlsx                  (gitignore)
├── skyview_project/
├── skyview/
└── archive/                      (gitignore)
```

---

## 4. GitHub 저장소

### 포함 (약 42개 파일 + docs)

- Django 소스, templates, static 소스, migrations
- `requirements.txt`, `README.md`, `.gitignore`, `.env.example`

### 제외 (`.gitignore`)

- `db.sqlite3`, `.env`, `archive/`, `skyview.xlsx`
- `staticfiles/`, `__pycache__/`, `venv/`

### 커밋 이력 (보고서 작성 시점)

| Hash | Message |
|------|---------|
| `39d2dea` | Establish SkyView production-ready Django baseline |
| `6657e72` | Add STATIC_ROOT for PythonAnywhere collectstatic |

---

## 5. 환경변수 (`.env`)

| 변수 | 로컬 (개발) | PythonAnywhere (운영) |
|------|-------------|------------------------|
| `SECRET_KEY` | `.env` 파일 | `.env` 또는 Web 탭 env |
| `DEBUG` | `True` (기본) | `False` |
| `ALLOWED_HOSTS` | 빈값 또는 `localhost` | `skyview.pythonanywhere.com` |

> PA용 `SECRET_KEY`는 로컬과 **다른 새 키** 사용 권장.

---

## 6. PythonAnywhere 최종 설정

| 항목 | 경로 |
|------|------|
| 프로젝트 | `/home/skyview/skyview-django` |
| virtualenv | `/home/skyview/.virtualenvs/skyview-django-313` |
| DB | `/home/skyview/skyview-django/db.sqlite3` |
| static 수집 | `/home/skyview/skyview-django/staticfiles/` |

**Web 탭**

- Domain: `skyview.pythonanywhere.com`
- Static: URL `/static/` → Directory `.../staticfiles/`
- Python: 3.13

**WSGI** (`/var/www/skyview_pythonanywhere_com_wsgi.py`)

```python
path = "/home/skyview/skyview-django"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyview_project.settings")
application = get_wsgi_application()
```

---

## 7. 주요 URL

| URL | 설명 |
|-----|------|
| `/` | 메인 |
| `/videos/` | 16:9 Landscape |
| `/shorts/` | 9:16 Shorts |
| `/places/<slug>/` | 장소별 영상 |
| `/places/all/` | 전체 장소 + 지도 |
| `/about/` | About |
| `/maps/` | Leaflet 지도 |
| `/admin/` | Django Admin |

장소 `intro_url`: [GitHub Pages](https://tonykks.github.io/skyview/places/...) 외부 iframe

---

## 8. 배포·유지보수 절차

### 일상 업데이트

1. Cursor에서 코드 수정
2. `git commit` && `git push`
3. PA: `cd ~/skyview-django && workon skyview-django-313 && git pull`
4. (모델 변경 시) `python manage.py migrate`
5. (static 변경 시) `python manage.py collectstatic --noinput`
6. (**Django 업그레이드 시**) `python manage.py collectstatic --clear --noinput` — [사례 참고](troubleshooting.md)
7. Web 탭 → **Reload**

### DB 백업

- 주기적으로 PA Files 탭에서 `db.sqlite3` 다운로드 (GitHub에 없음)

### Excel 데이터 갱신

- `skyview.xlsx`를 PA에 일시 업로드 → `python manage.py import_skyview_excel`

---

## 9. 작업 중 이슈와 해결

| 이슈 | 해결 |
|------|------|
| 레거시 `places/`/`images/` 혼재 | `archive/`로 이동 |
| `SECRET_KEY` 하드코딩 | env + `.env.example` |
| PA에서 clone 전 `.env` 생성 | 순서 재정리 |
| `SECRET_KEY` 빈값 | `SECRET_KEY=$(...)` 후 `.env` 재작성 |
| Bash 여러 줄 `python -c` | 한 줄 명령으로 분리 |
| PA Admin 필터 위치 | `collectstatic --clear`로 5.2 CSS 잔존 제거 — [상세](troubleshooting.md) |
| `W042` warning | `DEFAULT_AUTO_FIELD` 미설정 — 무시 가능 |
| Admin ID/PW 모름 | `changepassword admin` |

---

## 10. Release Test 결과 (로컬)

- `manage.py check`: 이슈 없음
- 주요 URL: 200
- static: OK
- DB: Place 28, Video 121

---

## 11. 미완료·향후 선택 작업

- [ ] `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`
- [ ] `STATIC_URL = '/static/'`
- [ ] `requirements.txt` Django 버전 pin
- [x] PA Django 6.0.6 (런타임 확인됨, requirements pin은 미반영)
- [x] Admin 필터 레이아웃 — 2026-06-22 해결 ([troubleshooting.md](troubleshooting.md))
- [ ] README에 PA 배포 체크리스트 보강
- [ ] `db.sqlite3` 백업 루틴 문서화

---

## 12. 처음부터 계획했다면 하지 않아도 되었을 작업

다음 프로젝트 또는 동일 프로젝트를 처음부터 다시 한다면, 아래를 먼저 맞추면 재작업이 크게 줄어듭니다.

### 12.1 Python / Django 버전 통일

**실제 상황**

- 로컬: Python 3.14 + Django 6.x
- PA: Python 3.13 + Django 5.2.15 (`Django>=5.0`만 명시)

**결과**

- `W042` warning, Admin UI 차이, `collectstatic` 파일 수 차이

**처음부터**

1. PA 사용 가능 Python 버전 확인
2. 로컬 venv도 동일 major.minor
3. `requirements.txt` 예시:

```txt
Django>=6.0,<6.1
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

4. PA Web 탭 Python = venv Python 일치

### 12.2 배포 전 `settings.py` 한 번에 준비

- `SECRET_KEY` env 분리
- `STATIC_ROOT` 추가
- (권장) `STATIC_URL = '/static/'`
- (권장) `DEFAULT_AUTO_FIELD`

### 12.3 `.gitignore` · `.env.example` · README를 git init 전에 완성

### 12.4 `archive/` 분리를 삭제 검토 전에 역할 분리로 설계

- Django repo / GitHub Pages repo / 로컬 archive 3갈래

### 12.5 PythonAnywhere 배포 순서 고정

1. Web 앱 생성
2. `git clone`
3. `mkvirtualenv` (Python 버전 고정)
4. `pip install -r requirements.txt`
5. `.env` 생성 + `SECRET_KEY`
6. `python manage.py check`
7. `db.sqlite3` 업로드
8. `collectstatic --clear --noinput` (Django 업그레이드 시 필수)
9. Web: virtualenv, source, working dir, static, WSGI
10. Reload
11. `changepassword`

### 12.6 `db.sqlite3` 전략 사전 결정

- GitHub 제외, PA에서만 유지, 주기적 다운로드 백업

### 12.7 Release Test 체크리스트를 PA 배포 후에도 동일 적용

### 12.8 zip 업로드는 초기 이전용만, 이후 git pull only

---

## 13. 최종 상태 요약

| 상태 | 항목 |
|------|------|
| 완료 | 로컬 운영 구조, GitHub push, PA 배포, Admin 로그인 |
| 완료 | `db.sqlite3` PA 유지, `collectstatic`, static 매핑 |
| 완료 | Admin 필터 레이아웃 (2026-06-22, `collectstatic --clear`) |
| 보류 | `requirements.txt` Django 버전 pin, settings 정리 |

**운영 워크플로:** Cursor → GitHub → PA `git pull` → (migrate/collectstatic) → Reload

---

## 14. 참고 링크

| 항목 | URL |
|------|-----|
| GitHub | https://github.com/tonykks/skyview-django.git |
| 운영 사이트 | https://skyview.pythonanywhere.com/ |
| Admin | https://skyview.pythonanywhere.com/admin/ |
| GitHub Pages (장소 intro) | https://tonykks.github.io/skyview/places/... |

| 경로 | 위치 |
|------|------|
| 로컬 | `c:\Users\김광수\Desktop\skyview` |
| PA | `/home/skyview/skyview-django` |

---

*보고서 끝*
