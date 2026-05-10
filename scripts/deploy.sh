#!/bin/bash
# UI / 코드 변경 한 번에 배포 — Mac에서 실행
#
# 사용:
#   bash scripts/deploy.sh "커밋 메시지"
#   bash scripts/deploy.sh "fix: 검색창 색상"
#
# 흐름:
#   1) git add -A + commit + push (Mac → GitHub)
#   2) AWS 서버에서 git pull
#   3) systemd restart (Streamlit 재기동)
#   4) https://portal.koreaene.co.kr 200 응답 확인

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEY="/Users/grouphub/Downloads/LightsailDefaultKey-ap-northeast-2 (1).pem"
HOST="ubuntu@15.165.87.119"
URL="https://portal.koreaene.co.kr"

MSG="${1:-update}"

cd "$ROOT"

echo "=== 1) 변경사항 ==="
git status --short
echo

if git diff --quiet && git diff --cached --quiet; then
    echo "  변경 없음 — push 스킵"
    NEED_PUSH=0
else
    NEED_PUSH=1
fi

if [ "$NEED_PUSH" = "1" ]; then
    echo "=== 2) commit + push ==="
    git add -A
    git commit -m "$MSG"
    git push
    echo
fi

echo "=== 3) AWS 서버 반영 (git pull + restart) ==="
ssh -i "$KEY" "$HOST" 'cd ~/wi-mro-portal && git pull --rebase && sudo systemctl restart wi-mro-portal && sleep 3 && sudo systemctl is-active wi-mro-portal'
echo

echo "=== 4) 운영 URL 응답 확인 ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ $URL — HTTP $HTTP_CODE"
else
    echo "  ⚠️  $URL — HTTP $HTTP_CODE (확인 필요)"
fi
