@echo off
cd /d D:\Projects\markdown-viewer
powershell.exe -ExecutionPolicy Bypass -File "D:\Projects\markdown-viewer\OpenMarkdown.ps1" "%~1"
