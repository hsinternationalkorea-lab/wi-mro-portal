#!/bin/bash
# =====================================================================
# NAS 영구 마운트 + 자동 재연결 셋업 (Mac, 5/14 1회 실행)
# 사용: bash scripts/setup_nas_persistent.sh
# 전제: 시놀로지 NAS 호스트 = teamscompany.local 또는 LAN IP
# =====================================================================

set -e

NAS_HOST="${NAS_HOST:-teamscompany.local}"
NAS_SHARE="${NAS_SHARE:-Group_Hub}"
NAS_USER="${NAS_USER:-kjhong}"
MOUNT_POINT="/Volumes/${NAS_SHARE}"

echo "==================================="
echo "NAS 영구 마운트 셋업"
echo "Host:  $NAS_HOST"
echo "Share: $NAS_SHARE"
echo "User:  $NAS_USER"
echo "Mount: $MOUNT_POINT"
echo "==================================="

# 1. /etc/nsmb.conf — SMB idle timeout 24시간
echo ""
echo "[1/4] /etc/nsmb.conf 설정 (sudo 비번 필요)"
if [ ! -f /etc/nsmb.conf ] || ! grep -q "idle_timeout" /etc/nsmb.conf; then
    sudo tee -a /etc/nsmb.conf > /dev/null <<EOF

# WI MRO — NAS 안정 마운트
[default]
idle_timeout=86400
streams=yes
notify_off=yes
signing_required=no

[$NAS_HOST:$NAS_SHARE]
addr=$NAS_HOST
EOF
    echo "  ✓ idle_timeout=24h 적용"
else
    echo "  - 이미 설정됨 (skip)"
fi

# 2. Keychain 자격증명 저장 (한 번만 입력 후 영구)
echo ""
echo "[2/4] Keychain 자격증명 저장"
echo "  → Finder에서 Cmd+K → smb://$NAS_HOST/$NAS_SHARE 접속 시"
echo "    'Remember this password in my keychain' ☑ 체크"
echo "  → 한 번만 입력하면 이후 자동"

# 3. launchd 자동 마운트 + 재연결 watchdog
PLIST="$HOME/Library/LaunchAgents/com.wi.nas-watchdog.plist"
echo ""
echo "[3/4] launchd watchdog 등록 ($PLIST)"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wi.nas-watchdog</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/Wholesale_Industry/MRO/PriceIntel/scripts/ensure_nas.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/nas-watchdog.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nas-watchdog.err</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "  ✓ 5분마다 자동 마운트 상태 점검 + 재연결"

# 4. 첫 마운트 시도
echo ""
echo "[4/4] 첫 마운트 시도"
if [ ! -d "$MOUNT_POINT" ]; then
    open "smb://$NAS_USER@$NAS_HOST/$NAS_SHARE"
    sleep 3
fi

if [ -d "$MOUNT_POINT" ]; then
    echo "  ✓ NAS 마운트 성공: $MOUNT_POINT"
    echo ""
    ls -la "$MOUNT_POINT" | head -10
else
    echo "  ⚠ Finder가 자동 열림 — Keychain 저장 후 재실행"
fi

echo ""
echo "==================================="
echo "✅ NAS 셋업 완료"
echo "==================================="
echo ""
echo "검증:"
echo "  ls /Volumes/$NAS_SHARE/"
echo ""
echo "Watchdog 로그:"
echo "  tail -f /tmp/nas-watchdog.log"
echo ""
echo "마운트 끊겨도 5분 안에 자동 재연결됩니다."
