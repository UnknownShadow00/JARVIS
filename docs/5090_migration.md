# RTX 5090 Migration Runbook

This runbook covers migrating JARVIS from the RTX 4070 Ti Super 16GB machine to the RTX 5090 32GB server PC.

## Prerequisites

- NVIDIA driver installed and the GPU visible in Device Manager
- CUDA 12.8+
- Ollama 0.12.7+
- Windows 11 Pro
- Python installed and available on `PATH`
- Git installed and available on `PATH`

## Step 1: Install Ollama On New Server

1. Download and install Ollama for Windows on the new server PC.
2. Open PowerShell and verify the version:

```powershell
ollama --version
```

3. Confirm the installed version is `0.12.7` or newer before pulling `qwen3-vl`.

## Step 2: Pull Full Model Stack

Run the full model pulls in PowerShell:

```powershell
ollama pull qwen3:32b
ollama pull qwen2.5-coder:32b
ollama pull gemma3:4b
ollama pull qwen3-vl
```

## Step 3: Set Ollama Environment Variables

Set these Windows environment variables before starting or restarting Ollama:

- `OLLAMA_KEEP_ALIVE=-1`
- `OLLAMA_NUM_PARALLEL=2`

PowerShell example:

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "-1", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "2", "Machine")
```

Restart the Ollama service or reboot the server after setting them.

## Step 4: Switch JARVIS To The 5090 Profile

From the repo root, update `config.yaml` with the 5090 model profile:

```powershell
python scripts/switch_models.py --profile 5090
```

This sets:

- `models.main` to `qwen3:32b`
- `models.coder` to `qwen2.5-coder:32b`
- `models.vision` to `qwen3-vl`

## Step 5: Clone Repo And Install Python Dependencies

Clone the repo onto the new server, then install dependencies:

```powershell
git clone <repo-url>
cd JARVIS
pip install -r requirements.txt
```

## Step 6: Verify The Test Suite

Run the verification command from the repo root:

```powershell
pytest tests/ -q --tb=short
```

Expected result: `265+` tests pass.

## Step 7: Activate Hermes Agent

Install Hermes Agent using the NousResearch install command:

```powershell
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Configure Hermes to use:

- Endpoint: `http://localhost:11434/v1`
- Model: `qwen3:32b`
- Context: `65536`

Do not enable Hermes until the 5090 system is up and the local Ollama stack is verified.

## Step 8: Enable Discord And Telegram In `config.yaml`

Update the `comms` section in `config.yaml`:

- Set `discord_enabled: true`
- Set `telegram_enabled: true`
- Fill in the required token and channel/chat values

## Step 9: Update `CLAUDE.md` Hardware Status

Update `CLAUDE.md` so the active hardware status reflects the live 5090 server setup instead of the temporary 4070 Ti fallback state.

Items to confirm in that update:

- 5090 is the active server GPU
- Qwen3 32B is the primary model
- Qwen2.5-Coder 32B is the coding model
- Hermes Agent is now active on the 5090 machine

## Rollback

If the 5090 migration needs to be reverted, switch back to the 4070 Ti profile:

```powershell
python scripts/switch_models.py --profile 4070ti
```

That restores:

- `models.main` to `qwen3:14b`
- `models.coder` to `qwen2.5-coder:14b`
