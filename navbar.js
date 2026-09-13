// ── 공용 네비게이션 자동 생성 ──────────────────────────────
// 이 파일을 수정하면 사이트 전체 네비게이션이 한 번에 바뀝니다.
// index.html: <script src="navbar.js"></script>
// 하위 폴더:  <script src="../navbar.js"></script>

(function () {
  // 현재 경로 기반으로 prefix 자동 결정
  var p = window.location.pathname.replace(/\\/g, '/');
  var isRoot = !/\/(Kr_Daily_Report|Us_Daily_Report|Kr_Stock_Report|Us_Stock_Report|Weekly_Report|Quote|ETF_Report|Theme_Report)\//.test(p);
  var pre = isRoot ? '' : '../';

  // ── 메뉴 항목 정의 (여기만 수정하면 전체 반영) ─────────────
  var ITEMS = [
    { key: 'home',     href: pre + 'index.html',                                    icon: '🏠',  label: '홈'              },
    { key: 'kr',       href: pre + 'Kr_Daily_Report/kr_daily_list.html',            icon: '🇰🇷', label: '한국 주식'        },
    { key: 'us',       href: pre + 'Us_Daily_Report/us_daily_list.html',            icon: '🇺🇸', label: '미국 주식'        },
    { key: 'kr_stk',   href: pre + 'Kr_Stock_Report/kr_stock_list.html',            icon: '📊',  label: '한국 종목 리포트' },
    { key: 'us_stk',   href: pre + 'Us_Stock_Report/us_stock_list.html',            icon: '📋',  label: '미국 종목 리포트' },
    { key: 'etf',      href: pre + 'ETF_Report/etf_list.html',                      icon: '📈',  label: 'ETF 리포트'      },
    { key: 'thm',      href: pre + 'Theme_Report/theme_list.html',                  icon: '🔗',  label: '테마 밸류체인'   },
    { key: 'wk',       href: pre + 'Weekly_Report/weekly_list.html',                icon: '📰',  label: '주간 뉴스레터'   },
    { key: 'qt',       href: pre + 'Quote/quote_list.html',                         icon: '💬',  label: '오늘의 명언'     },
  ];

  // ── 현재 페이지의 active 키 자동 감지 ──────────────────────
  function detectActive() {
    if (/\/Kr_Daily_Report\//.test(p))   return 'kr';
    if (/\/Us_Daily_Report\//.test(p))   return 'us';
    if (/\/Kr_Stock_Report\//.test(p))   return 'kr_stk';
    if (/\/Us_Stock_Report\//.test(p))   return 'us_stk';
    if (/\/ETF_Report\//.test(p))        return 'etf';
    if (/\/Theme_Report\//.test(p))      return 'thm';
    if (/\/Weekly_Report\//.test(p))     return 'wk';
    if (/\/Quote\//.test(p))             return 'qt';
    return 'home';
  }

  var activeKey = detectActive();

  // ── 스타일 주입 (전역 네비게이션 통일) ──────────────────────
  function injectStyles() {
    var style = document.createElement('style');
    style.innerHTML = `
      .navbar {
        position: sticky; top: 0; z-index: 1000;
        background: #0f2244; box-shadow: 0 2px 12px rgba(0,0,0,.3);
        font-family: 'Pretendard', sans-serif;
      }
      .navbar-inner, .nb {
        max-width: 1280px; margin: 0 auto; padding: 0 24px;
        display: flex; align-items: center; gap: 8px; height: 56px;
        overflow: hidden; flex-wrap: nowrap;
      }
      .nav-logo, .logo {
        display: flex; align-items: center; flex-shrink: 0; gap: 10px;
        color: #fff !important; font-size: 1.05rem; font-weight: 700;
        letter-spacing: -.3px; margin-right: 8px; text-decoration: none;
      }
      .logo-icon {
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-size: 16px; flex-shrink: 0;
      }
      .nav-links {
        display: flex; align-items: center; gap: 1px; list-style: none;
        flex: 1; flex-wrap: nowrap; overflow: hidden; min-width: 0; margin: 0; padding: 0;
      }
      .nav-links li { list-style: none; }
      .nav-links a {
        display: flex; align-items: center; gap: 5px; padding: 6px 10px;
        border-radius: 8px; color: rgba(255,255,255,.75);
        font-size: .82rem; font-weight: 500; white-space: nowrap;
        transition: all .22s; text-decoration: none;
      }
      .nav-links a:hover, .nav-links a.active {
        background: rgba(255,255,255,.12); color: #fff;
      }
      .nav-links a .nav-icon { font-size: 14px; }
      .nav-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
      .nav-badge, #ts, #lastUpdated {
        background: rgba(255,255,255,.1); color: rgba(255,255,255,.7);
        font-size: .75rem; padding: 3px 8px; border-radius: 20px;
        border: 1px solid rgba(255,255,255,.15); white-space: nowrap;
      }
      @media (max-width: 900px) { .nav-links { display: none; } }
    `;
    document.head.appendChild(style);
  }

  // ── ul.nav-links 를 채워 넣음 ──────────────────────────────
  function inject() {
    injectStyles();

    var ul = document.querySelector('ul.nav-links');
    if (ul) {
      ul.innerHTML = ITEMS.map(function (item) {
        var cls = item.key === activeKey ? ' class="active"' : '';
        return '<li><a href="' + item.href + '"' + cls + '>'
             + '<span class="nav-icon">' + item.icon + '</span> '
             + item.label + '</a></li>';
      }).join('');
    }

  }

  // DOM 준비 여부에 따라 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
