# -*- coding: utf-8 -*-
"""
_secrets/ 폴더 백업 ZIP 생성 (5/14 Mac 이전용)
- 출력: ~/Desktop/wi_secrets_backup_YYYYMMDD.zip
- 그 후 사장님이 시놀로지 NAS의 Group_Hub/1_shared/4_secrets_backup/ 에 업로드
"""
import os
import zipfile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
SECRETS_DIR = ROOT / "_secrets"
ZIP_OUT = Path.home() / "Desktop" / f"wi_secrets_backup_{datetime.now().strftime('%Y%m%d')}.zip"


def main():
    if not SECRETS_DIR.exists():
        print(f"❌ _secrets/ 폴더 없음: {SECRETS_DIR}")
        return

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SECRETS_DIR):
            for file in files:
                src = Path(root) / file
                arc = src.relative_to(ROOT)  # _secrets/.env, _secrets/cookies/... 형태
                zf.write(src, arc)

    file_count = sum(1 for _ in SECRETS_DIR.rglob("*") if _.is_file())
    size_kb = ZIP_OUT.stat().st_size / 1024
    print(f"OK 파일 {file_count}개 백업")
    print(f"OK ZIP: {ZIP_OUT}  ({size_kb:.1f} KB)")
    print()
    print("다음 단계:")
    print("1. 시놀로지 NAS 접속 (https://teamscompany.quickconnect.to)")
    print("2. File Station → Group_Hub/1_shared/4_secrets_backup/ 이동")
    print("3. 위 ZIP 파일 업로드")
    print("4. (5/14) Mac에서 다운받아 PriceIntel/ 안에 압축 풀기")


if __name__ == "__main__":
    main()
