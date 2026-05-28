from pathlib import Path

from tools.verification.dependency_audit import audit_nlpcc_does_not_import_tools
from tools.verification.leakage_audit import audit_decision_metadata
from tools.verification.reproducibility_audit import hash_files, runtime_fingerprint
from tools.verification.submission_audit import audit_outputs_exist, audit_required_paths


def test_verification_audits_report_clean_baseline_and_detect_leakage_metadata() -> None:
    clean = {"decisions": [{"decision": {"metadata": {"forbidden_current_fields_used": []}}}]}
    dirty = {"decisions": [{"decision": {"metadata": {"forbidden_current_fields_used": ["close"]}}}]}

    assert audit_decision_metadata(clean) == []
    assert audit_decision_metadata(dirty)[0].code == "forbidden_current_fields_used"
    assert audit_required_paths(Path(".")) == []
    assert audit_outputs_exist(Path(".")) == []
    assert audit_nlpcc_does_not_import_tools(Path("src")) == []


def test_reproducibility_helpers_hash_files_and_runtime() -> None:
    hashes = hash_files([Path("README.md")])
    fingerprint = runtime_fingerprint()

    assert "README.md" in hashes
    assert "python" in fingerprint
