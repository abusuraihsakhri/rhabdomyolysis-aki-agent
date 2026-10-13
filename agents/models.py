"""
Pydantic v2 schemas and data definitions for Rhabdomyolysis Aki Agent.
Domain: Nephrology & Dialysis Systems
Standard: Illustrative software rules only; not clinically validated
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier", min_length=1, max_length=128)
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target", min_length=1, max_length=128)
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor", max_length=64)
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_metric_finite(cls, v: float) -> float:
        """Ensure metric values are finite numbers within clinical bounds."""
        import math
        if not math.isfinite(v):
            raise ValueError("Metric value must be a finite number (not NaN or Infinity)")
        if abs(v) > 1_000_000:
            raise ValueError("Metric value exceeds maximum allowed magnitude (1,000,000)")
        return v

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def validate_no_control_chars(cls, v: str) -> str:
        """Prevent control characters in string fields."""
        if any(ord(c) < 32 and c not in "\t\n\r" for c in v):
            raise ValueError("Field contains invalid control characters")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "Illustrative software checks; no clinical validation"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "rhabdomyolysis-aki-agent"
    domain: str = "Nephrology & Dialysis Systems"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "Illustrative software checks; no clinical validation"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
