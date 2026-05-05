import json
import os
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prompts import AGENT_PROMPTS, GLOBAL_SYSTEM
from tools import dispatch_tool, get_audit_log, get_all_engagements, set_engagement

app = FastAPI(title="ApexAI Executive Search", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

TOOL_SCHEMAS = [
    {
        "name": "invoke_agent",
        "description": "Invoke a specialist sub-agent with a typed payload.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string", "enum": list(AGENT_PROMPTS.keys())},
                "payload": {"type": "object"},
                "engagement_id": {"type": "string"},
                "parallel_group_id": {"type": "string"},
            },
            "required": ["agent_name", "payload", "engagement_id"],
        },
    },
    {
        "name": "read_crm",
        "description": "Read from the connected ATS/CRM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "entity_type": {"type": "string", "enum": ["candidate", "client", "engagement", "note"]},
                "filters": {"type": "object"},
                "limit": {"type": "integer"},
            },
            "required": ["query", "entity_type"],
        },
    },
    {
        "name": "write_crm",
        "description": "Write or update entities in the CRM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string"},
                "operation": {"type": "string", "enum": ["CREATE", "UPDATE", "APPEND_NOTE"]},
                "payload": {"type": "object"},
                "engagement_id": {"type": "string"},
            },
            "required": ["entity_type", "operation", "payload", "engagement_id"],
        },
    },
    {
        "name": "search_enrichment",
        "description": "Multi-source candidate enrichment via licensed data partners.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_query": {"type": "object"},
                "depth": {"type": "string", "enum": ["LITE", "STANDARD", "DEEP"]},
                "source_preferences": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["entity_query", "depth"],
        },
    },
    {
        "name": "compliance_check",
        "description": "Mandatory guardrail — inspect content against jurisdictional rules.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "content_type": {"type": "string"},
                "jurisdictions": {"type": "array", "items": {"type": "string"}},
                "engagement_id": {"type": "string"},
            },
            "required": ["content", "content_type", "jurisdictions", "engagement_id"],
        },
    },
    {
        "name": "send_for_approval",
        "description": "Route a draft to consultant for approval. Never auto-sends.",
        "input_schema": {
            "type": "object",
            "properties": {
                "draft": {"type": "object"},
                "recipient": {"type": "string"},
                "channel": {"type": "string"},
                "approver_user_id": {"type": "string"},
                "engagement_id": {"type": "string"},
            },
            "required": ["draft", "recipient", "channel", "approver_user_id", "engagement_id"],
        },
    },
    {
        "name": "log_audit",
        "description": "Append-only audit log entry.",
        "input_schema": {
            "type": "object",
            "properties": {
                "engagement_id": {"type": "string"},
                "agent": {"type": "string"},
                "action": {"type": "string"},
                "inputs_hash": {"type": "string"},
                "output_hash": {"type": "string"},
                "timestamp": {"type": "string"},
            },
            "required": ["engagement_id", "agent", "action", "timestamp"],
        },
    },
    {
        "name": "get_engagement_state",
        "description": "Retrieve full current state of an engagement.",
        "input_schema": {
            "type": "object",
            "properties": {"engagement_id": {"type": "string"}},
            "required": ["engagement_id"],
        },
    },
    {
        "name": "update_engagement_state",
        "description": "Patch engagement state.",
        "input_schema": {
            "type": "object",
            "properties": {
                "engagement_id": {"type": "string"},
                "patch": {"type": "object"},
            },
            "required": ["engagement_id", "patch"],
        },
    },
    {
        "name": "web_search",
        "description": "Public-web search for org-chart reconstruction and talent surfacing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer"},
                "date_range": {"type": "string", "enum": ["LAST_7D", "LAST_30D", "LAST_12M", "ALL_TIME"]},
            },
            "required": ["query"],
        },
    },
]


# ── Models ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    engagement_id: str
    agent: str = "ORCHESTRATOR"
    message: str
    conversation_history: list = []


class EngagementRequest(BaseModel):
    client_name: str
    role_title: str
    codename: str
    jurisdictions: list = ["US-FED"]
    consultant_name: str = "Senior Consultant"


