#!/bin/bash
pkill -f "python3 bot.py"
cd ~/autoprime-bot
source venv/bin/activate
python3 bot.py
