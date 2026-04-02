#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/launch.log"

cd "$SCRIPT_DIR" || exit 1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching Chill Guard" >> "$LOG_FILE"
"$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/chill_guard_app.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Exit code: $EXIT_CODE" >> "$LOG_FILE"

if [ "$EXIT_CODE" -ne 0 ]; then
  echo
  echo "Chill Guard 启动失败，退出码: $EXIT_CODE"
  echo "日志文件: $LOG_FILE"
  echo "按回车键关闭此窗口..."
  read -r _
fi
