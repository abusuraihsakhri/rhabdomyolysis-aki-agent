import pytest
from rhabdo_guard import CKClearanceKineticsAgent, McMahonRiskScorerAgent, UrineAlkalinizationAdvisorAgent, RhabdoCoordinator, main


def test_sub_agents():
    a1 = CKClearanceKineticsAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = McMahonRiskScorerAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = UrineAlkalinizationAdvisorAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_coordinator():
    coord = RhabdoCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from rhabdo_guard import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is False
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION

def test_advisory_not_labeled_normal():
    coord = RhabdoCoordinator()
    dossier = coord.audit_case({"status_text": "DISCORDANT"})
    assert dossier["overall_status"] == "ADVISORY_ACTIVE"
