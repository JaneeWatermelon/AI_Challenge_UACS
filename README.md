# AI_Challenge_UACS
Project for AI Challenge 2026 which presenting AI Universal Cyber-Security Agent

We are writing an AI agent for the first time and didn't pay attention to OpenAI API and Pydantic-AI. So we wrote everything ourselves. Only after 2 weeks we started integrating this API. But we ended up with a good project, our own small API for the agent.

## Windows

```powershell
$env:PYTHONPATH="$PWD;$env:PYTHONPATH"; uv run harbor run -p local_task --agent-import-path agent.agent:MyInstalledAgent -m qwen/qwen3.6-35b-a3b --ae OPENAI_API_KEY=$env:OPENAI_API_KEY --ae OPENAI_BASE_URL=https://openrouter.ai/api/v1 -y
```

## Linux

```bash
PYTHONPATH="$PWD:$PYTHONPATH" uv run harbor run -p local_task --agent-import-path agent.agent:MyInstalledAgent -m qwen/qwen3.6-35b-a3b --ae OPENAI_API_KEY=$OPENAI_API_KEY --ae OPENAI_BASE_URL=https://openrouter.ai/api/v1 -y
```
