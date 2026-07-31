@echo off
cd /d D:\MarkdownViewer
powershell.exe -ExecutionPolicy Bypass -File "D:\MarkdownViewer\OpenMarkdown.ps1" "%~1"
