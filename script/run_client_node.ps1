param(
    [string]$ServerHost = "100.88.119.25:8000",
    [string]$DraftModel = "E:\models\Qwen3-1.7B",
    [int]$ClientIdx = 0
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$env:SPECEDGE_RESULT_PATH = "result/three_node_14b"
$env:SPECEDGE_EXP_NAME = "specedge"
$env:SPECEDGE_PROCESS_NAME = "client_node_1.7b"
$env:SPECEDGE_SEED = "42"
$env:SPECEDGE_OPTIMIZATION = "2"
$env:SPECEDGE_MAX_LEN = "2048"

$env:SPECEDGE_DRAFT_MODEL = $DraftModel
$env:SPECEDGE_DEVICE = "cuda:0"
$env:SPECEDGE_DTYPE = "fp16"
$env:SPECEDGE_REASONING = "False"

$env:SPECEDGE_DATASET = "specbench"
$env:SPECEDGE_MAX_N_BEAMS = "32"
$env:SPECEDGE_MAX_BEAM_LEN = "4"
$env:SPECEDGE_MAX_BRANCH_WIDTH = "16"
$env:SPECEDGE_MAX_BUDGET = "32"

$env:SPECEDGE_PROACTIVE_TYPE = "excluded"
$env:SPECEDGE_PROACTIVE_MAX_N_BEAMS = "32"
$env:SPECEDGE_PROACTIVE_MAX_BEAM_LEN = "3"
$env:SPECEDGE_PROACTIVE_MAX_BRANCH_WIDTH = "16"
$env:SPECEDGE_PROACTIVE_MAX_BUDGET = "32"

$env:SPECEDGE_MAX_NEW_TOKENS = "64"
$env:SPECEDGE_MAX_REQUEST_NUM = "-1"
$env:SPECEDGE_REQ_OFFSET = "0"
$env:SPECEDGE_SAMPLE_REQ_CNT = "48"

$env:SPECEDGE_HOST = $ServerHost
$env:SPECEDGE_CLIENT_IDX = "$ClientIdx"
$env:PYTHONPATH = "src"

& ".\.venv\Scripts\python.exe" -O "src/script/client.py"
