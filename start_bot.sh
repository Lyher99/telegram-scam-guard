#!/bin/bash
cd /home/ubuntu/code/Telegram
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi
export TELEGRAM_BOT_TOKEN
python3 -m bot.main >> /tmp/bot.log 2>&1
