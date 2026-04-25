#!/usr/bin/env python3
import sys, time, threading, subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

MD_FILE = PROJECT_ROOT / "md" / "正文.md"
DOCX_FILE = PROJECT_ROOT / "docx_tex" / "正文_formatted.docx"
CONVERTER = SCRIPT_DIR / "pandoc_convert.py"
DEBOUNCE_SECONDS = 2.0

_timer = None

def run_conversion():
    print(f"\n[{time.strftime('%H:%M:%S')}] 检测到变更，开始转换…")
    result = subprocess.run(
        ["python3", str(CONVERTER), str(MD_FILE), str(DOCX_FILE)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  ✓ 已更新：{DOCX_FILE.name}")
    else:
        print(f"  ✗ 转换失败：{result.stderr[-400:] if result.stderr else ''}")

def schedule_conversion():
    global _timer
    if _timer:
        _timer.cancel()
    _timer = threading.Timer(DEBOUNCE_SECONDS, run_conversion)
    _timer.start()

class MdHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if Path(event.src_path).resolve() == MD_FILE.resolve():
            schedule_conversion()

    def on_created(self, event):
        if Path(event.src_path).resolve() == MD_FILE.resolve():
            schedule_conversion()

if __name__ == "__main__":
    print(f"监听：{MD_FILE.relative_to(PROJECT_ROOT)}")
    print(f"输出：{DOCX_FILE.relative_to(PROJECT_ROOT)}")
    print(f"防抖：{DEBOUNCE_SECONDS}s  按 Ctrl+C 退出\n")
    run_conversion()
    observer = Observer()
    observer.schedule(MdHandler(), str(PROJECT_ROOT / "md"), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n已停止。")
