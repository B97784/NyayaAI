# Legal Multi-Agent System

A 5-agent legal assistant built on the **Claude Agent SDK** (Python).

```
Frontend (HTML/JS)
      │
      ▼
Backend (FastAPI, SSE)
      │
      ▼
Main Orchestrator  ──► Task tool ──► 5 specialist sub-agents
      │                                │
      └────────────► Fake RAG ◄────────┘
                  (legal docs + compliances)
```

## Sub-agents

| Agent | Purpose | Tools |
|---|---|---|
| `legal-research` | Find statutes, case law, templates | `retrieve_legal_docs` |
| `case-strategy` | Recommend approach (sue/settle/negotiate) | — |
| `legal-drafting` | Draft NDAs, contracts, letters, motions | `retrieve_legal_docs` |
| `compliance-review` | Review against GDPR/HIPAA/SOC2/CCPA/PCI | `retrieve_compliance_rules` |
| `client-intake` | Plain-English fact gathering | — |

## Run locally

```bash
cp .env.example .env
# put your ANTHROPIC_API_KEY in .env
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code     # SDK spawns this CLI
uvicorn server:app --reload
```

Open <http://localhost:8000>.

## Run with Docker

```bash
cp .env.example .env
# put your ANTHROPIC_API_KEY in .env
docker compose up --build
```

Open <http://localhost:8000>.

## Run evals

```bash
python -m evals.run_evals
```

Prints a markdown table of which sub-agent + tool fired per case.

## Layout

```
server.py             FastAPI app + SSE
agents/
  orchestrator.py     ClaudeSDKClient with 5 subagents
  prompts.py          system prompts
  tools.py            fake RAG @tool fns + MCP server
data/                 stub corpora (legal_docs, compliances)
static/               HTML + JS frontend
evals/                cases.jsonl + run_evals.py
```

## Notes

- The "RAG" is a keyword scan over hardcoded JSON — no embeddings.
- The `claude-agent-sdk` requires the `claude` CLI to be on `$PATH` (provided by `@anthropic-ai/claude-code`). The Dockerfile installs it.
- Output is informational, not legal advice.
