"""Stage 2 schema validators."""

from __future__ import annotations

from dataclasses import dataclass

from nlpcc.stage2_text_store.schema import (
    BLViewRecord,
    ConfidenceMatrix,
    DecayedEventMemory,
    EventTableRow,
    FlatFeatureRow,
    SectorGraphEdge,
    SectorImpactRow,
    Stage2TextState,
)


class Stage2ValidationError(ValueError):
    """Raised when Stage 2 state violates schema constraints."""


@dataclass(frozen=True)
class Stage2ValidationIssue:
    code: str
    message: str
    location: str | None = None


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> bool:
    return low <= value <= high


def validate_flat_feature(row: FlatFeatureRow, location: str) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if not row.feature_name:
        issues.append(Stage2ValidationIssue("missing_feature_name", "Flat feature row has no name.", location))
    if not _bounded(row.confidence):
        issues.append(Stage2ValidationIssue("invalid_confidence", "Flat feature confidence must be in [0, 1].", location))
    if row.source_count < 0:
        issues.append(Stage2ValidationIssue("invalid_source_count", "Flat feature source count is negative.", location))
    return issues


def validate_event_row(row: EventTableRow, location: str) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if not row.event_id:
        issues.append(Stage2ValidationIssue("missing_event_id", "Event row has no id.", location))
    if not row.news_id:
        issues.append(Stage2ValidationIssue("missing_news_id", "Event row has no news id.", location))
    if not row.sector:
        issues.append(Stage2ValidationIssue("missing_sector", "Event row has no sector.", location))
    if row.direction not in {"positive", "negative", "neutral"}:
        issues.append(Stage2ValidationIssue("invalid_direction", "Event row direction is invalid.", location))
    if not -1.0 <= row.signed_intensity <= 1.0:
        issues.append(Stage2ValidationIssue("invalid_signed_intensity", "Signed intensity must be in [-1, 1].", location))
    if not _bounded(row.confidence):
        issues.append(Stage2ValidationIssue("invalid_confidence", "Event row confidence must be in [0, 1].", location))
    if row.duplicate_count < 1:
        issues.append(Stage2ValidationIssue("invalid_duplicate_count", "Duplicate count must be positive.", location))
    return issues


def validate_bl_view(row: BLViewRecord, location: str) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if not row.view_id:
        issues.append(Stage2ValidationIssue("missing_view_id", "BL view record has no id.", location))
    if not row.asset_group:
        issues.append(Stage2ValidationIssue("missing_asset_group", "BL view record has no asset group.", location))
    if row.direction not in {"positive", "negative", "neutral"}:
        issues.append(Stage2ValidationIssue("invalid_direction", "BL view direction is invalid.", location))
    if not _bounded(row.confidence):
        issues.append(Stage2ValidationIssue("invalid_confidence", "BL view confidence must be in [0, 1].", location))
    if row.source_count < 1:
        issues.append(Stage2ValidationIssue("invalid_source_count", "BL view source count must be positive.", location))
    return issues


def validate_confidence_matrix(matrix: ConfidenceMatrix, location: str = "confidence_matrix") -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    size = len(matrix.labels)
    if len(matrix.values) != size:
        issues.append(Stage2ValidationIssue("invalid_matrix_shape", "Confidence matrix row count must match labels.", location))
    for row_index, row in enumerate(matrix.values):
        if len(row) != size:
            issues.append(
                Stage2ValidationIssue(
                    "invalid_matrix_shape",
                    "Confidence matrix must be square.",
                    f"{location}.values[{row_index}]",
                )
            )
        for col_index, value in enumerate(row):
            if not _bounded(value):
                issues.append(
                    Stage2ValidationIssue(
                        "invalid_matrix_value",
                        "Confidence matrix values must be in [0, 1].",
                        f"{location}.values[{row_index}][{col_index}]",
                    )
                )
    return issues


def validate_decayed_memory(memory: DecayedEventMemory, location: str = "decayed_memory") -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if memory.decay_half_life_days <= 0:
        issues.append(Stage2ValidationIssue("invalid_half_life", "Decay half-life must be positive.", location))
    if memory.event_count < 0:
        issues.append(Stage2ValidationIssue("invalid_event_count", "Event count must be non-negative.", location))
    return issues


def validate_sector_impact(row: SectorImpactRow, location: str) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if not row.sector:
        issues.append(Stage2ValidationIssue("missing_sector", "Sector impact row has no sector.", location))
    if row.direction not in {"positive", "negative", "neutral"}:
        issues.append(Stage2ValidationIssue("invalid_direction", "Sector impact direction is invalid.", location))
    if not -1.0 <= row.signed_intensity <= 1.0:
        issues.append(Stage2ValidationIssue("invalid_signed_intensity", "Sector signed intensity must be in [-1, 1].", location))
    if not _bounded(row.confidence):
        issues.append(Stage2ValidationIssue("invalid_confidence", "Sector impact confidence must be in [0, 1].", location))
    if row.evidence_count < 0:
        issues.append(Stage2ValidationIssue("invalid_evidence_count", "Evidence count must be non-negative.", location))
    return issues


def validate_sector_graph_edge(edge: SectorGraphEdge, location: str) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    if not edge.source or not edge.target:
        issues.append(Stage2ValidationIssue("missing_graph_node", "Sector graph edge must have source and target.", location))
    if not edge.relation:
        issues.append(Stage2ValidationIssue("missing_relation", "Sector graph edge must have relation.", location))
    if edge.weight < 0:
        issues.append(Stage2ValidationIssue("invalid_weight", "Sector graph edge weight must be non-negative.", location))
    if not _bounded(edge.confidence):
        issues.append(Stage2ValidationIssue("invalid_confidence", "Sector graph edge confidence must be in [0, 1].", location))
    return issues


def find_stage2_state_issues(state: Stage2TextState) -> list[Stage2ValidationIssue]:
    issues: list[Stage2ValidationIssue] = []
    seen_event_ids: set[str] = set()
    for index, row in enumerate(state.flat_features):
        issues.extend(validate_flat_feature(row, f"flat_features[{index}]"))
    for index, row in enumerate(state.event_table):
        issues.extend(validate_event_row(row, f"event_table[{index}]"))
        if row.event_id in seen_event_ids:
            issues.append(Stage2ValidationIssue("duplicate_event_id", "Event id appears more than once.", f"event_table[{index}]"))
        seen_event_ids.add(row.event_id)
    for index, row in enumerate(state.bl_views):
        issues.extend(validate_bl_view(row, f"bl_views[{index}]"))
    for index, row in enumerate(state.sector_impact_panel):
        issues.extend(validate_sector_impact(row, f"sector_impact_panel[{index}]"))
    for index, edge in enumerate(state.sector_graph_edges):
        issues.extend(validate_sector_graph_edge(edge, f"sector_graph_edges[{index}]"))
    issues.extend(validate_confidence_matrix(state.confidence_matrix))
    issues.extend(validate_decayed_memory(state.decayed_memory))
    return issues


def assert_valid_stage2_state(state: Stage2TextState) -> None:
    issues = find_stage2_state_issues(state)
    if issues:
        joined = "; ".join(f"{issue.code}@{issue.location}: {issue.message}" for issue in issues)
        raise Stage2ValidationError(joined)
