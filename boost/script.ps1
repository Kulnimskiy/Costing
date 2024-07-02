$projectPath = "C:\Users\User\Desktop\Projects\Costing"
$venvPath = "$projectPath\venv\Scripts\activate"
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "cmd.exe"
$startInfo.Arguments = "/c cd $projectPath && call $venvPath && flask --app .\project\app run --debug"
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
[System.Diagnostics.Process]::Start($startInfo) | Out-Null

Start-Sleep -Seconds 2
Start-Process "http://192.168.1.87:5000"