# ── Engagement Management ────────────────────────────────────────────────────

@app.post("/engagements")
async def create_engagement(req: EngagementRequest):
    eid = str(uuid.uuid4())[:8].upper()
    state = {
        "engagement_id": eid,
        "codename": req.codename,
        "client_name": req.client_name,
        "role_title": req.role_title,
        "current_stage": "INTAKE",
        "jurisdictions": req.jurisdictions,
        "consultant_name": req.consultant_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_pipeline": [],
        "success_profile": None,
    }
    set_engagement(eid, state)
    return state


@app.get("/engagements")
async def list_engagements():
    return list(get_all_engagements().values())


@app.get("/engagements/{engagement_id}")
async def get_engagement(engagement_id: str):
    all_eng = get_all_engagements()
    if engagement_id not in all_eng:
        raise HTTPException(404, "Engagement not found")
    return all_eng[engagement_id]


@app.get("/audit-log")
async def audit_log():
    return get_audit_log()


# ── Streaming Chat ───────────────────────────────────────────────────────────

async def _run_agent_stream(agent: str, messages: list) -> AsyncGenerator[str, None]:
    system_prompt = AGENT_PROMPTS.get(agent, AGENT_PROMPTS["ORCHESTRATOR"])

    current_messages = messages.copy()

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=current_messages,
        )

        # Stream text content
        full_text = ""
        tool_uses = []

        for block in response.content:
            if block.type == "text":
                full_text += block.text
                # Stream word by word
                for chunk in block.text.split(" "):
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk + ' '})}\n\n"
            elif block.type == "tool_use":
                tool_uses.append(block)
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name, 'input': block.input})}\n\n"

        if response.stop_reason == "end_turn" or not tool_uses:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            break

        # Handle tool use
        tool_results = []
        for tool_use in tool_uses:
            result = dispatch_tool(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result),
            })
            yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_use.name, 'result': result})}\n\n"

        # Continue conversation
        current_messages = current_messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    messages = req.conversation_history.copy()
    messages.append({"role": "user", "content": req.message})

    return StreamingResponse(
        _run_agent_stream(req.agent, messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Direct Agent Calls ───────────────────────────────────────────────────────

@app.post("/agents/{agent_name}/run")
async def run_agent(agent_name: str, body: dict):
    agent = agent_name.upper()
    if agent not in AGENT_PROMPTS:
        raise HTTPException(404, f"Agent {agent_name} not found")

    system_prompt = AGENT_PROMPTS[agent]
    prompt = body.get("prompt", "")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=system_prompt,
        tools=TOOL_SCHEMAS,
        messages=[{"role": "user", "content": prompt}],
    )

    # Handle tool use loop
    messages = [{"role": "user", "content": prompt}]
    while response.stop_reason == "tool_use":
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        tool_results = []
        for tu in tool_uses:
            result = dispatch_tool(tu.name, tu.input)
            tool_results.append({"type": "tool_result", "tool_use_id": tu.id, "content": json.dumps(result)})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

    text = " ".join(b.text for b in response.content if b.type == "text")
    return {"agent": agent, "response": text, "stop_reason": response.stop_reason}


@app.get("/agents")
async def list_agents():
    return [
        {"id": k, "name": k.replace("_", " ").title(), "stage": _agent_stage(k)}
        for k in AGENT_PROMPTS.keys()
    ]


def _agent_stage(agent: str) -> str:
    mapping = {
        "ORCHESTRATOR": "All Stages",
        "INTAKE": "Intake",
        "POSITION_SPEC": "Spec",
        "MARKET_MAPPER": "Mapping",
        "SOURCING": "Sourcing",
        "OUTREACH": "Outreach",
        "ASSESSMENT": "Assessment",
        "SUBMISSION": "Presentation",
        "REFERENCE": "Reference",
        "OFFER_COMP": "Offer",
        "ONBOARDING": "Onboarding",
        "COMPLIANCE": "All Stages",
    }
    return mapping.get(agent, "General")


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "agents": len(AGENT_PROMPTS)}


# Mount frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
