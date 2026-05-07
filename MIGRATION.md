# Windows → Mac 마이그레이션 가이드

다음 주 Mac으로 메인 PC 변경 시 30분 안에 모든 환경 복원.

## 사전 준비 (Windows에서 마지막에)

### 1. 비밀 백업 (USB or 1Password or 클라우드)

```powershell
# Windows에서 _secrets/ 폴더 압축
Compress-Archive -Path "C:\Wholesale Industry\AI Assistant\MRO\PriceIntel\_secrets" `
                 -DestinationPath "$env:USERPROFILE\Desktop\wi_secrets_backup.zip"
```

비밀번호 걸어 USB로 옮김 (또는 1Password에 .zip 첨부 / 본인 이메일에 첨부).

### 2. 마지막 push 확인

```powershell
cd "C:\Wholesale Industry\AI Assistant\MRO\PriceIntel"
git status         # 변경 없어야 함
git log -1         # 최근 commit 확인
```

작업 중이면 commit + push 후 옮기기.

---

## Mac에서 복원 (30분)

### Step 1: 기본 도구 설치

터미널 열고:

```bash
# Homebrew (Mac 패키지 매니저)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python, Git
brew install python@3.13 git

# (선택) VS Code, Cursor
brew install --cask visual-studio-code
```

### Step 2: 코드 가져오기

```bash
mkdir -p ~/Wholesale_Industry/MRO
cd ~/Wholesale_Industry/MRO
git clone https://github.com/hsinternationalkorea-lab/wi-mro-portal.git PriceIntel
cd PriceIntel
```

GitHub Personal Access Token 필요 — Mac에서도 처음엔 한 번 입력.

### Step 3: 비밀 복원

USB에서 `wi_secrets_backup.zip` 가져와서:

```bash
cd ~/Wholesale_Industry/MRO/PriceIntel
unzip ~/Downloads/wi_secrets_backup.zip
ls _secrets/   # .env, cookies/ 보이는지 확인
```

### Step 4: Python 환경 + 의존성

```bash
cd ~/Wholesale_Industry/MRO/PriceIntel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install playwright
playwright install chromium
```

### Step 5: 검증

```bash
# Supabase 연결 확인
python supabase_client.py

# 크롤러 dry-run
python crawlers/daily_refresh.py --dry-run

# 포털 로컬 실행
streamlit run portal/app.py
```

브라우저에서 `http://localhost:8501` 떠야 함.

### Step 6: 자동 크롤링 (cron, optional)

Mac은 Windows Task Scheduler 대신 `crontab`:

```bash
crontab -e
```

아래 한 줄 추가 (매일 새벽 3시):

```
0 3 * * * cd ~/Wholesale_Industry/MRO/PriceIntel && /usr/bin/env python3 crawlers/daily_refresh.py >> output/cron/cron.log 2>&1
```

저장 (`:wq`).

또는 launchd (Mac 권장):
- `~/Library/LaunchAgents/com.wi.mro.crawl.plist` 만들기
- 자세한 건 `MIGRATION_LAUNCHD.md` 참조 (필요 시 작성)

---

## 차이점 요약 (Windows vs Mac)

| 항목 | Windows | Mac |
|---|---|---|
| Python 절전방지 | `ctypes.windll.kernel32...` | `caffeinate` (자동 처리) |
| 경로 구분자 | `\` | `/` |
| Cron | Task Scheduler GUI | `crontab -e` 또는 `launchd` |
| 가상환경 활성화 | `venv\Scripts\activate` | `source venv/bin/activate` |
| Python 명령 | `python` | `python3` |

대부분 코드는 `os.path.join` / `pathlib.Path` 사용해서 자동 호환됨.

---

## 트러블슈팅

### "playwright install" 실패
```bash
brew install --cask chromium
playwright install chromium --with-deps
```

### "ModuleNotFoundError: No module named 'streamlit'"
가상환경 활성화 안 됨 → `source venv/bin/activate` 다시.

### Supabase 연결 실패
`_secrets/.env` 복원 안 됨 → Step 3 다시.

### Git push 실패
GitHub PAT 만료 가능 → https://github.com/settings/tokens 에서 재발급.
