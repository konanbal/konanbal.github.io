# 📈 주식 리서치 허브 (Stock Research Hub)

한국·미국 주식 일일 시황, 개별 종목 분석, 주간 금융 뉴스레터를 날짜별로 정리해 한눈에 조회할 수 있는 정적 웹사이트입니다.

---

## 🌐 웹사이트 개요

| 항목 | 내용 |
|------|------|
| 유형 | 정적 HTML 사이트 (서버 불필요) |
| 진입점 | `index.html` |
| 데이터 소스 | `manifest.js` (자동 생성) |
| 업데이트 방법 | HTML 파일 추가 후 `python update_manifest.py` 실행 |

**4개 섹션으로 구성됩니다:**

- 🇰🇷 **한국 주식 일일 리포트** — KOSPI/KOSDAQ 장 마감 특징주 정리
- 🇺🇸 **미국 주식 일일 리포트** — NASDAQ/NYSE 장 마감 특징주 정리
- 📊 **개별 종목 리포트** — 특정 종목 심층 분석 리포트
- 📰 **주간 금융 뉴스레터** — 주간 시황 요약 뉴스레터

---

## 📁 폴더 구조

```
homepage/
├── index.html                  # 메인 허브 페이지
├── manifest.js                 # 파일 목록 자동 생성 (수동 편집 금지)
├── update_manifest.py          # manifest.js 재생성 스크립트
├── generate_daily_html.py      # MD → HTML 변환 스크립트 (구형 워크플로우)
├── README.md                   # 이 문서
│
├── Kr_Daily_Report/            # 한국 주식 일일 리포트
│   ├── MD/                     # 원본 마크다운 소스
│   │   ├── blog_20260508_KR.md
│   │   └── blog_20260507_KR.md
│   ├── blog_20260508_KR.html   # 최종 HTML (index에 표시됨)
│   ├── blog_20260507_KR.html
│   └── ...
│
├── Us_Daily_Report/            # 미국 주식 일일 리포트
│   ├── MD/                     # 원본 마크다운 소스
│   │   ├── blog_20260508_US.md
│   │   └── blog_20260507_US.md
│   ├── blog_20260508_US.html
│   ├── blog_20260507_US.html
│   └── ...
│
├── Stock_Report/               # 개별 종목 리포트
│   ├── 한화시스템(272210)_report_20260509.html
│   └── ...
│
└── Weekly_Report/              # 주간 뉴스레터
    ├── newsletter_20260509.html
    └── ...
```

---

## 📄 파일 명명 규칙

### 한국·미국 일일 리포트

| 구분 | 파일명 패턴 | 예시 |
|------|------------|------|
| 신규 (단일 파일) | `blog_YYYYMMDD_KR.html` | `blog_20260508_KR.html` |
| 신규 (단일 파일) | `blog_YYYYMMDD_US.html` | `blog_20260508_US.html` |
| 구형 (대시보드) | `blog_YYYYMMDD_dashboard.html` | `blog_20260508_dashboard.html` |
| 구형 (포스트) | `blog_YYYYMMDD_post.html` | `blog_20260508_post.html` |

> `update_manifest.py`는 신규·구형 패턴을 모두 인식합니다. 같은 날짜에 두 형식이 혼재하면 신규 형식을 우선합니다.

### 종목 리포트

```
{종목명}({종목코드})_report_YYYYMMDD.html
예: 한화시스템(272210)_report_20260509.html
```

### 주간 뉴스레터

```
newsletter_YYYYMMDD.html
예: newsletter_20260509.html
```

### 원본 마크다운 (소스 보관용)

```
Kr_Daily_Report/MD/blog_YYYYMMDD_KR.md
Us_Daily_Report/MD/blog_YYYYMMDD_US.md
```

---

## 🔄 업데이트 방법

### A. 일일 리포트 추가 (신규 워크플로우 — 권장)

1. Claude Cowork 에서 **market-blog** 스킬로 엑셀 리포트 → MD 파일 생성
2. **blog-md-to-html** 스킬로 MD → `blog_YYYYMMDD_KR.html` / `blog_YYYYMMDD_US.html` 변환
3. 생성된 HTML을 각 폴더에 저장
   - 한국: `Kr_Daily_Report/`
   - 미국: `Us_Daily_Report/`
