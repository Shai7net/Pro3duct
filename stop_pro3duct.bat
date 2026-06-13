@echo off
title Pro3duct - Stop
cd /d "%~dp0"
echo Stopping Pro3duct services...
docker compose stop
echo Pro3duct has stopped.
timeout /t 2 >nul
