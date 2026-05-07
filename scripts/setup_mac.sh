#!/bin/bash
# =====================================================================
# WI MRO Portal — Mac 자동 설치 스크립트
# 사용: bash scripts/setup_mac.sh
# 전제: _secrets/ 폴더 이미 복원됨 (USB 등에서)
# =====================================================================

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

echo "==================================="
echo "WI MRO Portal — Mac Setup"
echo "프로젝트: $PROJECT_DIR"
echo "==================================="

# 1. Python 버전 체크
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 없음. brew install python@3.13 먼저 실행"
    exit 1
fi
echo "Python: $(python3 --version)"

# 2. _secrets 확인
if [ ! -f "_secrets/.env" ]; then
    echo "❌ _secrets/.env 없음. USB 등에서 복원해주세요."
    echo "   백업 파일 위치: ~/Downloads/wi_secrets_backup.zip"
    exit 1
fi
echo "✅ _secrets/.env 확인됨"

# 3. 가상환경
if [ ! -d "venv" ]; then
    echo "→ venv 생성"
    python3 -m venv venv
fi
source venv/bin/activate

# 4. 의존성 설치
echo "→ pip install"
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
pip install playwright

# 5. Playwright 브라우저
echo "→ playwright chromium 설치 (5분 정도)"
playwright install chromium --with-deps

# 6. 검증
echo ""
echo "→ Supabase 연결 테스트"
python supabase_client.py

echo ""
echo "→ 크롤러 dry-run"
python crawlers/daily_refresh.py --dry-run

# 7. cron 등록 안내
echo ""
echo "==================================="
echo "✅ 설치 완료"
echo "==================================="
echo ""
echo "다음 단계:"
echo "  1. 포털 실행:  source venv/bin/activate && streamlit run portal/app.py"
echo "  2. 자동 크롤:  crontab -e 에 다음 한 줄 추가"
echo ""
echo "      0 3 * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python crawlers/daily_refresh.py >> output/cron/cron.log 2>&1"
echo ""
