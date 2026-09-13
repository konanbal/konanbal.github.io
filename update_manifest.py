#!/usr/bin/env python3
import re
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent

LIST_PAGES = {
    "kr_daily_list.html",
    "us_daily_list.html",
    "stock_list.html",
    "kr_stock_list.html",
    "us_stock_list.html",
    "weekly_list.html",
    "quote_list.html",
    "etf_list.html",
    "theme_list.html",
    "kr_viewer.html",
    "us_viewer.html",
    "stock_viewer.html",
    "kr_stock_viewer.html",
    "us_stock_viewer.html",
    "weekly_viewer.html",
    "quote_viewer.html",
    "etf_viewer.html",
    "theme_viewer.html",
}


def _mtime_hhmm(fh):
    return datetime.fromtimestamp(fh.stat().st_mtime).strftime("%H:%M")


def _datetime_str(date_fmt, fh):
    return "{} {}".format(date_fmt, _mtime_hhmm(fh))


def scan_kr_daily():
    folder = BASE_DIR / "Kr_Daily_Report"
    items = []
    if not folder.exists():
        return items
    files_new = sorted(folder.glob("blog_*_KR.html"), reverse=True)
    files_old = sorted(folder.glob("blog_*_dashboard.html"), reverse=True)
    seen = set()
    for f in files_new:
        m = re.match(r"blog_(\d{8})_KR\.html", f.name)
        if m:
            ds = m.group(1)
            if ds in seen:
                continue
            seen.add(ds)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
            items.append({
                "date": date_fmt,
                "datetime": _datetime_str(date_fmt, f),
                "date_raw": ds,
                "file": f.name,
                "title": "한국 주식 일일 리포트 {}".format(date_fmt)
            })
    for f in files_old:
        m = re.match(r"blog_(\d{8})_dashboard\.html", f.name)
        if m:
            ds = m.group(1)
            if ds in seen:
                continue
            seen.add(ds)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
            post_file = "blog_{}_post.html".format(ds)
            post_exists = (folder / post_file).exists()
            items.append({
                "date": date_fmt,
                "datetime": _datetime_str(date_fmt, f),
                "date_raw": ds,
                "dashboard": f.name,
                "post": post_file if post_exists else None,
                "title": "한국 주식 일일 리포트 {}".format(date_fmt)
            })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def scan_us_daily():
    folder = BASE_DIR / "Us_Daily_Report"
    items = []
    if not folder.exists():
        return items
    files_new = sorted(folder.glob("blog_*_US.html"), reverse=True)
    files_old = sorted(folder.glob("blog_*_dashboard.html"), reverse=True)
    seen = set()
    for f in files_new:
        m = re.match(r"blog_(\d{8})_US\.html", f.name)
        if m:
            ds = m.group(1)
            if ds in seen:
                continue
            seen.add(ds)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
            items.append({
                "date": date_fmt,
                "datetime": _datetime_str(date_fmt, f),
                "date_raw": ds,
                "file": f.name,
                "title": "미국 주식 일일 리포트 {}".format(date_fmt)
            })
    for f in files_old:
        m = re.match(r"blog_(\d{8})_dashboard\.html", f.name)
        if m:
            ds = m.group(1)
            if ds in seen:
                continue
            seen.add(ds)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
            post_file = "blog_{}_post.html".format(ds)
            post_exists = (folder / post_file).exists()
            items.append({
                "date": date_fmt,
                "datetime": _datetime_str(date_fmt, f),
                "date_raw": ds,
                "dashboard": f.name,
                "post": post_file if post_exists else None,
                "title": "미국 주식 일일 리포트 {}".format(date_fmt)
            })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def _scan_stock_folder(folder_path):
    items = []
    folder = BASE_DIR / folder_path
    if not folder.exists():
        return items
    files = sorted(folder.glob("*.html"))
    for fh in files:
        if fh.name in LIST_PAGES:
            continue
        m = re.search(r"_(\d{8})\.html$", fh.name)
        date_fmt = ""
        if m:
            ds = m.group(1)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
        dt_str = _datetime_str(date_fmt, fh) if date_fmt else datetime.fromtimestamp(fh.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        name = re.sub(r"_report_\d{8}\.html$", "", fh.name)
        if name == fh.name:
            name = re.sub(r"_\d{8}\.html$", "", name)
        items.append({
            "date": date_fmt,
            "datetime": dt_str,
            "file": fh.name,
            "title": name,
            "name": name
        })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def scan_kr_stock_reports():
    return _scan_stock_folder("Kr_Stock_Report")


def scan_us_stock_reports():
    return _scan_stock_folder("Us_Stock_Report")


def scan_weekly_reports():
    folder = BASE_DIR / "Weekly_Report"
    items = []
    if not folder.exists():
        return items
    files = sorted(folder.glob("*.html"))
    for fh in files:
        if fh.name in LIST_PAGES:
            continue
        m = re.search(r"(\d{8})", fh.name)
        date_fmt = ""
        if m:
            ds = m.group(1)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
        dt_str = _datetime_str(date_fmt, fh) if date_fmt else datetime.fromtimestamp(fh.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        title = "주간 금융 뉴스레터 {}".format(date_fmt) if date_fmt else fh.stem
        items.append({
            "date": date_fmt,
            "datetime": dt_str,
            "file": fh.name,
            "title": title
        })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def scan_etf_reports():
    folder = BASE_DIR / "ETF_Report"
    items = []
    if not folder.exists():
        return items
    files = sorted(folder.glob("*.html"))
    for fh in files:
        if fh.name in LIST_PAGES:
            continue
        m = re.search(r"_(\d{8})\.html$", fh.name)
        date_fmt = ""
        if m:
            ds = m.group(1)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
        dt_str = _datetime_str(date_fmt, fh) if date_fmt else datetime.fromtimestamp(fh.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        name = re.sub(r"_report_\d{8}\.html$", "", fh.name)
        if name == fh.name:
            name = re.sub(r"_\d{8}\.html$", "", name)
        items.append({
            "date": date_fmt,
            "datetime": dt_str,
            "file": fh.name,
            "title": name,
            "name": name
        })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def scan_theme_reports():
    folder = BASE_DIR / "Theme_Report"
    items = []
    if not folder.exists():
        return items
    files = sorted(folder.glob("*.html"))
    for fh in files:
        if fh.name in LIST_PAGES:
            continue
        # 네이버 붙여넣기용 사본은 목록에서 제외 (동일 내용)
        if fh.name.endswith("_naver.html"):
            continue
        m = re.search(r"_(\d{8})\.html$", fh.name)
        date_fmt = ""
        if m:
            ds = m.group(1)
            date_fmt = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
        dt_str = _datetime_str(date_fmt, fh) if date_fmt else datetime.fromtimestamp(fh.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        # 밸류체인_[테마]_YYYYMMDD.html → "[테마] 밸류체인"
        theme = re.sub(r"_\d{8}\.html$", "", fh.name)
        theme = re.sub(r"^밸류체인_", "", theme)
        theme = theme.replace("_", " ").strip()
        title = "{} 밸류체인".format(theme) if theme else fh.stem
        items.append({
            "date": date_fmt,
            "datetime": dt_str,
            "file": fh.name,
            "title": title,
            "name": title
        })
    items.sort(key=lambda x: x["datetime"], reverse=True)
    return items


def scan_quotes():
    folder = BASE_DIR / "Quote"
    items = []
    if not folder.exists():
        return items
    files = sorted(folder.glob("*.html"))
    for fh in files:
        if fh.name in LIST_PAGES:
            continue
        raw = fh.read_text(encoding="utf-8", errors="ignore")
        m_t = re.search(r'class="blog-title"[^>]*>([^<]+)<', raw)
        title = m_t.group(1).strip() if m_t else fh.stem
        m_a = re.search(r'class="(?:hero-attr|attribution|attr)"[^>]*>([^<]+)<', raw)
        author = re.sub(r"^[—\-\s]+", "", m_a.group(1).strip()) if m_a else ""
        m_d = re.search(r"(\d{8})", fh.name)
        mtime = fh.stat().st_mtime
        if m_d:
            ds = m_d.group(1)
            mdate = "{}-{}-{}".format(ds[:4], ds[4:6], ds[6:])
        else:
            mdate = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        mdt = "{} {}".format(mdate, datetime.fromtimestamp(mtime).strftime("%H:%M"))
        items.append({"date": mdate, "datetime": mdt, "mtime": mtime, "file": fh.name, "title": title, "author": author})
    items.sort(key=lambda x: x["datetime"], reverse=True)
    for it in items:
        it.pop("mtime", None)
    return items


def main():
    manifest = {
        "generated": datetime.now().isoformat(),
        "Kr_Daily_Report": scan_kr_daily(),
        "Us_Daily_Report": scan_us_daily(),
        "Kr_Stock_Report": scan_kr_stock_reports(),
        "Us_Stock_Report": scan_us_stock_reports(),
        "Weekly_Report": scan_weekly_reports(),
        "Quote": scan_quotes(),
        "ETF_Report": scan_etf_reports(),
        "Theme_Report": scan_theme_reports(),
        "list_pages": {
            "kr":       "Kr_Daily_Report/kr_daily_list.html",
            "us":       "Us_Daily_Report/us_daily_list.html",
            "kr_stock": "Kr_Stock_Report/kr_stock_list.html",
            "us_stock": "Us_Stock_Report/us_stock_list.html",
            "weekly":   "Weekly_Report/weekly_list.html",
            "quote":    "Quote/quote_list.html",
            "etf":      "ETF_Report/etf_list.html",
            "theme":    "Theme_Report/theme_list.html"
        }
    }

    body = json.dumps(manifest, ensure_ascii=False, indent=2)
    js_content = (
        "// Auto-generated by update_manifest.py -- DO NOT EDIT MANUALLY\n"
        "// Run: python update_manifest.py\n"
        "window.SITE_MANIFEST = " + body + ";\n"
    )

    output_path = BASE_DIR / "manifest.js"
    output_path.write_text(js_content, encoding="utf-8")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n  manifest.js generated [{}]".format(now))
    print("-" * 44)
    for key in ["Kr_Daily_Report", "Us_Daily_Report", "Kr_Stock_Report", "Us_Stock_Report", "Weekly_Report", "Quote", "ETF_Report", "Theme_Report"]:
        print("  {:<22}: {:>3} items".format(key, len(manifest[key])))
    print("-" * 44 + "\n")


if __name__ == "__main__":
    main()
