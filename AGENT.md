# Universal Cybersecurity Agent

This project is an autonomous cybersecurity agent for the Universal Agent Competition.

The agent receives a task instruction and must solve it autonomously inside an isolated `secureintelligent/acp` runtime using a local LLM and local tools.

## Task Types

The closed benchmark contains:

* Vulnerability discovery
* Digital forensics
* Security fixes / SWE-bench-style tasks
* CTF tasks

`local_task/` contains examples for development only. Do not hard-code solutions for them.

## Runtime

The evaluator runs:

```sh
./run.sh "<task instruction>"
```

Submission must be a `.zip` ≤ 10 MB and contain at least:

```text
run.sh
```

Additional files can be included next to it.

`agent/agent.py` is the competition-provided Harbor wrapper and will be overwritten. Agent logic must be started from `run.sh`.

Runtime:

* Docker image: `secureintelligent/acp:latest`
* Python 3.12
* No internet access
* No runtime dependency installation

Use only dependencies available in the runtime or included in the submission.

## LLM

LLM connection is provided through:

```text
LOCAL_AGENT_MODEL
OPENAI_BASE_URL
OPENAI_API_KEY
```

Do not use external APIs or internet access.

Optimize for both task success and token usage.

## Agent Workflow

Use an iterative loop:

```text
Task → inspect → reason → act → observe → verify → answer
```

Prefer deterministic tools for mechanical work:

```text
rg, find, grep, sed, awk, git, diff, python, pytest,
curl, jq, openssl, tcpdump
```

For large repositories/files, search first and send only relevant content to the LLM.

Avoid unnecessary LLM calls, huge contexts, redundant actions, and unbounded loops.

## Task Guidelines

### Vulnerability Discovery

Trace input → dangerous operation → exploitability. Report confirmed findings rather than speculation.

### Forensics

Search and correlate logs/artifacts, build a timeline, and verify conclusions against evidence.

### Security Fixes

Identify root cause → make minimal fix → run relevant tests → inspect diff.

### CTF

Enumerate the attack surface → test targeted hypotheses → verify the result.

## Reliability

Any crash, timeout, incorrect result, or failed verification means `0` for the task.

Therefore:

* Bound LLM/tool calls and retries.
* Use subprocess timeouts.
* Handle expected command failures.
* Verify important results before finishing.
* Never depend on network connectivity.

## Evaluation

Each task receives `0` or `1`.

Leaderboard priority:

1. Number of solved tasks
2. Fewer LLM tokens
3. Less execution time

Primary objective:

> Maximize the number of reliably solved unseen tasks within the task's time and token budget.
