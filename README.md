# ◈ ApexAI — Executive Intelligence Platform

End-to-end AI-augmented retained executive search system.

## Architecture

```
apexai/
├── backend/
│   ├── main.py          # FastAPI app — streaming, REST, agent routing
│   ├── prompts.py       # All 12 agent system prompts
│   └── tools.py         # Tool dispatchers (CRM, enrichment, compliance, audit)
├── frontend/
│   └── index.html       # Luxury dark single-page app
├── requirements.txt
└── start.sh
```

## Agents

| Agent | Stage | Purpose |
|-------|-------|---------|
| ORCHESTRATOR | All | Primary consultant interface, routes to specialist agents |
| INTAKE | Kickoff | Converts transcripts/JDs into success profiles (The Real Four) |
| POSITION_SPEC | Spec | 2-page narrative position specifications |
| MARKET_MAPPER | Mapping | Target universe: 20+ companies, 50–80 candidate longlist |
| SOURCING | Enrichment | Evidence-cited candidate dossiers |
| OUTREACH | Outreach | 3-touch personalized sequences (human approval required) |
| ASSESSMENT | Interviews | Interview kits + post-interview synthesis |
| SUBMISSION | Presentation | Client-ready 2-page candidate submissions |
| REFERENCE | Reference | Reference question design + call synthesis |
| OFFER_COMP | Offer | Market benchmarks + offer structure + negotiation map |
| ONBOARDING | Post-Place | 30/60/90/180-day check-in cadences |
| COMPLIANCE | All | EU AI Act, NYC LL144, EEOC, GDPR guardrails |

## Quick Start

```bash
export ANTHROPIC_API_KEY=sk-ant-...
chmod +x start.sh && ./start.sh
# Open http://localhost:8000
```

## API Endpoints

```
POST /engagements              Create new engagement
GET  /engagements              List all engagements
GET  /engagements/{id}         Get engagement state
POST /chat/stream              SSE streaming chat with any agent
POST /agents/{name}/run        Direct agent call (non-streaming)
GET  /agents                   List all agents
GET  /audit-log                Retrieve immutable audit log
GET  /health                   Health check
```

## Key Compliance Features

- **EU AI Act** — Blocks emotion inference, biometric categorization
- **NYC Local Law 144** — AEDT pre-use notice, independent bias audit requirement
- **Colorado SB24-205** — Impact assessments, appeal rights
- **Illinois AIVI Act** — Written consent for AI video analysis
- **EEOC / Title VII** — Protected-class inference prevention
- **GDPR** — Lawful basis, data minimization, candidate rights

## Wiring Live Integrations

Replace mock implementations in `backend/tools.py`:

| Tool | Integration |
|------|------------|
| `search_enrichment` | People Data Labs, Crustdata, ZoomInfo |
| `read_crm / write_crm` | Bullhorn, Invenias, Salesforce |
| `web_search` | Brave Search, Tavily, SerpAPI |
| `send_for_approval` | Slack, email, your review UI |

## Security Notes

- All outbound comms require explicit consultant approval (`send_for_approval`)
- Audit log is append-only
- Prompt injection from candidate/client content is explicitly blocked
- Candidate names never appear in subjects, titles, or filenames without authorization
