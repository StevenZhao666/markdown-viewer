param([string]$FilePath)

# 防止UNC路径导致工作目录异常
Set-Location "D:\MarkdownViewer"

$PORT = 18520
$PYTHON = "C:\Users\风夜\AppData\Local\Programs\Python\Python311\python.exe"
$HELPER = "D:\MarkdownViewer\helper.py"

# 检测端口是否已监听（助手已在运行？）
function Test-Port($hostname, $port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($hostname, $port)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-Port "127.0.0.1" $PORT)) {
    Write-Host "启动文件助手..."
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $PYTHON
    $pinfo.Arguments = """$HELPER"""
    $pinfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $pinfo.CreateNoWindow = $true
    [void][System.Diagnostics.Process]::Start($pinfo)

    # 等就绪（最长2秒）
    $ready = $false
    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Milliseconds 200
        if (Test-Port "127.0.0.1" $PORT) { $ready = $true; break }
    }
    if (-not $ready) {
        Write-Host "错误：文件助手启动失败" -ForegroundColor Red
        Read-Host "按回车退出"
        exit 1
    }
}

# 打开浏览器
$encodedPath = [System.Uri]::EscapeDataString($FilePath)
$url = "http://127.0.0.1:$PORT/?file=$encodedPath"
Start-Process $url
