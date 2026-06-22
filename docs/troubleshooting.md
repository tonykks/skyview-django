# SkyView — 트러블슈팅 기록

운영 중 발생한 이슈와 진단·해결 과정을 기록합니다.

| 항목 | 내용 |
|------|------|
| 관련 문서 | [배포 작업 보고서 (2026-06-21)](deployment_report_2026_06_21.md) |
| 운영 URL | https://skyview.pythonanywhere.com/ |

---

## 사례 1: Django Admin 필터가 오른쪽이 아닌 위쪽에 표시됨

| 항목 | 내용 |
|------|------|
| 발생일 | 2026-06-21 (배포 직후 발견) |
| 해결일 | 2026-06-22 |
| 환경 | PythonAnywhere `skyview`, Django 6.0.6, Python 3.13 |
| 상태 | **해결됨** |

### 문제 현상

- Django Admin changelist 화면에서 필터가 **오른쪽**에 있어야 하는데 **위쪽**으로 이동함.
- zip 업로드 방식(`kwangsookim.pythonanywhere.com`)에서는 정상인데, GitHub + PythonAnywhere 배포 구조(`skyview.pythonanywhere.com`)에서는 비정상적으로 보임.
- Admin CSS가 Network 탭에서 전부 **200**으로 보여, 처음에는 static 404 문제가 아닌 것으로 추정됨.
- 데이터·기능(Place 28, Video 121)은 정상 — **레이아웃(UI) 문제**에 한정됨.

### 초기 가설

| # | 가설 | 결과 |
|---|------|------|
| 1 | 브라우저 캐시 문제 | **기각** — 강력 새로고침 후에도 동일 |
| 2 | PythonAnywhere static mapping 문제 | **기각** — Live URL MD5 = staticfiles MD5 |
| 3 | Django 버전 불일치 (런타임 vs pip) | **기각** — 둘 다 6.0.6 |
| 4 | collectstatic 결과물이 pip 패키지와 불일치 | **확정** — MD5·파일 내용 불일치 확인 |

### 진단 과정

**원칙:** 가설 → 실험 → 반증 → 원인 확정

#### 1. Runtime Django 버전 확인

```bash
cd ~/skyview-django
workon skyview-django-313
python -c "import django; print('Django:', django.get_version())"
```

**결과:** `Django: 6.0.6`

#### 2. Package CSS와 staticfiles CSS 비교

```bash
PKG_CSS=$(python -c "import django, os; print(os.path.join(os.path.dirname(django.__file__), 'contrib/admin/static/admin/css/changelists.css'))")

echo "=== Package (pip) ==="
head -12 "$PKG_CSS"

echo "=== staticfiles ==="
head -12 staticfiles/admin/css/changelists.css
```

**결과 (수정 전):**

| 위치 | 파일 시작 패턴 |
|------|----------------|
| Package (pip) | `#changelist .changelist-form-container {` (Django **6.0** 구조) |
| staticfiles | `#changelist { display: flex; ...}` (Django **5.2** 구조) |

#### 3. 실제 Live URL CSS 비교

```bash
curl -s https://skyview.pythonanywhere.com/static/admin/css/changelists.css | head -12
```

**결과:** staticfiles와 **동일** (예전 5.2 CSS)

→ PythonAnywhere Web 탭 static 매핑(`/static/` → `~/skyview-django/staticfiles/`)은 **정상**이었음.

#### 4. MD5 비교

```bash
md5sum "$PKG_CSS" staticfiles/admin/css/changelists.css
curl -s https://skyview.pythonanywhere.com/static/admin/css/changelists.css | md5sum
```

**결과 (수정 전):**

```
Package CSS  ≠  staticfiles CSS  =  Live URL CSS
```

| 파일 | MD5 (수정 전) |
|------|----------------|
| Package (pip) | `dc127cbae4a6c96f012ef7e249115742` |
| staticfiles | `59465e72d1eff4750a62ea42d118e191` |
| Live URL | `59465e72d1eff4750a62ea42d118e191` |

### 원인

Django **6.0.6**으로 업그레이드한 후, 예전 Django **5.2** 시절의 admin CSS가 `staticfiles/` 안에 **남아 있었음**.

Django 5.2와 6.0은 Admin changelist **HTML 구조와 CSS 선택자가 다름**:

| | Django 5.2 | Django 6.0 |
|---|-----------|-----------|
| 필터 DOM 위치 | `#changelist` 형제 (테이블 아래) | `changelist-form-container` 내부 첫 번째 (테이블 위) |
| 레이아웃 CSS | `#changelist { display: flex }` | `.changelist-form-container { display: flex }` |

**6.0 HTML + 5.2 CSS** 조합으로 인해 Admin 필터가 위쪽으로 이동하는 현상이 발생.

`python manage.py collectstatic`(without `--clear`)만 실행하면 **기존 파일이 덮어쓰이지 않고 남을 수 있음**.

### 해결

```bash
cd ~/skyview-django
workon skyview-django-313

python manage.py collectstatic --clear --noinput
```

출력 예시: `133 static files deleted, 136 static files copied to '.../staticfiles'`

이후:

1. PythonAnywhere **Web 탭 → Reload**
2. Admin 페이지에서 **Ctrl+Shift+R** (강력 새로고침)

### 결과

**MD5 (수정 후):**

```
Package CSS  =  staticfiles CSS  =  Live URL CSS
```

세 파일 모두 `#changelist .changelist-form-container {`로 시작. Admin 필터가 **오른쪽**에 정상 표시됨.

### 교훈

1. **Django 업그레이드 후**에는 `collectstatic`만 실행하지 말고, 반드시 아래를 사용:

   ```bash
   python manage.py collectstatic --clear --noinput
   ```

   기존 `staticfiles/`를 완전히 비운 뒤 다시 생성해야 pip 패키지의 admin CSS와 일치함.

2. **CSS 200 응답 ≠ 올바른 CSS** — Network에서 200이어도 **파일 내용·버전**이 맞는지 확인해야 함.

3. **진단 시 비교 대상 3곳:**

   ```
   pip 패키지 CSS  vs  staticfiles CSS  vs  Live URL CSS
   ```

   Live URL = staticfiles이면 매핑은 정상. Package ≠ staticfiles이면 collectstatic 문제.

4. 문제 발생 시 **가설 → 실험 → 반증 → 원인 확정** 순서로 단계별 디버깅을 수행하는 것이 중요함.

### 빠른 진단 명령 (재사용)

```bash
cd ~/skyview-django
workon skyview-django-313

PKG_CSS=$(python -c "import django, os; print(os.path.join(os.path.dirname(django.__file__), 'contrib/admin/static/admin/css/changelists.css'))")

python -c "import django; print('Django:', django.get_version())"
head -5 "$PKG_CSS"
head -5 staticfiles/admin/css/changelists.css
curl -s https://skyview.pythonanywhere.com/static/admin/css/changelists.css | head -5
md5sum "$PKG_CSS" staticfiles/admin/css/changelists.css
curl -s https://skyview.pythonanywhere.com/static/admin/css/changelists.css | md5sum
```

세 MD5가 모두 같으면 static 동기화는 정상.

---

*추가 사례는 위 형식으로 이 문서에 누적합니다.*
