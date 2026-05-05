import json
import uuid
from datetime import datetime, timezone
from typing import Any

# In-memory stores
_engagements: dict = {}
_crm_data: dict = {"candidates": [], "clients": [], "engagements": [], "notes": []}
_audit_log: list = []


def dispatch_tool(tool_name: str, tool_input: dict) -> Any:
    """Route tool calls to their implementations."""
    handlers = {
        "invoke_agent": _invoke_agent,
        "read_crm": _read_crm,
        "write_crm": _write_crm,
        "search_enrichment": _search_enrichment,
        "compliance_check": _compliance_check,
        "send_for_approval": _send_for_approval,
        "log_audit": _log_audit,
        "get_engagement_state": _get_engagement_state,
        "update_engagement_state": _update_engagement_state,
        "web_search": _web_search,
    }
    handler = handlers.get(tool_name)
    if handler:
        return handler(tool_input)
    return {"error": f"Unknown tool: {tool_name}"}


def _invoke_agent(inp: dict) -> dict:
    return {
        "status": "queued",
        "agent": inp.get("agent_name"),
        "engagement_id": inp.get("engagement_id"),
        "parallel_group_id": inp.get("parallel_group_id"),
        "message": f"Agent {inp.get('agent_name')} invoked — results will be synthesized by Orchestrator.",
    }


def _read_crm(inp: dict) -> dict:
    entity_type = inp.get("entity_type", "candidate")
    results = _crm_data.get(entity_type + "s", [])
    query = inp.get("query", "").lower()
    if query:
        results = [r for r in results if query in json.dumps(r).lower()]
    return {"results": results[:inp.get("limit", 25)], "total": len(results)}


def _write_crm(inp: dict) -> dict:
    entity_type = inp.get("entity_type", "candidate")
    operation = inp.get("operation", "CREATE")
    payload = inp.get("payload", {})
    key = entity_type + "s"
    if operation == "CREATE":
        payload["id"] = str(uuid.uuid4())
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        _crm_data.setdefault(key, []).append(payload)
    elif operation == "APPEND_NOTE":
        _crm_data.setdefault("notes", []).append({
            "id": str(uuid.uuid4()),
            "engagement_id": inp.get("engagement_id"),
            "content": payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    return {"status": "ok", "operation": operation, "entity_type": entity_type}


def _search_enrichment(inp: dict) -> dict:
    eq = inp.get("entity_query", {})
    depth = inp.get("depth", "STANDARD")
    return {
        "status": "enrichment_complete",
        "depth": depth,
        "entity": eq,
        "note": "MOCK DATA — integrate People Data Labs / ZoomInfo / Crustdata for live enrichment.",
        "profile": {
            "name": eq.get("name", "Unknown"),
            "company": eq.get("company", "Unknown"),
            "career_ladder": [
                {"role": "VP Product", "company": eq.get("company", "TechCo"), "years": "2020–present",
                 "scope": "150-person org, $80M P&L", "source": "PRESS_RELEASE", "confidence": "MEDIUM"}
            ],
            "outcomes": ["Led $120M ARR product line (UNVERIFIED)"],
            "board_roles": [],
            "compensation_signal": {"base_range": "$280K–$320K", "source": "SECTOR_BENCHMARK_P50"},
            "risk_flags": [],
        }
    }


def _compliance_check(inp: dict) -> dict:
    content = inp.get("content", "")
    jurisdictions = inp.get("jurisdictions", [])
    issues = []
    prohibited_terms = [
        ("young", "EU AI Act / EEOC — age inference prohibited"),
        ("energetic", "EEOC — coded age language"),
        ("aggressive male", "EEOC — gender preference"),
        ("culture fit", "EEOC — may encode demographic bias without behavioral anchor"),
        ("emotion", "EU AI Act Art. 50 — emotion inference prohibited in hiring"),
    ]
    for term, rule in prohibited_terms:
        if term.lower() in content.lower():
            issues.append({"issue": f"Contains '{term}'", "rule_cited": rule,
                           "remediation": "Replace with observable behavioral indicator."})

    if "EU" in jurisdictions and "GDPR" not in content and len(content) > 100:
        issues.append({"issue": "No GDPR data-processing notice detected",
                       "rule_cited": "GDPR Art. 13/14",
                       "remediation": "Append candidate rights notice with lawful basis."})

    verdict = "BLOCKED" if issues else "APPROVED"
    return {
        "verdict": verdict,
        "edits": [],
        "blocks": issues,
        "audit_hash": str(uuid.uuid4())[:8],
        "jurisdictions_checked": jurisdictions,
    }


def _send_for_approval(inp: dict) -> dict:
    draft_id = str(uuid.uuid4())
    return {
        "status": "pending_approval",
        "draft_id": draft_id,
        "approver": inp.get("approver_user_id"),
        "channel": inp.get("channel"),
        "message": "Draft queued for consultant approval. No outbound action taken.",
    }


def _log_audit(inp: dict) -> dict:
    entry = {**inp, "log_id": str(uuid.uuid4()), "logged_at": datetime.now(timezone.utc).isoformat()}
    _audit_log.append(entry)
    return {"status": "logged", "log_id": entry["log_id"]}


def _get_engagement_state(inp: dict) -> dict:
    eid = inp.get("engagement_id")
    state = _engagements.get(eid)
    if not state:
        return {"error": f"Engagement {eid} not found"}
    return state


def _update_engagement_state(inp: dict) -> dict:
    eid = inp.get("engagement_id")
    patch = inp.get("patch", {})
    if eid not in _engagements:
        _engagements[eid] = {}
    _engagements[eid].update(patch)
    _engagements[eid]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"status": "updated", "engagement_id": eid}


def _web_search(inp: dict) -> dict:
    query = inp.get("query", "")
    return {
        "status": "mock_results",
        "query": query,
        "note": "MOCK — wire to SerpAPI / Brave Search / Tavily for live results.",
        "results": [
            {"title": f"Search result 1 for: {query}", "url": "https://example.com/1",
             "snippet": "Relevant executive profile and career history...", "date": "2025-01-15"},
            {"title": f"Search result 2 for: {query}", "url": "https://example.com/2",
             "snippet": "Board appointment and company announcement...", "date": "2025-03-02"},
        ]
    }


def get_audit_log() -> list:
    return _audit_log


def get_all_engagements() -> dict:
    return _engagements


def set_engagement(eid: str, state: dict):
    _engagements[eid] = state
