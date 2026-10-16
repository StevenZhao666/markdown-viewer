# -*- coding: utf-8 -*-
"""生成 MarkdownViewer 便携版分发包（免安装文件夹版，通用命名，不面向特定人群）：
- icon.ico（纯 Python 手写，32+16，蓝底白箭头）
- OpenMarkdown.bat / OpenMarkdown.ps1（相对路径 + 自带 Python 优先）
- 一键设为默认.bat / _setup.ps1（注册 + 直接生效逻辑 + 兜底引导）
- 使用说明.txt
"""
import os, struct

PKG = r'D:\MarkdownViewer\portable-package\MarkdownViewer'

# ─────────────────────── 1) icon.ico ───────────────────────
def draw(size):
    """蓝底 + 白色下箭头 + 底横线。返回 BGRA 行（自下而上之外按 y 正序，后面逆序）"""
    ACC = (204, 122, 0, 255)   # BGRA: #007acc
    WHT = (255, 255, 255, 255)
    bg = [ACC] * (size * size)
    def put(x, y):
        if 0 <= x < size and 0 <= y < size:
            bg[y * size + x] = WHT
    s = size / 32.0
    # 竖杆
    x0, x1 = int(12 * s), int(19 * s)
    for y in range(int(5 * s), int(15 * s)):
        for x in range(x0, x1 + 1):
            put(x, y)
    # 箭头三角
    tip = int(23 * s)
    for i, y in enumerate(range(int(14 * s), tip)):
        half = int((19 - 12) * s * (1 - i / max(1, tip - int(14 * s))))
        for x in range(int(15.5 * s) - half, int(15.5 * s) + half + 1):
            put(x, y)
    # 底横线
    for y in range(int(27 * s), int(29 * s)):
        for x in range(int(7 * s), int(25 * s)):
            put(x, y)
    return bg

