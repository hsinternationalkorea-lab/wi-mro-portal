# -*- coding: utf-8 -*-
"""
일일 통합 크롤링 스크립트 (Windows + Mac 호환)
- registry.yaml 읽어 enabled=true 크롤러를 priority 순서로 실행
- 각 크롤러 격리 실행 (subprocess + timeout)
- 결과 crawl_runs DB 기록 + 로그 파일
- 한 크롤러 실패해도 다음 진행

사용:
    python crawlers/daily_refresh.py             # 모든 enabled 크롤러
    python crawlers/daily_refresh.py cretec      # 특정 크롤러만
    python crawlers/daily_refresh.py --dry-run   # 실행 안 하고 계획만
"""
import os
import sys
import re
import time
import subprocess
import platform
import ctypes
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
REGISTRY = ROOT / "crawlers" / "registry.yaml"
LOG_DIR = ROOT / "output" / "cron"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Mac에서 cron 시작 전 NAS 마운트 보장
if sys.platform == "darwin":
    nas_mount = Path("/Volumes/Group_Hub")
    if not nas_mount.exists():
        ensure_script = ROOT / "scripts" / "ensure_nas.sh"
        if ensure_script.exists():
            try:
                subprocess.run(["bash", str(ensure_script)], timeout=30)
                time.sleep(3)
            except Exception as e:
                print(f"WARN NAS 마운트 시도 실패: {e}")

# Windows 절전 방지
if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)


def parse_yaml_simple(path):
    """yaml 라이브러리 의존성 없이 우리 registry.yaml 만 파싱
    (구조: crawlers: - name: ... script: ... enabled: ...)"""
    crawlers = []
    current = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            stripped = line.strip()
            if stripped == "crawlers:":
                continue
            if line.startswith("  - "):
                if current:
                    crawlers.append(current)
                current = {}
                # 첫 줄에 키:값 가능 (- name: cretec)
                kv = line[4:].split(":", 1)
                if len(kv) == 2:
                    current[kv[0].strip()] = parse_value(kv[1].strip())
            elif line.startswith("    ") and current is not None and ":" in line:
                k, v = line.strip().split(":", 1)
                current[k.strip()] = parse_value(v.strip())
        if current:
            crawlers.append(current)
    return crawlers


def parse_value(v):
    # inline comment 제거 (yaml 단순 파서 — 우리 registry는 따옴표 안에 # 안 씀)
    if " #" in v:
        v = v.split(" #", 1)[0].rstrip()
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    # 숫자
    if re.match(r"^-?\d+$", v):
        return int(v)
    # 따옴표 제거
    return v.strip('"\'')


def get_python():
    """현재 인터프리터 경로"""
    return sys.executable


def run_crawler(c, log_dir):
    """단일 크롤러 실행 (subprocess + timeout). (status, duration_sec, log_path) 반환"""
    name = c["name"]
    script = c["script"]
    timeout = c.get("timeout_min", 60) * 60

    script_path = ROOT / "crawlers" / script
    if not script_path.exists():
        print(f"  [SKIP] {name}: 스크립트 없음 ({script})", flush=True)
        return ("skipped", 0, None)

    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"\n{'='*60}", flush=True)
    print(f"[START] {name} ({script}) — timeout {timeout//60}분", flush=True)
    print(f"{'='*60}", flush=True)

    started = time.time()
    try:
        with open(log_file, "w", encoding="utf-8", errors="replace") as f:
            proc = subprocess.run(
                [get_python(), str(script_path)],
                stdout=f, stderr=subprocess.STDOUT,
                cwd=str(ROOT),
                timeout=timeout,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        elapsed = time.time() - started
        if proc.returncode == 0:
            print(f"[OK   ] {name} — {elapsed/60:.1f}분 (log: {log_file.name})", flush=True)
            return ("success", elapsed, str(log_file))
        else:
            print(f"[FAIL ] {name} — exit {proc.returncode} ({elapsed/60:.1f}분)", flush=True)
            return ("failed", elapsed, str(log_file))
    except subprocess.TimeoutExpired:
        elapsed = time.time() - started
        print(f"[TIMEOUT] {name} — {timeout//60}분 초과 강제 종료", flush=True)
        return ("timeout", elapsed, str(log_file))
    except Exception as e:
        elapsed = time.time() - started
        print(f"[ERROR] {name}: {e}", flush=True)
        return ("error", elapsed, str(log_file))


def log_run(name, status, duration_sec, log_path):
    """crawl_runs 에 기록 (실패해도 무시)"""
    try:
        sys.path.insert(0, str(ROOT))
        from supabase_client import SupabaseClient
        c = SupabaseClient()
        c.insert("crawl_runs", {
            "source_code": name,
            "status": status,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "notes": f"daily_refresh — {duration_sec/60:.1f}min, log: {Path(log_path).name if log_path else '-'}",
        })
    except Exception as e:
        print(f"  (log_run 실패: {e})", flush=True)


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    target = next((a for a in args if not a.startswith("--")), None)

    if not REGISTRY.exists():
        print(f"❌ {REGISTRY} 없음")
        sys.exit(1)

    crawlers = parse_yaml_simple(REGISTRY)
    if not crawlers:
        print("❌ registry.yaml 비어있음")
        sys.exit(1)

    # 필터 + 정렬
    enabled = [c for c in crawlers if c.get("enabled") and (target is None or c["name"] == target)]
    enabled.sort(key=lambda c: c.get("priority", 999))

    print(f"\n{'='*60}")
    print(f"WI MRO Daily Refresh — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"실행 대상: {len(enabled)}개 크롤러")
    print(f"{'='*60}\n")
    for c in enabled:
        print(f"  - [{c.get('priority',999):>2}] {c['name']:<15} ({c.get('timeout_min', 60)}분 timeout) — {c.get('notes','')}")
    if dry_run:
        print("\n--dry-run, 실제 실행 안 함")
        return

    started_total = time.time()
    summary = []

    for c in enabled:
        result = run_crawler(c, LOG_DIR)
        summary.append((c["name"], result))
        log_run(c["name"], result[0], result[1], result[2])

        # 다음 크롤러 시작 전 휴식
        delay = c.get("delay_after_min", 5)
        if delay > 0 and c != enabled[-1]:
            print(f"  ... {delay}분 휴식 후 다음 크롤러", flush=True)
            time.sleep(delay * 60)

    # 요약
    total_elapsed = time.time() - started_total
    print(f"\n{'='*60}")
    print(f"전체 완료 — {total_elapsed/60:.1f}분")
    print(f"{'='*60}")
    for name, (status, dur, _) in summary:
        emoji = "✅" if status == "success" else "❌" if status in ("failed", "error") else "⏱️" if status == "timeout" else "⏭️"
        print(f"  {emoji} {name:<15} {status:<10} {dur/60:.1f}분")

    # exit 1은 "전체가 실패"일 때만. 부분 실패는 systemd status를 'failed'로 만들지 않음
    # (개별 실패는 Supabase crawl_runs + 이 stdout 로그에 이미 기록됨)
    if summary and all(s[1][0] in ("failed", "error", "timeout") for s in summary):
        print("\n[exit 1] 모든 크롤러 실패", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
