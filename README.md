# AI_Challenge_UACS
Project for AI Challenge 2026 which presenting AI Universal Cyber-Security Agent

uv run harbor run 
-p local_task 
--agent-import-path agent.agent:MyInstalledAgent 
-m qwen/qwen3.6-35b-a3b 
--ae OPENAI_API_KEY=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 
--ae OPENAI_BASE_URL=https://openrouter.ai/api/v1 
-y

uv run harbor run `
  -p local_task `
  --agent agent.agent:MyInstalledAgent `
  -m qwen/qwen3.6-35b-a3b `
  --ae OPENAI_API_KEY=$env:OPENAI_API_KEY `
  --ae OPENAI_BASE_URL=https://openrouter.ai/api/v1  `
  -y
