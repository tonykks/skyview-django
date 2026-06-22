# SkyView

제주 드론 영상 아카이브 **Tony Skyview** — Django + SQLite 기반 드론 영상 포트폴리오 웹사이트입니다.

기존 Google Apps Script + Spreadsheet 구조에서 Django + SQLite + Django Admin 구조로 이전한 프로젝트입니다.

---

## 현재 운영 구조

| 환경 | 역할 |
|------|------|
| **로컬 (Cursor)** | 개발·테스트 |
| **GitHub** | Django 소스 코드만 관리 |
| **PythonAnywhere** | `git pull` 후 Reload로 배포 |

- `db.sqlite3`는 GitHub에 올리지 않고, 로컬·서버 각각에서 별도 유지합니다.
- 장소 소개 HTML(`intro_url`)은 GitHub Pages 등 외부 URL을 사용합니다.

---

## GitHub에 포함되는 것

- Django 소스 코드 (`skyview/`, `skyview_project/`, `manage.py`)
- templates
- static 소스 (`skyview/static/`)
- migrations
- `requirements.txt`
- `.env.example`

---

## GitHub에서 제외되는 것

| 항목 | 이유 |
|------|------|
| `db.sqlite3` | 운영 데이터, 환경별로 다름 |
| `.env` | 비밀값 포함 |
| `archive/` | 레거시·백업 자료 |
| `skyview.xlsx` | import용, 런타임 미사용 |
| `staticfiles/` | `collectstatic` 결과물 |
| `__pycache__/` | Python 캐시 |
| `venv/` | 가상환경 |

---

## 환경변수

`settings.py`는 아래 환경변수를 읽습니다.

| 변수 | 설명 |
|------|------|
| `SECRET_KEY` | Django 비밀 키 (필수) |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | 쉼표로 구분 (예: `127.0.0.1,localhost`) |

로컬에서는 `.env.example`을 복사해 `.env`를 만들고 값을 채웁니다.

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

PythonAnywhere에서는 Web 탭 환경변수 또는 서버의 `.env` 파일로 설정합니다.

---

## 기본 실행 방법

```bash
pip install -r requirements.txt
copy .env.example .env    # Windows (macOS/Linux: cp .env.example .env)
# .env 에 SECRET_KEY 등 설정

python manage.py migrate
python manage.py runserver
```

브라우저: http://127.0.0.1:8000/

Admin 계정이 없으면:

```bash
python manage.py createsuperuser
```

---

## 배포 흐름

```
Cursor에서 수정
    → git commit / push
    → PythonAnywhere에서 git pull
    → (필요 시) migrate / collectstatic
    → Reload
```

---

## 문서

| 문서 | 설명 |
|------|------|
| [배포 보고서](docs/deployment_report_2026_06_21.md) | 배포 타임라인과 운영 절차 |
| [트러블슈팅 기록](docs/troubleshooting.md) | 운영 중 발생한 문제의 진단과 해결 기록 |

> Django 업그레이드 후에는 `python manage.py collectstatic --clear --noinput` 사용 권장

---

## 주요 URL

| URL | 설명 |
|-----|------|
| `/` | 메인 |
| `/videos/` | 16:9 Landscape 목록 |
| `/shorts/` | 9:16 Shorts 목록 |
| `/places/<slug>/` | 장소별 영상 |
| `/places/all/` | 전체 장소 + 지도 |
| `/about/` | About |
| `/admin/` | Django Admin |

---

© 2026 Tony Skyview — Drone Archive of Jeju
