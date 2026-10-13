"""
FastAPI REST API Server for Rhabdomyolysis Aki Agent.
"""
import os
import hmac
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Rhabdomyolysis Aki Agent API",
    description="Illustrative rule checks, not a validated clinical risk score or treatment recommendation.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "rhabdomyolysis-aki-agent", "domain": "Nephrology & Dialysis Systems", "standard": "Demonstration only (not clinically validated)", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a potentially identifying value")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a potentially identifying value")


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_key: str = Header(default="", alias="X-Audit-Key")):
    key = os.environ.get("AUDIT_READ_TOKEN", "")
    if not key or not hmac.compare_digest(x_audit_key, key):
        raise HTTPException(status_code=403, detail="Audit key required")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
