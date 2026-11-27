param(
    [Parameter(Mandatory=$true)]
    [string]$NodeSshTarget,
    [Parameter(Mandatory=$true)]
    [string]$MacSshTarget,
    [string]$SshKey = "$HOME\.ssh\id_ed25519"
)

$ErrorActionPreference = "Continue"

Write-Output "=== 1. Starting SpecEdge 14B Server in WSL2 ==="
$serverJob = Start-Job -ScriptBlock {
    wsl -e bash -lc "cd ~/specedge && rm -rf result/three_node_14b && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python -O src/script/batch_server.py --config config/specedge_3node.yaml"
}

Write-Output "=== 2. Waiting for Server inference loop ==="
Start-Sleep -Seconds 3
$ready = $false
for ($i = 1; $i -le 60; $i++) {
    if ($serverJob.State -ne "Running") {
        Write-Output "SERVER_EXITED_EARLY"
        Receive-Job $serverJob
        exit 1
    }
    $hit = wsl -e bash -lc "grep -c 'Starting inference loop' ~/specedge/result/three_node_14b/specedge/server.log 2>/dev/null || echo 0"
    if (($hit | Out-String) -match "1") {
        Write-Output "SERVER_READY_AT_${i}s"
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    Write-Output "SERVER_WAIT_TIMEOUT"
    Stop-Job $serverJob
    exit 1
}

Write-Output "=== 3. Launching Edge 1 (node 1.7B) & Edge 2 (davids 0.6B) in parallel ==="
$nodeJob = Start-Job -ArgumentList $SshKey, $NodeSshTarget -ScriptBlock {
    param($k, $target)
    ssh -i $k -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $target "powershell -NoProfile -ExecutionPolicy Bypass -File E:\specedge\script\run_client_node.ps1" 2>&1
}
$macJob = Start-Job -ArgumentList $SshKey, $MacSshTarget -ScriptBlock {
    param($k, $target)
    ssh -i $k -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $target "bash ~/specedge/script/run_client_mac.sh" 2>&1
}

Wait-Job $nodeJob, $macJob | Out-Null

Write-Output "=== NODE (RTX 5060 Ti, Qwen3-1.7B) OUTPUT ==="
Receive-Job $nodeJob
Write-Output "=== DAVIDS (Apple M4, Qwen3-0.6B) OUTPUT ==="
Receive-Job $macJob

Write-Output "=== 4. Stopping Server cleanly ==="
wsl -e pkill -INT -f batch_server.py 2>$null
Start-Sleep -Seconds 3
Stop-Job $serverJob -ErrorAction SilentlyContinue
Remove-Job $serverJob, $nodeJob, $macJob -Force -ErrorAction SilentlyContinue
Write-Output "=== EXPERIMENT_DONE ==="