4. 원본 MD는 `MD/` 하위 폴더에 보관
5. **manifest 갱신 실행:**
   ```bash
   python update_manifest.py
   ```

### B. 일일 리포트 추가 (구형 워크플로우)

1. MD 파일을 `Kr_Daily_Report/MD/` 또는 `Us_Daily_Report/MD/` 에 저장
2. **HTML 변환 실행:**
   ```bash
   python generate_daily_html.py          # KR + US 전체
   python generate_daily_html.py KR       # 한국만
   python generate_daily_html.py US       # 미국만
   ```
   > `blog_YYYYMMDD_dashboard.html` + `blog_YYYYMMDD_post.html` 두 파일이 생성되며, 마지막에 `update_manifest.py`가 자동 실행됩니다.

### C. 종목 리포트 추가

1. Claude Cowork 에서 **stock-research** 스킬로 HTML 리포트 생성
2. 생성된 파일을 `Stock_Report/` 폴더에 저장
3. **manifest 갱신 실행:**
   ```bash
   python update_manifest.py
   ```

### D. 주간 뉴스레터 추가

1. Claude Cowork 에서 **weekly-finance-newsletter** 스킬로 HTML 생성
2. 생성된 파일을 `Weekly_Report/` 폴더에 저장
3. **manifest 갱신 실행:**
   ```bash
   python update_manifest.py
   ```

---

## 🛠 스크립트 설명

### `update_manifest.py`

각 폴더를 스캔해 `manifest.js`를 자동 생성합니다.

```bash
python update_manifest.py
```

**스캔 규칙:**

| 폴더 | 인식 패턴 |
|------|----------|
| `Kr_Daily_Report/` | `blog_*_KR.html` (우선), `blog_*_dashboard.html` (하위 호환) |
| `Us_Daily_Report/` | `blog_*_US.html` (우선), `blog_*_dashboard.html` (하위 호환) |
| `Stock_Report/` | `*.html` (수정일 기준 정렬) |
| `Weekly_Report/` | `*.html` (수정일 기준 정렬) |

생성 결과 예시:
```
----------------------------------------
  Kr_Daily_Report       :   4 items
  Us_Daily_Report       :   4 items
  Stock_Report          :   1 items
  Weekly_Report         :   1 items
----------------------------------------
```

---

### `generate_daily_html.py` (구형 변환기)

`MD/` 폴더의 마크다운을 파싱해 대시보드 + 포스트 HTML 두 파일을 생성합니다. 생성 후 `update_manifest.py`를 자동 호출합니다.

```bash
python generate_daily_html.py        # KR + US 전체
python generate_daily_html.py KR     # 한국 시장만
python generate_daily_html.py US     # 미국 시장만
```

> 현재 신규 워크플로우(blog-md-to-html 스킬)에서는 이 스크립트를 사용하지 않아도 됩니다.

---

### `manifest.js`

`index.html`이 로드하는 데이터 파일입니다. 직접 편집하지 말고 항상 `update_manifest.py`로 재생성하세요.

```js
window.SITE_MANIFEST = {
  "generated": "2026-05-10T...",
  "Kr_Daily_Report": [ { "date": "2026-05-08", "file": "blog_20260508_KR.html", ... }, ... ],
  "Us_Daily_Report": [ ... ],
  "Stock_Report":    [ ... ],
  "Weekly_Report":   [ ... ]
};
```

---

## ⚡ 빠른 참조 — 매일 하는 작업

```
새 리포트 파일 저장
       ↓
python update_manifest.py
       ↓
index.html 새로고침 → 확인
```

| 작업 | 명령어 |
|------|--------|
| manifest 갱신 | `python update_manifest.py` |
| MD → HTML 변환 (구형) | `python generate_daily_html.py` |
| 한국만 변환 (구형) | `python generate_daily_html.py KR` |
| 미국만 변환 (구형) | `python generate_daily_html.py US` |

---

## 📌 주의사항

- `manifest.js`는 **수동으로 편집하지 마세요.** `update_manifest.py`가 덮어씁니다.
- HTML 파일을 삭제하면 `update_manifest.py` 재실행 후 목록에서 사라집니다.
- 본 웹사이트의 주식 정보는 **참고용**이며 투자 권유가 아닙니다.

---

*마지막 업데이트: 2026-05-10*
