#!/bin/bash
# =====================================================================
# WI MRO — Mac 첫 셋업 마스터 스크립트 (5/8 도착 직후 1회 실행)
#
# 사용법 (Mac 터미널에 한 줄 붙여넣기):
#   curl -fsSL https://raw.githubusercontent.com/hsinternationalkorea-lab/wi-mro-portal/main/scripts/mac_first_run.sh | bash
#
# 또는 Wi-Fi 없을 때: USB로 이 파일 옮긴 후 → bash mac_first_run.sh
# =====================================================================

set -e

# =====================================================================
# 색상 + 헬퍼
# =====================================================================
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

step()  { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
ok()    { echo -e "${GREEN}✓ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠ $1${NC}"; }
err()   { echo -e "${RED}✗ $1${NC}"; }
ask()   { echo -e "${YELLOW}? $1${NC}"; }

# =====================================================================
# 설정
# =====================================================================
PROJECT_DIR="$HOME/Wholesale_Industry/MRO/PriceIntel"
GITHUB_REPO="hsinternationalkorea-lab/wi-mro-portal"
NAS_HOST="${NAS_HOST:-teamscompany.local}"
NAS_SHARE="Group_Hub"
SECRETS_BACKUP_PATH="1_shared/4_secrets_backup"

echo ""
echo "════════════════════════════════════════════════"
echo "  WI MRO Mac 첫 셋업 마스터 스크립트"
echo "  $(date)"
echo "════════════════════════════════════════════════"

# =====================================================================
# Step 1: macOS 업데이트 권장
# =====================================================================
step "1/9   환경 확인"
echo "macOS: $(sw_vers -productVersion)"
echo "Hardware: $(sysctl -n machdep.cpu.brand_string)"
ok "환경 확인 완료"

# =====================================================================
# Step 2: Homebrew
# =====================================================================
step "2/9   Homebrew 설치"
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # PATH 추가 (Apple Silicon Mac)
    if [ -f /opt/homebrew/bin/brew ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    ok "Homebrew 설치 완료"
else
    ok "Homebrew 이미 설치됨"
fi

# =====================================================================
# Step 3: Python + Git + 기타
# =====================================================================
step "3/9   Python + Git 설치"
brew install python@3.13 git wget jq 2>&1 | tail -5
ok "기본 도구 설치 완료"

# =====================================================================
# Step 4: 코드 가져오기
# =====================================================================
step "4/9   GitHub 코드 clone"
mkdir -p "$(dirname "$PROJECT_DIR")"
if [ ! -d "$PROJECT_DIR/.git" ]; then
    git clone "https://github.com/$GITHUB_REPO.git" "$PROJECT_DIR"
    ok "Clone 완료: $PROJECT_DIR"
else
    cd "$PROJECT_DIR"
    git pull
    ok "최신 코드 pull"
fi
cd "$PROJECT_DIR"

# =====================================================================
# Step 5: NAS 마운트 (Keychain 자격증명 입력)
# =====================================================================
step "5/9   NAS 마운트"

if [ ! -d "/Volumes/$NAS_SHARE" ]; then
    ask "NAS 마운트가 필요합니다."
    echo "  1. Finder가 자동 열립니다"
    echo "  2. 사용자/비번 입력 시 ☑ 'Remember this password in my keychain'"
    echo "  3. 연결 후 이 터미널에서 Enter"
    open "smb://$NAS_HOST/$NAS_SHARE"
    read -p "  → NAS 마운트 완료되면 Enter ▶ "
fi

if [ -d "/Volumes/$NAS_SHARE" ]; then
    ok "NAS 마운트 확인: /Volumes/$NAS_SHARE"
else
    err "NAS 마운트 실패. 수동 마운트 후 스크립트 재실행"
    exit 1
fi

# =====================================================================
# Step 6: _secrets 복원
# =====================================================================
step "6/9   _secrets 복원"
SECRETS_ZIP="/Volumes/$NAS_SHARE/$SECRETS_BACKUP_PATH/wi_secrets_backup_*.zip"
LATEST_ZIP=$(ls -t $SECRETS_ZIP 2>/dev/null | head -1)

if [ -n "$LATEST_ZIP" ] && [ -f "$LATEST_ZIP" ]; then
    cd "$PROJECT_DIR"
    unzip -o "$LATEST_ZIP" -d .
    if [ -f "_secrets/.env" ]; then
        ok "_secrets 복원 완료 ($LATEST_ZIP)"
    else
        warn "ZIP 풀었으나 .env 못 찾음"
    fi
else
    warn "NAS에서 _secrets backup ZIP 못 찾음"
    echo "  경로 확인: /Volumes/$NAS_SHARE/$SECRETS_BACKUP_PATH/"
    ls "/Volumes/$NAS_SHARE/$SECRETS_BACKUP_PATH/" 2>/dev/null || echo "  (폴더 비어있음)"
    read -p "  USB나 다른 경로로 _secrets 복원 후 Enter ▶ "
fi

# =====================================================================
# Step 7: Python 가상환경 + 의존성
# =====================================================================
step "7/9   Python 환경 + 의존성"
cd "$PROJECT_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
pip install playwright
playwright install chromium --with-deps
ok "Python + Playwright 준비 완료"

# =====================================================================
# Step 8: NAS 영구 마운트 + watchdog
# =====================================================================
step "8/9   NAS 영구 마운트 셋업"
bash scripts/setup_nas_persistent.sh
ok "NAS watchdog 등록 완료 (5분마다 자동 재연결)"

# =====================================================================
# Step 9: 검증
# =====================================================================
step "9/9   검증"

# Supabase 연결
echo ""
echo "→ Supabase 연결 테스트"
python supabase_client.py 2>&1 | head -10

# 크롤러 dry-run
echo ""
echo "→ 크롤러 dry-run"
python crawlers/daily_refresh.py --dry-run 2>&1 | head -15

# =====================================================================
# 완료 + 다음 단계
# =====================================================================
echo ""
echo "════════════════════════════════════════════════"
ok "🎉 Mac 셋업 100% 완료"
echo "════════════════════════════════════════════════"
echo ""
echo "다음 단계 (선택):"
echo ""
echo "  ▸ 포털 로컬 실행:"
echo "      cd $PROJECT_DIR && source venv/bin/activate && streamlit run portal/app.py"
echo ""
echo "  ▸ cron 등록 (매일 새벽 3시 자동 크롤):"
echo "      crontab -e"
echo "      # 다음 한 줄 추가:"
echo "      0 3 * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python crawlers/daily_refresh.py >> output/cron/cron.log 2>&1"
echo ""
echo "  ▸ Tailscale 설치 (외부 원격 접속):"
echo "      brew install --cask tailscale"
echo ""
echo "  ▸ 시놀로지 DSM SMB 설정 (idle timeout = 0):"
echo "      docs/NAS_SETUP.md 참조"
echo ""
