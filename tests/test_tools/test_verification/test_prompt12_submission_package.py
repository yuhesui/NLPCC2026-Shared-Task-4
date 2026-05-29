import json
from pathlib import Path
import zipfile
from uuid import uuid4

from tools.verification.submission_package import (
    audit_submission_archive,
    build_submission_package,
    collect_submission_files,
    validate_no_raw_data,
)


def test_prompt12_collect_submission_files_excludes_raw_data() -> None:
    files = collect_submission_files(Path("."))

    assert Path("src/nlpcc/__init__.py") in files
    assert validate_no_raw_data(files) == ()
    assert all("__pycache__" not in path.parts for path in files)


def test_prompt12_build_submission_package_writes_manifest_and_zip() -> None:
    output_root = Path("outputs/test_tools_prompt12/submissions")
    package_name = f"unit_candidate_package_{uuid4().hex}"
    result = build_submission_package(
        repo_root=Path("."),
        output_root=output_root,
        package_name=package_name,
        include_paths=(Path("src/nlpcc/__init__.py"), Path("README.md")),
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    audit = audit_submission_archive(result.archive_path)

    assert manifest["raw_data_excluded"] is True
    assert result.file_count == 2
    assert audit["issues"] == []
    with zipfile.ZipFile(result.archive_path, "r") as archive:
        names = set(archive.namelist())
    assert "SUBMISSION_MANIFEST.json" in names
    assert "src/nlpcc/__init__.py" in names
