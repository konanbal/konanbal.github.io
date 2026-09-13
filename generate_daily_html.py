#!/usr/bin/env python3
"""
generate_daily_html.py
MD 파일 → blog_{date}_dashboard.html + blog_{date}_post.html 변환기

사용법:
    python generate_daily_html.py           # 모든 MD 파일 일괄 처리
    python generate_daily_html.py KR        # 한국 시장만
    python generate_daily_html.py US        # 미국 시장만
"""

import re, sys, json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent

# ──────────────────────────────────────────────────────────
# 공통 유틸
# ──────────────────────────────────────────────────────────
def pct_color(pct_str):
    """등락률 문자열 → 색상 클래스"""
    try:
        v = float(re.sub(r'[^0-9.\-]', '', pct_str or '0'))
        if v > 0: return 'up'
        if v < 0: return 'down'
    except: pass
    return 'flat'

def pct_badge(pct_str):
    cls = pct_color(pct_str)
    sign = '+' if cls == 'up' else ''
    return f'<span class="badge {cls}">{sign}{pct_str}</span>'

def nav_html(date_fmt, market, dashboard_file, post_file, is_dashboard=True):
    other_file = post_file if is_dashboard else dashboard_file
    other_label = '📝 블로그 포스트' if is_dashboard else '📊 대시보드'
    flag = '🇰🇷' if market == 'KR' else '🇺🇸'
    market_label = '한국 시장' if market == 'KR' else '미국 시장'
    active_d = 'active' if is_dashboard else ''
    active_p = '' if is_dashboard else 'active'
    return f"""
<nav class="navbar">
  <div class="navbar-inner">
    <a href="../index.html" class="nav-logo">
      <div class="logo-icon">📈</div>
      주식 리서치 허브
    </a>
    <ul class="nav-links">
      <li><a href="../index.html"><span>🏠</span> 홈</a></li>
      <li><a href="../Kr_Daily_Report/" ><span>🇰🇷</span> 한국 주식</a></li>
      <li><a href="../Us_Daily_Report/"><span>🇺🇸</span> 미국 주식</a></li>
      <li><a href="../Stock_Report/"><span>📊</span> 종목 리포트</a></li>
      <li><a href="../Weekly_Report/"><span>📰</span> 주간 뉴스레터</a></li>
    </ul>
    <div class="nav-right">
      <a href="{dashboard_file}" class="nav-pill {active_d}">📊 대시보드</a>
      <a href="{post_file}" class="nav-pill {active_p}">📝 포스트</a>
    </div>
  </div>
</nav>"""

COMMON_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#1a56db;--primary-dark:#1239a0;--primary-light:#3b82f6;
  --navy:#0f2244;--navy-mid:#1e3a5f;--accent:#60a5fa;
  --up:#16a34a;--up-bg:#f0fdf4;--up-border:#bbf7d0;
  --down:#dc2626;--down-bg:#fff1f2;--down-border:#fecdd3;
  --flat:#64748b;--flat-bg:#f1f5f9;
  --bg:#f0f5fb;--card:#ffffff;--border:#dbe8f8;
  --text:#1e293b;--muted:#64748b;--light:#94a3b8;
  --radius:14px;--radius-sm:8px;
  --shadow:0 4px 20px rgba(26,86,219,.10);
  --transition:.22s cubic-bezier(.4,0,.2,1);
}
html{scroll-behavior:smooth}
body{font-family:'Apple SD Gothic Neo','Pretendard','Noto Sans KR',sans-serif;
     background:var(--bg);color:var(--text);min-height:100vh}