def bmp_payload(size):
    pixels = draw(size)
    # BITMAPINFOHEADER: 高度写两倍
    hdr = struct.pack('<IiiHHIIiiII', 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    data = bytearray(hdr)
    for y in range(size - 1, -1, -1):          # 自下而上
        for x in range(size):
            b, g, r, a = pixels[y * size + x]
            data += bytes((b, g, r, a))
    # AND mask（1bpp，每行 4 字节对齐），全 0
    rowbytes = ((size + 31) // 32) * 4
    data += bytes(rowbytes * size)
    return bytes(data)

def make_ico(path):
    sizes = (32, 16)
    payloads = [bmp_payload(s) for s in sizes]
    out = struct.pack('<HHH', 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    entries = b''
    for s, p in zip(sizes, payloads):
        entries += struct.pack('<BBBBHHII', s if s < 256 else 0, s if s < 256 else 0, 0, 0, 1, 32, len(p), offset)
        offset += len(p)
    with open(path, 'wb') as f:
        f.write(out + entries + b''.join(payloads))

make_ico(os.path.join(PKG, 'icon.ico'))
print('OK icon.ico', os.path.getsize(os.path.join(PKG, 'icon.ico')), 'bytes')

# ─────────────────────── 2) 启动脚本 ───────────────────────
BAT = '@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0OpenMarkdown.ps1" "%~1"\r\n'

PS1 = '''param([string]$FilePath)
$Root = $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location $Root
$PORT = 18520
$SelfPy = Join-Path $Root 'runtime-python\\python.exe'
$HELPER = Join-Path $Root 'helper.py'

if (Test-Path $SelfPy) {
    $PYTHON = $SelfPy
} else {
    $c = Get-Command python -ErrorAction SilentlyContinue
    if ($c) { $PYTHON = $c.Source }
    else {
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show("缺少运行环境：请重新解压完整的 MarkdownViewer 文件夹（所有文件要放在一起）。", "Markdown Viewer", "OK", "Error") | Out-Null
        exit 1
    }
}

function Test-Port($hostname, $port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($hostname, $port)
        $client.Close()
        return $true
    } catch { return $false }
}

if (-not (Test-Port "127.0.0.1" $PORT)) {
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $PYTHON
    $pinfo.Arguments = '"' + $HELPER + '"'
    $pinfo.WorkingDirectory = $Root
    $pinfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $pinfo.CreateNoWindow = $true
    [void][System.Diagnostics.Process]::Start($pinfo)
    $ready = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Milliseconds 200
        if (Test-Port "127.0.0.1" $PORT) { $ready = $true; break }
    }
    if (-not $ready) {
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show("文件助手启动失败。请重新解压 MarkdownViewer 文件夹后再试。", "Markdown Viewer", "OK", "Error") | Out-Null
        exit 1
    }
}

$url = "http://127.0.0.1:$PORT/"
if ($FilePath) { $url += "?file=" + [System.Uri]::EscapeDataString($FilePath) }
Start-Process $url
'''

SETUP_BAT = '@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0_setup.ps1"\r\nif errorlevel 1 pause\r\n'

SETUP = '''$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$CmdFile = Join-Path $Root 'OpenMarkdown.ps1'
$IcoFile = Join-Path $Root 'icon.ico'

Write-Host ''
Write-Host '  ===== Markdown Viewer 一键设为默认程序 =====' -ForegroundColor Cyan
Write-Host ''

# ---- 1/4 注册程序（双击 .md 时要执行的东西）----
$cls = 'HKCU:\\Software\\Classes'
New-Item "$cls\\MarkdownViewer.md\\shell\\open\\command" -Force | Out-Null
Set-Item "$cls\\MarkdownViewer.md" -Value 'Markdown Viewer'
if (Test-Path $IcoFile) {
    New-Item "$cls\\MarkdownViewer.md\\DefaultIcon" -Force | Out-Null
    Set-Item "$cls\\MarkdownViewer.md\\DefaultIcon" -Value $IcoFile
}
$cmd = 'powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $CmdFile + '" "%1"'
Set-Item "$cls\\MarkdownViewer.md\\shell\\open\\command" -Value $cmd
Write-Host '  [1/4] 已注册 Markdown Viewer' -ForegroundColor Green

# ---- 2/4 关联 .md + 右键新建 ----
New-Item "$cls\\.md" -Force | Out-Null
Set-Item "$cls\\.md" -Value 'MarkdownViewer.md'
New-Item "$cls\\.md\\OpenWithProgids" -Force | Out-Null
New-ItemProperty "$cls\\.md\\OpenWithProgids" -Name 'MarkdownViewer.md' -PropertyType None -Value ([byte[]]@()) -Force | Out-Null
New-Item "$cls\\.md\\ShellNew" -Force | Out-Null
New-ItemProperty "$cls\\.md\\ShellNew" -Name 'NullFile' -PropertyType String -Value '' -Force | Out-Null
Write-Host '  [2/4] 已关联 .md（含右键 新建 -> Markdown 文档）' -ForegroundColor Green

# ---- 3/4 注册到 Windows「默认应用」列表 ----
$cap = 'HKCU:\\Software\\MarkdownViewer\\Capabilities'
New-Item "$cap\\FileAssociations" -Force | Out-Null
Set-ItemProperty $cap 'ApplicationName' 'Markdown Viewer'
Set-ItemProperty $cap 'ApplicationDescription' 'Markdown / LaTeX note editor'
New-ItemProperty "$cap\\FileAssociations" -Name '.md' -Value 'MarkdownViewer.md' -PropertyType String -Force | Out-Null
New-ItemProperty 'HKCU:\\Software\\RegisteredApplications' -Name 'MarkdownViewer' -Value 'Software\\MarkdownViewer\\Capabilities' -PropertyType String -Force | Out-Null
Write-Host '  [3/4] 已注册到 Windows 默认应用列表' -ForegroundColor Green

# ---- 4/4 让它真正成为「双击 .md 时的默认」----
$ucPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.md\\UserChoice'
$uc = $null
try { $uc = Get-ItemProperty $ucPath -ErrorAction Stop } catch {}

if (-not $uc) {
    Write-Host '  [4/4] 检测到 .md 没有其他程序占用 → 已直接生效！' -ForegroundColor Green
    Write-Host ''
    Write-Host '  完成 ✔  现在双击任何 .md 文件，都会用 Markdown Viewer 打开。' -ForegroundColor Cyan
    Write-Host '  在桌面或文件夹里：右键 → 新建 → Markdown 文档，可以直接新建笔记。' -ForegroundColor Cyan
} else {
    $cur = $uc.ProgId
    Write-Host ''
    Write-Host ("  提示：.md 当前由 [{0}] 打开。" -f $cur) -ForegroundColor Yellow
    $ans = Read-Host '  要把默认改成 Markdown Viewer 吗？ (Y = 是，直接回车或输入 N = 不改)'
    if ($ans -eq 'Y' -or $ans -eq 'y') {
        Remove-Item $ucPath -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 400
        $still = $null
        try { $still = Get-ItemProperty $ucPath -ErrorAction Stop } catch {}
        if (-not $still) {
            Write-Host '  完成 ✔  已改为 Markdown Viewer，现在双击 .md 就会用它打开。' -ForegroundColor Cyan
        } else {
            Write-Host '  Windows 保护了这个设置，需要手动点一下：' -ForegroundColor Yellow
            Start-Process 'ms-settings:defaultapps'
            Write-Host '  在打开的「设置」里搜索 Markdown Viewer，点右边的「设为默认值」即可。' -ForegroundColor Yellow
        }
    } else {
        Write-Host '  已跳过（.md 保持原样）。想改的时候随时重新运行本脚本。' -ForegroundColor Gray
    }
}
Write-Host ''
Read-Host '  按回车退出'
'''

README = '''============================================
  Markdown Viewer —— 使用说明
============================================

【第一次使用：只需做一次】
  双击「一键设为默认.bat」→ 按提示操作（多数情况下会直接完成，不需要手动设置）。
  完成后，双击任何 .md 文件就会用本程序打开。

【日常使用】
  · 打开笔记：双击 .md 文件，直接编辑，Ctrl + S 保存
  · 新建笔记：在桌面/文件夹里 右键 → 新建 → Markdown 文档
  · 打开整个笔记文件夹：打开程序后，点左上角「打开文件夹」，选中你的笔记文件夹，
    左侧就会出现完整的文件列表
  · 也可以把 .md 文件直接拖进程序窗口
  · 左侧栏：点右上角小三角收起；想拉宽/拉窄，拖中间的竖线；拖到很窄会自动收起

【提示】
  · 本程序完全在你的电脑上运行，不联网、不上传任何内容
  · 整个文件夹可以拷到 U 盘或其他电脑，解压即用，什么都不用安装
  · 请保持文件夹完整，不要单独挪走里面的文件；
    如果移动了文件夹位置，重新运行一次「一键设为默认.bat」即可
'''

for name, content in [('OpenMarkdown.bat', BAT), ('一键设为默认.bat', SETUP_BAT)]:
    with open(os.path.join(PKG, name), 'w', encoding='ascii', newline='') as f:
        f.write(content)
    print('OK', name)

for name, content in [('OpenMarkdown.ps1', PS1), ('_setup.ps1', SETUP), ('使用说明.txt', README)]:
    with open(os.path.join(PKG, name), 'w', encoding='utf-8-sig', newline='') as f:
        f.write(content)
    print('OK', name, '(UTF-8 BOM)')

print('DONE')
