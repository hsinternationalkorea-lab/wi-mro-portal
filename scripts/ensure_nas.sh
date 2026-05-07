#!/bin/bash
# =====================================================================
# NAS 마운트 상태 점검 + 자동 재연결 (5분마다 launchd 호출)
# cron 작업 전에도 호출하면 안정성 ↑
# =====================================================================

NAS_HOST="${NAS_HOST:-teamscompany.local}"
NAS_SHARE="${NAS_SHARE:-Group_Hub}"
NAS_USER="${NAS_USER:-kjhong}"
MOUNT_POINT="/Volumes/${NAS_SHARE}"
LOG="/tmp/nas-watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG"
}

# 마운트 상태 확인
if mount | grep -q "$MOUNT_POINT"; then
    # 추가 검증 — 실제 읽기 가능?
    if ls "$MOUNT_POINT" > /dev/null 2>&1; then
        log "OK NAS 정상 ($MOUNT_POINT)"
        exit 0
    else
        log "WARN NAS 마운트는 있으나 읽기 실패 → 재마운트 시도"
        diskutil unmount "$MOUNT_POINT" 2>/dev/null || true
        sleep 2
    fi
fi

# 재마운트 시도
log "INFO NAS 마운트 시도..."

# 1차: open smb:// (Keychain 자격증명 사용)
open "smb://$NAS_USER@$NAS_HOST/$NAS_SHARE" 2>&1 | tee -a "$LOG"
sleep 5

if mount | grep -q "$MOUNT_POINT"; then
    log "OK NAS 재마운트 성공"
    exit 0
fi

# 2차: mount_smbfs 직접 호출 (Keychain에서 비번 가져옴)
mkdir -p "$MOUNT_POINT" 2>/dev/null || true
mount_smbfs "//$NAS_USER@$NAS_HOST/$NAS_SHARE" "$MOUNT_POINT" 2>&1 | tee -a "$LOG"
sleep 3

if mount | grep -q "$MOUNT_POINT"; then
    log "OK mount_smbfs 성공"
    exit 0
fi

# 실패 — 알림
log "ERROR NAS 재마운트 실패"
osascript -e 'display notification "NAS 마운트 실패. 수동 확인 필요" with title "WI NAS Watchdog" sound name "Basso"' 2>/dev/null || true
exit 1
