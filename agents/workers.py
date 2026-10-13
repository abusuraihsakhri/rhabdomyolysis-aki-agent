"""
Specialized Domain Worker Agents for Rhabdomyolysis Aki Agent.
Domain: Nephrology & Dialysis Systems
Standard: KDIGO / KDOQI Clinical Practice Guidelines
"""
import uuid
from typing import List
from .models import SystemTaskPayload, AgentAlert, UrgencyLevel


class InvariantQCWorker:
    """Worker 1: Illustrative primary-threshold check (not a clinical score)."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        if payload.primary_metric > 25.0:
            alerts.append(AgentAlert(
                alert_id=f"QC-{uuid.uuid4().hex[:6]}",
                origin_worker="InvariantQCWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Primary Metric Threshold Exceeded",
                technical_details=f"Primary measurement ({payload.primary_metric:.2f}) exceeds upper reference limit (25.00) (illustrative unitless threshold, not a KDIGO cutoff).",
                actionable_remediation="Review example inputs; do not use these checks for patient-care decisions.",
            ))
        return alerts


class SafetyEscalationWorker:
    """Worker 2: Example secondary-threshold and manual-priority check."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        if payload.is_critical_flag or payload.secondary_metric > 12.0:
            alerts.append(AgentAlert(
                alert_id=f"SAFE-{uuid.uuid4().hex[:6]}",
                origin_worker="SafetyEscalationWorker",
                urgency=UrgencyLevel.CRITICAL_STAT if payload.is_critical_flag else UrgencyLevel.ELEVATED,
                summary="Example Priority Check Triggered",
                technical_details=f"Manual priority flag={payload.is_critical_flag}; example secondary value={payload.secondary_metric:.2f} (unitless).",
                actionable_remediation="Review the synthetic input and independently assess any real clinical concerns.",
            ))
        return alerts


class ProtocolConformanceWorker:
    """Worker 3: Example keyword-based status descriptor check."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        desc_upper = str(payload.status_descriptor).upper()
        if any(w in desc_upper for w in ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]):
            alerts.append(AgentAlert(
                alert_id=f"CONF-{uuid.uuid4().hex[:6]}",
                origin_worker="ProtocolConformanceWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Protocol Conformance Discordance Detected",
                technical_details=f"Descriptor '{payload.status_descriptor}' matches an example status keyword (not clinical guideline conformance).",
                actionable_remediation="Review example descriptor and independently validate any domain-specific interpretation.",
            ))
        return alerts
