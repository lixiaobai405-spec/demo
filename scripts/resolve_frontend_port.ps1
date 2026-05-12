param(
  [int]$PreferredPort = 3001,
  [int]$MaxAttempts = 100,
  [Parameter(Mandatory = $true)]
  [string]$FrontendDir
)

$resolvedFrontendDir = (Resolve-Path $FrontendDir).Path.TrimEnd('\')

function Test-PortAvailable {
  param([int]$Port)

  $listener = $null
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::IPv6Any, $Port)
    $listener.Server.DualMode = $true
    $listener.Server.ExclusiveAddressUse = $true
    $listener.Start()
    return $true
  } catch {
    return $false
  } finally {
    if ($listener) {
      try {
        $listener.Stop()
      } catch {
      }
    }
  }
}

$existingListener = Get-NetTCPConnection -LocalPort $PreferredPort -State Listen -ErrorAction SilentlyContinue |
  Sort-Object OwningProcess -Unique |
  Select-Object -First 1

if ($existingListener) {
  $processId = $existingListener.OwningProcess
  $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue

  if ($process -and $process.Name -eq "node.exe" -and $process.CommandLine -like "*$resolvedFrontendDir*") {
    Write-Host "[Meitai Demo] Found existing frontend process on port $PreferredPort (PID $processId), restarting it..."
    Stop-Process -Id $processId -Force -ErrorAction Stop
    Start-Sleep -Milliseconds 750
  } elseif ($process) {
    Write-Host "[Meitai Demo] Port $PreferredPort is busy with $($process.Name) (PID $processId), searching for another port..."
  } else {
    Write-Host "[Meitai Demo] Port $PreferredPort is busy, searching for another port..."
  }
}

for ($port = $PreferredPort; $port -lt ($PreferredPort + $MaxAttempts); $port++) {
  if (Test-PortAvailable -Port $port) {
    Write-Output $port
    exit 0
  }
}

Write-Error "No available port found in range $PreferredPort-$($PreferredPort + $MaxAttempts - 1)."
exit 1
