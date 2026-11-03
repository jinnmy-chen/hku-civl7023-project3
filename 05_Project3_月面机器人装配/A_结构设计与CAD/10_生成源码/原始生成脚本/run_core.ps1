param([string]$Script,[string]$Log,[string]$Drawing='')
$psi=New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName='D:\AutoCAD 2027\accoreconsole.exe'
$psi.Arguments='/s "'+$Script+'"'
if($Drawing){$psi.Arguments+=' /i "'+$Drawing+'"'}
$psi.UseShellExecute=$false
$psi.CreateNoWindow=$true
$psi.RedirectStandardOutput=$true
$psi.RedirectStandardError=$true
$psi.StandardOutputEncoding=[System.Text.Encoding]::Unicode
$psi.StandardErrorEncoding=[System.Text.Encoding]::Unicode
$proc=New-Object System.Diagnostics.Process
$proc.StartInfo=$psi
[void]$proc.Start()
$outTask=$proc.StandardOutput.ReadToEndAsync()
$errTask=$proc.StandardError.ReadToEndAsync()
$proc.WaitForExit()
$s=$outTask.Result+$errTask.Result
[System.IO.File]::WriteAllText($Log,$s,[System.Text.UTF8Encoding]::new($true))
Write-Output ('Core exit: '+$proc.ExitCode)
Write-Output ($s -split "`n" | Select-Object -Last 12)