a{text-decoration:none;color:inherit}
table{border-collapse:collapse;width:100%}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--border);font-size:.85rem}
th{background:#f8faff;font-weight:700;color:var(--navy-mid);font-size:.8rem}
tr:last-child td{border-bottom:none}
tr:hover td{background:#f8faff}

/* Navbar */
.navbar{position:sticky;top:0;z-index:100;background:var(--navy);box-shadow:0 2px 12px rgba(0,0,0,.3)}
.navbar-inner{max-width:1280px;margin:0 auto;padding:0 24px;display:flex;align-items:center;gap:8px;height:60px}
.nav-logo{display:flex;align-items:center;gap:10px;color:#fff;font-size:1rem;font-weight:700;margin-right:12px}
.logo-icon{width:32px;height:32px;background:linear-gradient(135deg,var(--primary-light),var(--accent));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}
.nav-links{display:flex;align-items:center;gap:2px;list-style:none;flex:1}
.nav-links a{display:flex;align-items:center;gap:5px;padding:6px 12px;border-radius:7px;color:rgba(255,255,255,.72);font-size:.84rem;font-weight:500;transition:var(--transition)}
.nav-links a:hover{background:rgba(255,255,255,.12);color:#fff}
.nav-right{display:flex;gap:8px;margin-left:auto}
.nav-pill{padding:6px 14px;border-radius:20px;font-size:.8rem;font-weight:600;color:rgba(255,255,255,.65);border:1px solid rgba(255,255,255,.15);transition:var(--transition)}
.nav-pill:hover,.nav-pill.active{background:var(--primary);color:#fff;border-color:var(--primary)}

/* Badges */
.badge{display:inline-block;padding:2px 9px;border-radius:5px;font-size:.78rem;font-weight:700;letter-spacing:.3px}
.badge.up{background:var(--up-bg);color:var(--up);border:1px solid var(--up-border)}
.badge.down{background:var(--down-bg);color:var(--down);border:1px solid var(--down-border)}
.badge.flat{background:var(--flat-bg);color:var(--flat)}

/* Hero */
.hero{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-mid) 60%,#1a4070 100%);
      padding:40px 24px 36px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:380px;height:380px;
              background:radial-gradient(circle,rgba(59,130,246,.18) 0%,transparent 70%);pointer-events:none}
.hero-inner{max-width:1280px;margin:0 auto;position:relative;z-index:1}
.hero-eyebrow{display:inline-flex;align-items:center;gap:6px;background:rgba(96,165,250,.15);
              border:1px solid rgba(96,165,250,.3);color:var(--accent);font-size:.75rem;font-weight:700;
              padding:3px 11px;border-radius:20px;margin-bottom:12px;letter-spacing:.5px;text-transform:uppercase}
.hero-title{font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;color:#fff;line-height:1.25;letter-spacing:-.4px;margin-bottom:8px}
.hero-title span{background:linear-gradient(90deg,var(--accent),#a5f3fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{color:rgba(255,255,255,.55);font-size:.9rem}
.hero-actions{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:8px;font-size:.85rem;font-weight:600;transition:var(--transition);cursor:pointer;border:none}
.btn-primary{background:var(--primary);color:#fff}
.btn-primary:hover{background:var(--primary-dark)}
.btn-ghost{background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2)}
.btn-ghost:hover{background:rgba(255,255,255,.2)}

/* Main */
.main{max-width:1280px;margin:0 auto;padding:32px 24px 60px}
.section-title{font-size:1.05rem;font-weight:700;color:var(--text);display:flex;align-items:center;gap:8px;margin-bottom:16px}
.section-title::before{content:'';display:block;width:4px;height:18px;background:linear-gradient(180deg,var(--primary),var(--primary-light));border-radius:2px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow)}

/* Footer */
.footer{background:var(--navy);color:rgba(255,255,255,.4);text-align:center;padding:24px;font-size:.78rem;line-height:1.8;margin-top:40px}
"""


# ──────────────────────────────────────────────────────────
# MD 파서
# ──────────────────────────────────────────────────────────
def parse_md(text):
    """MD 텍스트에서 구조화된 데이터 추출"""
    data = {
        'date': '', 'market': '',
        'halted': [],       # 상한가
        'hot': {},          # 거래량폭발 {테마: [종목]}
        'etf': [],          # ETF 행
        'summary': '',      # 시장 요약
        'big_events': [],   # US 급등급락 이벤트
        'high52': [],       # 52주신고가 테이블
        'raw_html': '',     # 전체 MD → HTML (post용)
    }

    # 날짜 추출
    m = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', text)
    if m:
        data['date'] = f"{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}"

    # 시장 구분
    if '🇰🇷' in text or '한국 시장' in text:
        data['market'] = 'KR'
    elif '🇺🇸' in text or '미국 시장' in text:
        data['market'] = 'US'

    # 시장 요약 추출
    m = re.search(r'## 📝 오늘의 시장 요약\s*\n+(.*?)(?=\n---|\Z)', text, re.DOTALL)
    if m:
        data['summary'] = m.group(1).strip()

    lines = text.split('\n')

    if data['market'] == 'KR':
        data.update(_parse_kr(lines))
    else:
        data.update(_parse_us(lines))

    return data

def _parse_stock_block(lines, start, end):
    """단일 종목 블록 파싱 (#### 시작)"""
    block = '\n'.join(lines[start:end])
    # 헤더 줄
    header = lines[start].lstrip('#').strip()
    # 등락률 추출
    m = re.search(r'([+\-]\d+\.?\d*%)', header)
    pct = m.group(1) if m else ''
    # 종목명
    name_m = re.match(r'([^(]+)', header)
    name = name_m.group(1).strip() if name_m else header
    name = re.sub(r'\s*\+\d+\.?\d*%|\s*\-\d+\.?\d*%', '', name).strip()
    # 시장
    mkt_m = re.search(r'\(([^)]+)\)', header)
    mkt = mkt_m.group(1) if mkt_m else ''
    # 현재가, 거래량
    price_m = re.search(r'현재가.*?[:：]\s*([^\|]+)', block)
    price = price_m.group(1).strip() if price_m else ''
    vol_m = re.search(r'거래량.*?[:：]\s*([^\|]+)', block)
    vol = vol_m.group(1).strip() if vol_m else ''
    cap_m = re.search(r'시총.*?[:：]\s*([^\n\|]+)', block)
    cap = cap_m.group(1).strip() if cap_m else ''
    # 배경/이유
    reason_m = re.search(r'(?:왜 올랐나\?|왜 움직였나\?|배경).*?[:：]\s*(.+?)(?=\n-|\n\n|\Z)', block, re.DOTALL)
    reason = reason_m.group(1).strip().replace('\n', ' ')[:200] if reason_m else ''
    # 특징
    feat_m = re.search(r'특징.*?[:：]\s*(.+)', block)
    feat = feat_m.group(1).strip() if feat_m else ''
    return {'name': name, 'market': mkt, 'pct': pct, 'price': price,
            'vol': vol, 'cap': cap, 'reason': reason, 'feat': feat}

def _parse_kr(lines):
    out = {'halted': [], 'hot': {}, 'etf': []}
    i = 0
    cur_theme = '기타'
    section = ''
    while i < len(lines):
        line = lines[i]
        if '### 🚀' in line and '상한가' in line:
            section = 'halted'
        elif '### 🔥' in line:
            section = 'hot'
        elif '### 📈 ETF' in line:
            section = 'etf'
        elif '## 📝' in line:
            section = 'done'
        elif section == 'hot' and re.match(r'^#+\s+[⚡💾🤖🚗📷]', line):
            # 테마 헤더
            cur_theme = re.sub(r'^#+\s+', '', line).strip()
        elif re.match(r'^####\s+', line):
            # 종목 블록 찾기
            j = i + 1
            while j < len(lines) and not re.match(r'^####\s+', lines[j]) and not re.match(r'^###\s+', lines[j]) and not re.match(r'^##\s+', lines[j]):
                j += 1
            stock = _parse_stock_block(lines, i, j)
            if section == 'halted':
                out['halted'].append(stock)
            elif section == 'hot':
                out['hot'].setdefault(cur_theme, []).append(stock)
            i = j
            continue
        elif section == 'etf' and line.startswith('|') and '---' not in line and '종목명' not in line:
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if len(cols) >= 5:
                out['etf'].append(cols)
        i += 1
    return out

def _parse_us(lines):
    out = {'big_events': [], 'hot': {}, 'high52': []}
    i = 0
    cur_theme = '기타'
    section = ''
    while i < len(lines):
        line = lines[i]
        if '### 🚀' in line:
            section = 'big'
        elif '### 🔥' in line:
            section = 'hot'
        elif '### 📈 52주' in line:
            section = 'h52'
        elif '## 📝' in line:
            section = 'done'
        elif section == 'hot' and re.match(r'^####\s+[^\s]', line):
            # 테마 헤더
            cur_theme = re.sub(r'^#+\s+', '', line).strip()
        elif re.match(r'^####\s+\d+\.', line) and section == 'big':
            j = i + 1
            while j < len(lines) and not re.match(r'^####', lines[j]) and not re.match(r'^###', lines[j]) and not re.match(r'^##', lines[j]):
                j += 1
            stock = _parse_stock_block(lines, i, j)
            out['big_events'].append(stock)
            i = j
            continue
        elif re.match(r'^#####\s+', line) and section == 'hot':
            j = i + 1
            while j < len(lines) and not re.match(r'^#####', lines[j]) and not re.match(r'^####', lines[j]) and not re.match(r'^###', lines[j]) and not re.match(r'^##', lines[j]):
                j += 1
            stock = _parse_stock_block(lines, i, j)
            out['hot'].setdefault(cur_theme, []).append(stock)
            i = j
            continue
        elif section == 'h52' and line.startswith('|') and '---' not in line and '종목명' not in line:
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if len(cols) >= 5:
                out['high52'].append(cols)
        i += 1
    return out


# ──────────────────────────────────────────────────────────
# MD → HTML 간단 변환 (post용)
# ──────────────────────────────────────────────────────────
def md_to_html_simple(text):
    """markdown 라이브러리 없이 기본 변환"""
    html = text

    # 이스케이프
    # (already handled inline below)

    # 코드블록
    html = re.sub(r'```.*?\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    # 인라인 코드
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    # bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    # italic
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    # H1-H4
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    # ##### h5
    html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    # blockquote
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    # hr
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
    # 표 처리
    def table_replace(m):
        rows = [r for r in m.group(0).strip().split('\n') if r.strip() and not re.match(r'^\|[\s\-|]+\|$', r.strip())]
        if not rows: return m.group(0)
        out = '<div class="table-wrap"><table>'
        for ri, row in enumerate(rows):
            cells = [c.strip() for c in row.split('|') if c.strip() != '']
            tag = 'th' if ri == 0 else 'td'
            out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        return out + '</table></div>'
    html = re.sub(r'(\|.+\n)+', table_replace, html)
    # 리스트
    def list_replace(m):
        items = re.findall(r'^[-*] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    html = re.sub(r'(?:^[-*] .+\n?)+', list_replace, html, flags=re.MULTILINE)
    # 빈 줄 → <p> 구분
    html = re.sub(r'\n{2,}', '\n</p><p>\n', html)
    html = '<p>' + html + '</p>'
    # 태그 앞뒤 <p> 제거
    for tag in ['h1','h2','h3','h4','h5','hr','table','ul','pre','blockquote','div']:
        html = re.sub(rf'<p>\s*(<{tag})', r'\1', html)
        html = re.sub(rf'(</{tag}>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*</p>', '', html)
    return html


# ──────────────────────────────────────────────────────────
# 대시보드 HTML 생성
# ──────────────────────────────────────────────────────────
def stock_card_html(s, flag=''):
    cls = pct_color(s['pct'])
    emo = '▲' if cls == 'up' else ('▼' if cls == 'down' else '─')
    return f"""
<div class="stock-card {cls}">
  <div class="sc-header">
    <div class="sc-name">{s['name']} <span class="sc-mkt">{s['market']}</span></div>
    {pct_badge(s['pct'])}
  </div>
  <div class="sc-meta">
    {f'<span>💰 {s["price"]}</span>' if s['price'] else ''}
    {f'<span>📊 {s["vol"]}</span>' if s['vol'] else ''}
    {f'<span>🏢 {s["cap"]}</span>' if s['cap'] else ''}
  </div>
  {f'<div class="sc-reason">{s["reason"]}</div>' if s['reason'] else ''}
  {f'<div class="sc-feat"><span class="feat-tag">{s["feat"]}</span></div>' if s['feat'] else ''}
</div>"""

DASHBOARD_EXTRA_CSS = """
/* Dashboard specific */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:32px}
.stat-box{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);border-radius:var(--radius);padding:18px 20px}
.stat-box .sb-icon{font-size:22px;margin-bottom:8px}
.stat-box .sb-num{font-size:1.8rem;font-weight:800;color:#fff;line-height:1}
.stat-box .sb-label{font-size:.75rem;color:rgba(255,255,255,.5);margin-top:4px}
.stat-box .sb-sub{font-size:.7rem;color:rgba(96,165,250,.7);margin-top:2px}
.theme-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.theme-tab{padding:6px 14px;border-radius:20px;font-size:.8rem;font-weight:600;background:rgba(26,86,219,.1);color:var(--primary);border:1px solid rgba(26,86,219,.2);cursor:pointer;transition:var(--transition)}
.theme-tab:hover,.theme-tab.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.stocks-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-bottom:28px}
.stock-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;transition:var(--transition)}
.stock-card:hover{box-shadow:0 6px 24px rgba(26,86,219,.12);transform:translateY(-2px)}
.stock-card.up{border-left:3px solid var(--up)}
.stock-card.down{border-left:3px solid var(--down)}
.stock-card.flat{border-left:3px solid var(--flat)}
.sc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.sc-name{font-weight:700;font-size:.95rem;color:var(--text)}
.sc-mkt{font-size:.72rem;color:var(--muted);font-weight:400;margin-left:4px}
.sc-meta{display:flex;flex-wrap:wrap;gap:8px;font-size:.75rem;color:var(--muted);margin-bottom:8px}
.sc-reason{font-size:.8rem;color:var(--muted);line-height:1.55;border-top:1px solid var(--border);padding-top:8px;margin-top:4px}
.sc-feat{margin-top:6px}
.feat-tag{font-size:.7rem;background:#eff6ff;color:var(--primary);border:1px solid #bfdbfe;padding:2px 8px;border-radius:4px}
.halted-card{background:linear-gradient(135deg,#fef3c7,#fde68a);border:1px solid #fbbf24;border-radius:var(--radius);padding:20px;margin-bottom:20px}
.hc-header{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.hc-badge{background:#f59e0b;color:#fff;font-size:.75rem;font-weight:700;padding:3px 10px;border-radius:20px}
.hc-name{font-size:1.15rem;font-weight:800;color:#78350f}
.hc-meta{font-size:.82rem;color:#92400e;margin-bottom:8px}
.hc-reason{font-size:.85rem;color:#78350f;line-height:1.6}
.theme-section{margin-bottom:32px}
.theme-header{display:flex;align-items:center;gap:10px;padding:10px 16px;background:linear-gradient(90deg,#eff6ff,#f8faff);border-radius:var(--radius-sm);border-left:4px solid var(--primary);margin-bottom:14px}
.theme-header h3{font-size:.95rem;font-weight:700;color:var(--navy-mid)}
.theme-catalyst{font-size:.8rem;color:var(--muted);background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:10px 14px;margin-bottom:14px;line-height:1.6}
.summary-box{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;line-height:1.8;color:var(--text);font-size:.9rem;margin-top:8px}
.summary-box strong{color:var(--primary)}
.summary-box p{margin-bottom:12px}
.summary-box p:last-child{margin-bottom:0}
.etf-section{margin-top:32px}
@media(max-width:900px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.stats-grid{grid-template-columns:repeat(2,1fr)};.stocks-grid{grid-template-columns:1fr};.main{padding:20px 16px 40px}}
"""

def build_dashboard_kr(data, dashboard_file, post_file):
    # 통계
    all_stocks = [s for lst in data['hot'].values() for s in lst] + data['halted']
    ups   = [s for s in all_stocks if pct_color(s['pct']) == 'up']
    downs = [s for s in all_stocks if pct_color(s['pct']) == 'down']
    top_up = max(ups, key=lambda s: float(re.sub(r'[^0-9.\-]','',s['pct'] or '0')), default=None)
    top_dn = min(downs, key=lambda s: float(re.sub(r'[^0-9.\-]','',s['pct'] or '0')), default=None)

    stats_html = f"""
<div class="stats-grid">
  <div class="stat-box">
    <div class="sb-icon">🚀</div>
    <div class="sb-num">{len(data['halted'])}</div>
    <div class="sb-label">상한가 종목</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">🔥</div>
    <div class="sb-num">{len(all_stocks)}</div>
    <div class="sb-label">거래량 폭발 종목</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">📈</div>
    <div class="sb-num" style="color:#86efac">{top_up['pct'] if top_up else '—'}</div>
    <div class="sb-label">최고 상승</div>
    <div class="sb-sub">{top_up['name'] if top_up else ''}</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">📉</div>
    <div class="sb-num" style="color:#fca5a5">{top_dn['pct'] if top_dn else '—'}</div>
    <div class="sb-label">최고 하락</div>
    <div class="sb-sub">{top_dn['name'] if top_dn else ''}</div>
  </div>
</div>"""

    # 상한가
    halted_html = ''
    for s in data['halted']:
        halted_html += f"""
<div class="halted-card">
  <div class="hc-header">
    <span class="hc-badge">상한가 🚀</span>
    <span class="hc-name">{s['name']}</span>
    <span class="badge up">{s['pct']}</span>
    <span style="font-size:.8rem;color:#92400e;margin-left:auto">{s['market']}</span>
  </div>
  <div class="hc-meta">💰 {s['price']} &nbsp;|&nbsp; 📊 {s['vol']} &nbsp;|&nbsp; 🏢 {s['cap']}</div>
  <div class="hc-reason">{s['reason']}</div>
</div>"""

    # 거래량 폭발
    hot_html = ''
    tabs_html = ''.join(f'<div class="theme-tab" onclick="filterTheme(\'{i}\')">{t}</div>'
                        for i, t in enumerate(data['hot'].keys()))

    for i, (theme, stocks) in enumerate(data['hot'].items()):
        cards = ''.join(stock_card_html(s) for s in stocks)
        hot_html += f"""
<div class="theme-section" data-theme="{i}">
  <div class="theme-header"><h3>{theme}</h3></div>
  <div class="stocks-grid">{cards}</div>
</div>"""

    # ETF 테이블
    etf_html = ''
    if data['etf']:
        etf_html = f"""
<div class="etf-section">
  <div class="section-title">📈 ETF·ETN 거래량 동향</div>
  <div class="card" style="overflow:auto">
    <table>
      <thead><tr><th>종목명</th><th>시장</th><th>현재가</th><th>등락률</th><th>거래량</th><th>연관 테마</th></tr></thead>
      <tbody>{''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in data['etf'])}</tbody>
    </table>
  </div>
</div>"""

    # 요약
    summary_paras = [f'<p>{p.strip()}</p>' for p in data['summary'].split('\n\n') if p.strip()]
    summary_html = '\n'.join(summary_paras)
    # bold 처리
    summary_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', summary_html)

    body = f"""
{nav_html(data['date'], 'KR', dashboard_file, post_file, is_dashboard=True)}

<section class="hero">
  <div class="hero-inner">
    <div class="hero-eyebrow">🇰🇷 한국 시장 대시보드</div>
    <h1 class="hero-title"><span>{data['date']}</span> 시장 특징주 총정리</h1>
    <div class="hero-sub">📅 데이터 기준: 당일 장 마감 (KOSPI / KOSDAQ)</div>
    <div class="hero-actions">
      <a class="btn btn-ghost" href="index.html">🏠 홈으로</a>
      <a class="btn btn-primary" href="{post_file}">📝 블로그 포스트로 보기</a>
    </div>
  </div>
</section>

<main class="main">
  {stats_html}

  {'<div class="section-title">🚀 오늘의 상한가 종목</div>' + halted_html if halted_html else ''}

  <div style="margin-bottom:32px">
    <div class="section-title">🔥 거래량 폭발 종목</div>
    <div class="theme-tabs" id="themeTabs">
      <div class="theme-tab active" onclick="filterTheme(-1)">전체 보기</div>
      {tabs_html}
    </div>
    <div id="themeContent">{hot_html}</div>
  </div>

  {etf_html}

  <div>
    <div class="section-title">📝 오늘의 시장 요약</div>
    <div class="summary-box">{summary_html}</div>
  </div>
</main>

<footer class="footer">
  주식 리서치 허브 · 데이터 기준일 {data['date']} · 투자 권유 아님
</footer>

<script>
function filterTheme(idx) {{
  document.querySelectorAll('.theme-section').forEach((el, i) => {{
    el.style.display = (idx === -1 || i === idx) ? '' : 'none';
  }});
  document.querySelectorAll('.theme-tab').forEach((el, i) => {{
    el.classList.toggle('active', i === idx + 1 || (idx === -1 && i === 0));
  }});
}}
</script>"""
    return body


def build_dashboard_us(data, dashboard_file, post_file):
    all_stocks = [s for lst in data['hot'].values() for s in lst] + data['big_events']
    ups   = [s for s in all_stocks if pct_color(s['pct']) == 'up']
    downs = [s for s in all_stocks if pct_color(s['pct']) == 'down']
    top_up = max(ups, key=lambda s: float(re.sub(r'[^0-9.\-]','',s['pct'] or '0')), default=None)
    top_dn = min(downs, key=lambda s: float(re.sub(r'[^0-9.\-]','',s['pct'] or '0')), default=None)

    stats_html = f"""
<div class="stats-grid">
  <div class="stat-box">
    <div class="sb-icon">🚀</div>
    <div class="sb-num">{len(data['big_events'])}</div>
    <div class="sb-label">대형 이벤트 종목</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">🏆</div>
    <div class="sb-num">{len(data['high52'])}</div>
    <div class="sb-label">52주 신고가</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">📈</div>
    <div class="sb-num" style="color:#86efac">{top_up['pct'] if top_up else '—'}</div>
    <div class="sb-label">최고 상승</div>
    <div class="sb-sub">{top_up['name'] if top_up else ''}</div>
  </div>
  <div class="stat-box">
    <div class="sb-icon">📉</div>
    <div class="sb-num" style="color:#fca5a5">{top_dn['pct'] if top_dn else '—'}</div>
    <div class="sb-label">최고 하락</div>
    <div class="sb-sub">{top_dn['name'] if top_dn else ''}</div>
  </div>
</div>"""

    # 급등급락 이벤트
    big_html = ''
    for s in data['big_events']:
        big_html += stock_card_html(s)

    # 거래량 폭발
    hot_html = ''
    tabs_html = ''.join(f'<div class="theme-tab" onclick="filterTheme(\'{i}\')">{t}</div>'
                        for i, t in enumerate(data['hot'].keys()))
    for i, (theme, stocks) in enumerate(data['hot'].items()):
        cards = ''.join(stock_card_html(s) for s in stocks)
        hot_html += f'<div class="theme-section" data-theme="{i}"><div class="theme-header"><h3>{theme}</h3></div><div class="stocks-grid">{cards}</div></div>'

    # 52주 신고가 테이블
    h52_html = ''
    if data['high52']:
        h52_html = f"""
<div class="etf-section">
  <div class="section-title">🏆 52주 신고가 종목</div>
  <div class="card" style="overflow:auto">
    <table>
      <thead><tr><th>종목명</th><th>티커</th><th>현재가</th><th>등락률</th><th>거래량</th><th>비고</th></tr></thead>
      <tbody>{''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in data['high52'])}</tbody>
    </table>
  </div>
</div>"""

    summary_paras = [f'<p>{p.strip()}</p>' for p in data['summary'].split('\n\n') if p.strip()]
    summary_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', '\n'.join(summary_paras))

    body = f"""
{nav_html(data['date'], 'US', dashboard_file, post_file, is_dashboard=True)}

<section class="hero">
  <div class="hero-inner">
    <div class="hero-eyebrow">🇺🇸 미국 시장 대시보드</div>
    <h1 class="hero-title"><span>{data['date']}</span> 시장 특징주 총정리</h1>
    <div class="hero-sub">📅 데이터 기준: 당일 장 마감 (NASDAQ / NYSE)</div>
    <div class="hero-actions">
      <a class="btn btn-ghost" href="../index.html">🏠 홈으로</a>
      <a class="btn btn-primary" href="{post_file}">📝 블로그 포스트로 보기</a>
    </div>
  </div>
</section>

<main class="main">
  {stats_html}

  <div style="margin-bottom:32px">
    <div class="section-title">🚀 급등·급락 대형 이벤트</div>
    <div class="stocks-grid">{big_html}</div>
  </div>

  <div style="margin-bottom:32px">
    <div class="section-title">🔥 거래량 폭발 종목</div>
    <div class="theme-tabs" id="themeTabs">
      <div class="theme-tab active" onclick="filterTheme(-1)">전체 보기</div>
      {tabs_html}
    </div>
    <div id="themeContent">{hot_html}</div>
  </div>

  {h52_html}

  <div>
    <div class="section-title">📝 오늘의 시장 요약</div>
    <div class="summary-box">{summary_html}</div>
  </div>
</main>

<footer class="footer">
  주식 리서치 허브 · 데이터 기준일 {data['date']} · 투자 권유 아님
</footer>

<script>
function filterTheme(idx) {{
  document.querySelectorAll('.theme-section').forEach((el, i) => {{
    el.style.display = (idx === -1 || i === idx) ? '' : 'none';
  }});
  document.querySelectorAll('.theme-tab').forEach((el, i) => {{
    el.classList.toggle('active', i === idx + 1 || (idx === -1 && i === 0));
  }});
}}
</script>"""
    return body


# ──────────────────────────────────────────────────────────
# 포스트 HTML 생성
# ──────────────────────────────────────────────────────────
POST_EXTRA_CSS = """
.post-layout{max-width:860px;margin:0 auto;padding:36px 24px 60px}
.post-header{margin-bottom:32px;padding-bottom:24px;border-bottom:2px solid var(--border)}
.post-title{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:800;color:var(--navy);line-height:1.3;margin-bottom:10px}
.post-meta{display:flex;gap:12px;flex-wrap:wrap;font-size:.82rem;color:var(--muted)}
.post-meta span{display:flex;align-items:center;gap:4px}
.post-body h1{font-size:1.5rem;font-weight:800;color:var(--navy);margin:28px 0 12px;border-bottom:2px solid var(--border);padding-bottom:8px}
.post-body h2{font-size:1.2rem;font-weight:700;color:var(--navy-mid);margin:24px 0 10px;display:flex;align-items:center;gap:6px}
.post-body h2::before{content:'';display:block;width:3px;height:16px;background:var(--primary);border-radius:2px}
.post-body h3{font-size:1.05rem;font-weight:700;color:var(--primary);margin:20px 0 8px}
.post-body h4{font-size:.95rem;font-weight:700;color:var(--text);margin:16px 0 6px;padding:8px 12px;background:#f8faff;border-radius:6px;border-left:3px solid var(--primary-light)}
.post-body h5{font-size:.92rem;font-weight:700;color:var(--navy-mid);margin:12px 0 6px}
.post-body p{line-height:1.85;margin-bottom:12px;font-size:.9rem;color:var(--text)}
.post-body ul{padding-left:20px;margin-bottom:14px}
.post-body li{line-height:1.75;font-size:.88rem;color:var(--text);margin-bottom:4px}
.post-body strong{color:var(--primary-dark);font-weight:700}
.post-body em{color:var(--muted);font-style:italic}
.post-body blockquote{background:#eff6ff;border-left:4px solid var(--primary);padding:10px 16px;border-radius:0 6px 6px 0;margin:12px 0;font-size:.87rem;color:var(--navy-mid)}
.post-body hr{border:none;border-top:1px solid var(--border);margin:24px 0}
.post-body code{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:.82rem;font-family:'Consolas','Courier New',monospace}
.post-body pre{background:#1e293b;color:#e2e8f0;padding:14px 18px;border-radius:8px;overflow-x:auto;font-size:.82rem;margin:14px 0}
.table-wrap{overflow-x:auto;margin:14px 0}
.table-wrap table{min-width:500px}
.post-nav{display:flex;gap:10px;margin-top:36px;padding-top:20px;border-top:1px solid var(--border)}
.pn-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 18px;border-radius:var(--radius-sm);font-size:.85rem;font-weight:600;border:1px solid var(--border);transition:var(--transition);background:var(--card)}
.pn-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
@media(max-width:600px){.post-layout{padding:20px 16px 40px}}
"""

def build_post(data, md_text, dashboard_file, post_file):
    market_label = '한국 시장' if data['market'] == 'KR' else '미국 시장'
    flag = '🇰🇷' if data['market'] == 'KR' else '🇺🇸'
    body_html = md_to_html_simple(md_text)

    return f"""
{nav_html(data['date'], data['market'], dashboard_file, post_file, is_dashboard=False)}

<div class="post-layout">
  <div class="post-header">
    <div class="post-title">{flag} {data['date']} {market_label} 특징주 총정리</div>
    <div class="post-meta">
      <span>📅 {data['date']}</span>
      <span>📍 {market_label}</span>
      <span>🕐 장 마감 기준</span>
    </div>
    <div style="margin-top:14px">
      <a href="{dashboard_file}" class="btn btn-primary" style="font-size:.82rem;padding:7px 14px">📊 대시보드로 보기</a>
    </div>
  </div>
  <div class="post-body">{body_html}</div>
  <div class="post-nav">
    <a class="pn-btn" href="../index.html">🏠 홈으로 돌아가기</a>
    <a class="pn-btn" href="{dashboard_file}">📊 대시보드로 보기</a>
  </div>
</div>

<footer class="footer">
  주식 리서치 허브 · 데이터 기준일 {data['date']} · 본 내용은 투자 권유가 아닙니다
</footer>"""


# ──────────────────────────────────────────────────────────
# HTML 래퍼
# ──────────────────────────────────────────────────────────
def wrap_html(body, title, extra_css=''):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{title}</title>
  <style>
{COMMON_CSS}
{extra_css}
  </style>
</head>
<body>
{body}
</body>
</html>"""


# ──────────────────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────────────────
def process_md(md_path: Path):
    text = md_path.read_text(encoding='utf-8')
    data = parse_md(text)

    m = re.search(r'(\d{8})', md_path.stem)
    date_raw = m.group(1) if m else 'unknown'

    parent = md_path.parent.parent  # MD/ 상위 폴더
    dashboard_file = f'blog_{date_raw}_dashboard.html'
    post_file      = f'blog_{date_raw}_post.html'

    # ── Dashboard ─────────────────────
    if data['market'] == 'KR':
        dash_body = build_dashboard_kr(data, dashboard_file, post_file)
    else:
        dash_body = build_dashboard_us(data, dashboard_file, post_file)

    market_label = '한국 시장' if data['market'] == 'KR' else '미국 시장'
    dash_title = f"{data['date']} {market_label} 대시보드"
    dash_html = wrap_html(dash_body, dash_title, DASHBOARD_EXTRA_CSS)

    # ── Post ──────────────────────────
    post_body = build_post(data, text, dashboard_file, post_file)
    post_title = f"{data['date']} {market_label} 특징주 총정리"
    post_html = wrap_html(post_body, post_title, POST_EXTRA_CSS)

    # ── 파일 저장 ──────────────────────
    (parent / dashboard_file).write_text(dash_html, encoding='utf-8')
    (parent / post_file).write_text(post_html, encoding='utf-8')

    print(f"  ✅ {parent.name}/{dashboard_file}")
    print(f"  ✅ {parent.name}/{post_file}")
    return True


def main():
    args = sys.argv[1:]
    filter_market = args[0].upper() if args else None

    folders = {'KR': BASE / 'Kr_Daily_Report', 'US': BASE / 'Us_Daily_Report'}
    processed = 0
    print(f"\n{'─'*50}")
    print(f"  MD → HTML 변환기  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"{'─'*50}")

    for market, folder in folders.items():
        if filter_market and filter_market not in ('KR','US','ALL') and filter_market != market:
            continue
        md_dir = folder / 'MD'
        if not md_dir.exists():
            continue
        mds = sorted(md_dir.glob('*.md'))
        if not mds:
            print(f"  ⚠  {market}: MD 파일 없음")
            continue
        print(f"\n  [{market}] {len(mds)}개 MD 파일 처리 중...")
        for md in mds:
            process_md(md)
            processed += 1

    # manifest 갱신
    print(f"\n  manifest.js 갱신 중...")
    import subprocess
    subprocess.run([sys.executable, str(BASE / 'update_manifest.py')], capture_output=True)

    print(f"\n{'─'*50}")
    print(f"  총 {processed}개 MD 파일 → {processed*2}개 HTML 파일 생성 완료")
    print(f"{'─'*50}\n")


if __name__ == '__main__':
    main()
