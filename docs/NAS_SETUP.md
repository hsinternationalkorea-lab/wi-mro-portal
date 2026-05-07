# 시놀로지 NAS 영구 마운트 셋업 가이드

5/14 Mac 받은 후 1시간 안에 "끊김 없는 24/7 NAS 연결" 완성.

## Part A: 시놀로지 DSM 설정 (사장님 직접, 5분)

### A-1. SMB idle timeout 늘리기

1. https://teamscompany.quickconnect.to 로그인
2. **제어판 → 파일 서비스 → SMB → 고급**
3. 다음 설정 변경:
   - **Smallest SMB protocol**: SMB2 (또는 SMB3)
   - **Largest SMB protocol**: SMB3
   - **고급 옵션**:
     - `idle session timeout in minutes` = **0** (또는 1440 = 24시간)
4. **적용**

→ NAS 측에서 idle 세션 안 끊음.

### A-2. 자격증명 저장 (Mac에서 한 번만)

5/14 Mac에서:
1. Finder → **Cmd+K**
2. 주소: `smb://teamscompany.local/Group_Hub`
   (또는 사무실 LAN IP, 예: `smb://192.168.0.X/Group_Hub`)
3. 사용자: 사장님 계정 (예: kjhong)
4. 비번 입력 시 ☑ **"Remember this password in my keychain"**
5. **연결**

→ 이후 비번 다시 안 물음.

## Part B: Mac 자동화 셋업 (스크립트 1줄)

### B-1. 영구 마운트 + watchdog (1줄)

```bash
cd ~/Wholesale_Industry/MRO/PriceIntel
bash scripts/setup_nas_persistent.sh
```

스크립트가 자동으로:
- `/etc/nsmb.conf` 에 `idle_timeout=86400` 설정
- `~/Library/LaunchAgents/com.wi.nas-watchdog.plist` 등록
- 5분마다 NAS 마운트 상태 자동 점검 + 재연결
- 첫 마운트 시도

### B-2. 검증

```bash
ls /Volumes/Group_Hub/   # 1_shared, 2_WI, 3_TeamS 보여야 함
tail -f /tmp/nas-watchdog.log   # watchdog 로그 모니터링
```

## Part C: cron 작업 안전 보장

`crawlers/daily_refresh.py` 가 실행 시작 시 자동으로:
1. `/Volumes/Group_Hub` 존재 확인
2. 없으면 `scripts/ensure_nas.sh` 호출 → 재마운트 시도
3. 그 후 크롤러 시작

→ 새벽 3시 cron 돌 때 NAS 끊겨있어도 자동 복구.

## Part D: 견고 대안 — rclone 양방향 동기화 (선택)

NAS 직접 마운트 대신 **로컬 ↔ NAS 동기화** = 네트워크 끊겨도 로컬 보존.

### 설치
```bash
brew install rclone
rclone config
# 이름: synology
# 타입: SMB
# 호스트: teamscompany.local
# 사용자/비번 입력
# 공유: Group_Hub
```

### 매일 동기화 (cron)
```bash
# 자정마다 양방향 sync
0 0 * * * /opt/homebrew/bin/rclone bisync ~/wi_local/ synology:/Group_Hub/ --resync-mode=newer
```

장점:
- NAS 끊겨도 로컬 작업 가능
- 재연결 시 자동 catch-up
- 디스크 공간만 추가 (자료 2배)

## 트러블슈팅

### 마운트 끊김이 자주 발생
```bash
# nsmb.conf 확인
cat /etc/nsmb.conf | grep idle

# 안 되어있으면
sudo vim /etc/nsmb.conf
# [default] 섹션에 idle_timeout=86400 추가
```

### Watchdog 작동 안 함
```bash
# launchd 상태 확인
launchctl list | grep wi.nas

# 재로드
launchctl unload ~/Library/LaunchAgents/com.wi.nas-watchdog.plist
launchctl load ~/Library/LaunchAgents/com.wi.nas-watchdog.plist
```

### Keychain 자격증명 만료
1. **키체인 접근** 앱 열기
2. `teamscompany.local` 검색
3. 항목 삭제
4. Finder Cmd+K로 다시 마운트하면서 새로 저장

### 사무실 외부에서 NAS 접근 (집/이동 중)
- Tailscale 또는 시놀로지 QuickConnect 사용
- 마운트 URL 변경: `smb://teamscompany.quickconnect.to/Group_Hub`
- 또는 Tailscale IP 사용

## 안정성 등급

| 셋업 | 안정성 |
|---|---|
| 기본 마운트만 | 🟡 70% (절전·재시작 시 끊김) |
| + Keychain | 🟢 85% |
| + nsmb.conf | 🟢 95% |
| + watchdog | 🟢 99% |
| + rclone | 🟢 100% (NAS 다운도 OK) |

5/14에 **+watchdog 까지** 99% 안정. rclone은 Phase 2~3에 검토.
