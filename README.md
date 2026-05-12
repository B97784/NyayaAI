# Nyāya: A Multi-Agent Legal Assistant for Indian Law ⚖️🇮🇳
A B.Tech Major Project (Jan–May 2026)
School of Computer Science, UPES Dehradun

## 📌 Overview
Nyāya (न्याय) is a multi-agent AI legal assistant tailored for the Indian legal system. It uses an orchestrator model that dispatches incoming briefs to five specialist sub-agents — Client Intake, Legal Research, Case Strategy, Legal Drafting, and Compliance & Contract Review. The system cites Indian statutes (BNS 2023, BNSS 2023, Constitution, Indian Contract Act, IT Act, DPDP Act 2023) and produces court-ready outputs such as FIR drafts, legal notices, plaints, writ petitions, and compliance memos.

## Architecuture<img width="1536" height="1024" alt="WhatsApp Image 2026-05-11 at 11 58 44" src="https://github.com/user-attachments/assets/04a5b8b8-9fd6-4680-94fb-522084b2a941" />


## ✨ Features
- Five role-specialised sub-agents orchestrated by a router model (built on Mastra)
- Indian-jurisdiction-first: BNS, BNSS, Constitution, Contract Act, IT Act, DPDP, Consumer Protection
- Retrieval-augmented generation over a curated corpus of statutes and compliance rules
- Per-user accounts with bcrypt-hashed passwords, cookie-based sessions
- Persistent chat history (SQLite) — every brief is saved per user
- Server-sent-events streaming with a live agent-flow timeline in the UI
- Markdown rendering of judgments, drafts, and clause-by-clause review
- Offline evaluation harness with confusion-matrix-based scoring

## 🧠 Problem Statement
Legal services in India are gated by cost, jargon, and delay. While LLMs can produce useful first-pass drafts, a single prompt-and-respond model conflates the very different skills of (a) extracting facts, (b) finding the right statute, (c) recommending strategy, and (d) producing court-format output. Nyāya decomposes this workflow into five specialist agents and routes every query through an orchestrator, giving auditable, agent-attributed responses that cite Indian statutes correctly and refuse to dispense legal advice without a disclaimer.

## 📊 Performance
| Metric | Single-prompt baseline | Multi-agent (Nyāya) | Improvement |
|---|---:|---:|---:|
| Routing accuracy | 64.2% | **91.7%** | +27.5% |
| Tool-call accuracy | — | **92.5%** | — |
| Citation accuracy (n=60) | 71.8% | **88.3%** | +16.5% |
| Hallucination rate | 12.4% | **4.2%** | −8.2% |
| Macro F1 (sub-agent routing) | — | **0.92** | — |
| Disclaimer compliance | 18% | **100%** | +82% |

Per-agent classification (test set: 240 cases):

| Sub-agent | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Client Intake | 0.92 | 0.89 | 0.90 | 36 |
| Legal Research | 0.94 | 0.91 | 0.92 | 58 |
| Case Strategy | 0.88 | 0.85 | 0.86 | 42 |
| Legal Drafting | 0.96 | 0.93 | 0.94 | 54 |
| Compliance Review | 0.93 | 0.95 | 0.94 | 50 |
| **Macro avg** | **0.93** | **0.91** | **0.92** | **240** |

Latency: **mean 18.4 s**, **p95 47.1 s** on commodity hardware.

## ⚙️ System Architecture
The pipeline consists of:

1. **Frontend** — minimal HTML/CSS/JS chat UI with a live agent-flow timeline
2. **Backend (FastAPI)** — auth, session management, SQLite persistence, SSE streaming
3. **Orchestrator (Mastra)** — main routing model that decides which specialist to invoke
4. **Sub-agents** — five role-specialised agents (Intake, Research, Strategy, Drafting, Compliance)
5. **Knowledge Retrieval (in-process MCP)** — `retrieve_legal_docs` and `retrieve_compliance_rules` tools over curated JSON corpora (BNS, BNSS, Constitution, DPDP, IT Rules, etc.)
6. **Evaluation harness** — offline scorer that runs labelled cases and reports precision/recall/F1 per sub-agent

📸 *See `ARCHITECTURE.md` for the full Mermaid flow + sequence diagrams.*

## 🛠️ Tech Stack
- **Orchestrator framework:** Mastra
- **Backend:** Python · FastAPI · uvicorn · SSE
- **Persistence:** SQLite (users, chats, messages)
- **Auth:** bcrypt + itsdangerous (signed cookie sessions)
- **Frontend:** Vanilla HTML/CSS/JS · marked.js · DOMPurify · Cormorant Garamond + Inter
- **Knowledge Retrieval:** in-process MCP tools over JSON corpora
- **Container:** Docker / docker-compose

## 🧪 Evaluation Metrics
- **Routing accuracy** — Was the correct sub-agent invoked for the query type?
- **Tool-call accuracy** — Was the right retrieval tool used when one was expected?
- **Precision / Recall / F1** — Per sub-agent classification, plus macro and weighted averages
- **Citation accuracy** — Manual sample of statute citations checked against ground truth
- **Hallucination rate** — Fraction of fabricated section numbers or case names
- **Disclaimer compliance** — Every response ends with the required disclaimer

📸 *Confusion matrix and full breakdown in `evals/results.md`.*

## 📈 Future Scope
- Native Indian-language interface (Hindi, Bengali, Marathi, Tamil) — voice + text
- Live retrieval over Indian case law databases (IndianKanoon, SCC Online, Manupatra)
- Integration with court e-filing portals (eCourts, NJDG)
- Vakalatnama generation and digital signature workflow
- Citation verification layer to drive the hallucination rate below 1%
- Mobile app for advocates with offline draft review

## Contact
For any inquiries or feedback, please contact:

**Name:** Deepanshu Miglani
**Education:** B.Tech CSE(AIML), UPES, Dehradun
**Email:** deepanshumiglani0408@gmail.com / Deepanshu.106264@stu.upes.ac.in
**GitHub:** deepanshum0408

**Name:** Divi Saxena
**Education:** B.Tech CSE(AIML), UPES, Dehradun
**Email:** divisaxena04@gmail.com / Divi.107784@stu.upes.ac.in
**GitHub:** Divi-Saxena

**Name:** Ayesha Varshney
**Education:** B.Tech CSE(AIML), UPES, Dehradun
**Email:** ayeshavarshney245@gmail.com
*


**Name:** Deepali Rana
**Education:** B.Tech CSE(AIML), UPES, Dehradun
**Email:** ranadeepali45@gmail.com


## Mentor
**Dr. Sahinur Rahman Laskar**
Assistant Professor (Senior Scale)
School of Computer Science, UPES, Dehradun, India
**Email:** sahinurlaskar.nits@gmail.com / sahinur.laskar@ddn.upes.ac.in

## Citation
@misc{nyayaai2026,
  title={NyayaAI: An AI-Powered Legal Assistant Using Multi-Agent Architecture and Retrieval-Augmented Generation},
  author={Deepanshu Miglani and Divi Saxena and Deepali Rana and Ayesha Varshney and Sahinur Rahman Laskar},
  year={2026},
  eprint={7577341},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2605.10155}
}
