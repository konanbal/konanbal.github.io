#!/usr/bin/env python3
"""Report_Data -> 각 폴더 이동 -> manifest.js 갱신 -> 커밋 -> push 를 한 번에 실행.

사용법:
    python publish.py            # 전체 실행
    python publish.py --dry-run  # 어디로 옮길지만 보여주고 아무것도 바꾸지 않음
    python publish.py --no-push  # 커밋까지만
"""
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "Report_Data"

# (파일명 정규식, 대상 폴더) — 위에서부터 먼저 맞는 규칙이 적용됨
RULES = [
    (r"^blog_\d{8}_KR\.html$", "Kr_Daily_Report"),
    (r"^blog_\d{8}_US\.html$", "Us_Daily_Report"),
    (r"^newsletter_\d{8}.*\.html$", "Weekly_Report"),
    (r"^(스크랩|노트|리서치|밸류체인)_.+\.(html|pdf)$", "My_Research"),
    (r"_blog\d*\.html$", "Quote"),
    (r"ETF.*_report_\d{8}\.html$", "ETF_Report"),
    # 국내 종목코드: 6자리, 숫자로 시작 (005380, 0183J0 등)
    (r"\(?\d[0-9A-Z]{5}\)?_report_\d{8}\.html$", "Kr_Stock_Report"),
    # 나머지 종목 리포트는 미국 주식 (TSLA, AVGO 등)
    (r"_report_\d{8}\.html$", "Us_Stock_Report"),
]


def classify(name):
    for pattern, folder in RULES:
        if re.search(pattern, name):
            return folder
    return None


def run(cmd):
    print("  $ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        sys.exit("\n[실패] 명령이 오류로 끝났습니다: " + " ".join(cmd))


def main():
    dry_run = "--dry-run" in sys.argv
    no_push = "--no-push" in sys.argv

    # 1. Report_Data -> 각 폴더 이동
    print("\n[1/4] Report_Data 파일 이동")
    files = sorted(p for p in SRC_DIR.glob("*") if p.is_file()) if SRC_DIR.exists() else []
    moved, skipped = [], []
    for f in files:
        folder = classify(f.name)
        if folder is None:
            skipped.append(f.name)
            continue
        dest = BASE_DIR / folder / f.name
        note = " (기존 파일 덮어씀)" if dest.exists() else ""
        print("  {} -> {}/{}".format(f.name, folder, note))
        if not dry_run:
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(f), str(dest))
        moved.append(dest.relative_to(BASE_DIR).as_posix())

    for name in skipped:
        print("  [건너뜀] 규칙에 맞는 폴더 없음: " + name)
    if not moved:
        print("  이동할 파일이 없습니다. 종료합니다.")
        return
    if dry_run:
        print("\n--dry-run: 여기서 멈춥니다. 아무것도 바뀌지 않았습니다.")
        return

    # 2. manifest.js 갱신
    print("\n[2/4] manifest.js 갱신")
    run([sys.executable, "update_manifest.py"])

    # 3. 커밋 (옮긴 파일 + manifest.js 만)
    msg = datetime.now().strftime("%Y%m%d%H%M")
    print("\n[3/4] 커밋: " + msg)
    run(["git", "add", "--", "manifest.js"] + moved)
    run(["git", "commit", "-m", msg])

    # 4. push
    if no_push:
        print("\n[4/4] --no-push: push 건너뜀")
    else:
        print("\n[4/4] push")
        run(["git", "push"])

    print("\n완료: 파일 {}개 게시 ({})".format(len(moved), msg))


if __name__ == "__main__":
    main()
