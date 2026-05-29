from pathlib import Path

from tools.verification.verification_suite import (
    run_doc_policy_audit,
    run_import_audit,
    run_raw_data_immutability_audit,
    write_verification_outputs,
)


def test_prompt11_import_audit_checks_src_modules() -> None:
    report = run_import_audit(Path("src"))

    assert report["checked"] > 0
    assert report["failures"] == []


def test_prompt11_doc_policy_audit_accepts_current_layout_policy() -> None:
    report = run_doc_policy_audit((Path("README.md"), Path("AGENTS.md"), Path("docs/architecture")))

    assert report["policy_confirmed"]["README.md"] is True
    assert report["policy_confirmed"]["AGENTS.md"] is True
    assert report["issues"] == []


def test_prompt11_raw_data_audit_checks_manifest_hashes() -> None:
    report = run_raw_data_immutability_audit(Path("data/sample"))

    assert "issues" in report
    assert report["issues"] == []


def test_prompt11_verification_outputs_are_written() -> None:
    root = Path("outputs/test_tools_prompt11/verification")
    paths = write_verification_outputs(
        {
            "import_audit": {"checked": 1, "failures": []},
            "dependency_boundary_audit": {"issues": []},
            "leakage_audit": {"checked_files": [], "issues": []},
            "official_local_audit": {"server_probe": {"status": "blocked", "blocker": "not running"}},
            "raw_data_immutability_audit": {"checked_count": 0, "issues": []},
            "doc_policy_audit": {"issues": []},
            "submission_audit": {"issues": []},
            "reproducibility_audit": {"runtime": {}, "hashes": {}},
        },
        output_dir=root,
    )

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()
