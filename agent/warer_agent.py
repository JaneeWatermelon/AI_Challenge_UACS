import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.run import AgentRunResultEvent
from pydantic_ai.usage import UsageLimits

from utils.environment import Environment, EnvKeys

@dataclass(frozen=True)
class LocalAgentDeps:
    workdir: Path

async def _run_bash(command: str, workdir: Path) -> str:
    _log_event("tool_call", tool="bash", command=command, cwd=str(workdir))
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=str(workdir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    out = stdout.decode("utf-8", errors="replace")
    err = stderr.decode("utf-8", errors="replace")
    result = _truncate(
        f"$ {command}\n"
        f"[cwd] {workdir}\n"
        f"[exit_code] {proc.returncode}\n"
        f"[stdout]\n{out or '<empty>'}\n"
        f"[stderr]\n{err or '<empty>'}"
    )
    _log_event(
        "tool_result",
        tool="bash",
        exit_code=proc.returncode,
        stdout=out or "<empty>",
        stderr=err or "<empty>",
    )
    return result


async def _read_file(path: str, workdir: Path) -> str:
    _log_event("tool_call", tool="read_file", path=path)
    file_path = _resolve_path(path, workdir)
    if not file_path.exists():
        result = f"File not found: {file_path}"
        _log_event("tool_result", tool="read_file", result=result)
        return result
    if not file_path.is_file():
        result = f"Not a file: {file_path}"
        _log_event("tool_result", tool="read_file", result=result)
        return result
    result = _truncate(await asyncio.to_thread(file_path.read_text, encoding="utf-8"))
    _log_event("tool_result", tool="read_file", path=path, result=result)
    return result


async def _apply_diff(path: str, diff_content: str, workdir: Path) -> str:
    _log_event("tool_call", tool="apply_diff", path=path, diff=diff_content)
    file_path = _resolve_path(path, workdir)
    if not file_path.exists():
        result = f"File not found: {file_path}"
        _log_event("tool_result", tool="apply_diff", result=result)
        return result
    if not file_path.is_file():
        result = f"Not a file: {file_path}"
        _log_event("tool_result", tool="apply_diff", result=result)
        return result
    result = _truncate(await _apply_unified_diff(file_path, diff_content))
    _log_event("tool_result", tool="apply_diff", path=path, result=result)
    return result


async def _append_file(path: str, content: str, workdir: Path) -> str:
    _log_event("tool_call", tool="append_file", path=path, content=content)
    file_path = _resolve_path(path, workdir)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_append_text, file_path, content)
    result = f"Appended {len(content)} chars to {file_path}"
    _log_event("tool_result", tool="append_file", path=path, result=result)
    return result

class WarerAgent:

    # def __new__(cls):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(WarerAgent, cls).__new__(cls)
    #     return cls.instance

    def __init__(self):
        model_name = Environment.get(EnvKeys.LOCAL_AGENT_MODEL)
        base_url = Environment.get(EnvKeys.OPENAI_BASE_URL)
        api_key = Environment.get(EnvKeys.OPENAI_API_KEY)
        self._agent = Agent(
            OpenAIChatModel(
                model_name,
                provider=OpenAIProvider(
                    base_url=base_url,
                    api_key=api_key,
                ),
            ),
            deps_type=LocalAgentDeps,
            system_prompt=(
                "You are a non-interactive coding agent. "
                "Complete the user's request autonomously. "
                "Use tools to inspect files, run commands, and apply focused diffs. "
                "Work in concise steps and explain what you changed in the final response."
            ),
        )

    @property
    def agent(self) -> Agent[LocalAgentDeps, str]:
        return self._agent

    @agent.tool
    async def bash(ctx: RunContext[LocalAgentDeps], command: str) -> str:
        return await _run_bash(command, ctx.deps.workdir)

    @agent.tool
    async def read_file(ctx: RunContext[LocalAgentDeps], path: str) -> str:
        return await _read_file(path, ctx.deps.workdir)

    @agent.tool
    async def apply_diff(
        ctx: RunContext[LocalAgentDeps], path: str, diff_content: str
    ) -> str:
        return await _apply_diff(path, diff_content, ctx.deps.workdir)

    @agent.tool
    async def append_file(
        ctx: RunContext[LocalAgentDeps], path: str, content: str
    ) -> str:
        return await _append_file(path, content, ctx.deps.workdir)