# AI_Challenge_UACS
Project for AI Challenge 2026 which presenting AI Universal Cyber-Security Agent

## Windows
$env:PYTHONPATH="$PWD;$env:PYTHONPATH"; uv run harbor run `
  -p local_task `
  --agent-import-path agent.agent:MyInstalledAgent `
  -m qwen/qwen3.6-35b-a3b `
  --ae OPENAI_API_KEY=$env:OPENAI_API_KEY `
  --ae OPENAI_BASE_URL=https://openrouter.ai/api/v1  `
  -y

## Linux
PYTHONPATH="$PWD:$PYTHONPATH" uv run harbor run -p local_task --agent-import-path agent.agent:MyInstalledAgent -m qwen/qwen3.6-35b-a3b --ae OPENAI_API_KEY=$OPENAI_API_KEY --ae OPENAI_BASE_URL=https://openrouter.ai/api/v1 -y