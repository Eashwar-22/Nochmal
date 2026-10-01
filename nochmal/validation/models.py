"""Strict schemas for persisted semantic-review and audio evidence."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from nochmal.content.models import StrictModel


AuditKind = Literal["rulebook", "language", "translation-pedagogy"]
Verdict = Literal["pass", "fail", "manual-review"]


class AuditFinding(StrictModel):
    severity: Literal["error", "warning"]
    location: str
    rule: str
    message: str


class SemanticAudit(StrictModel):
    kind: AuditKind
    reviewer: str
    verdict: Verdict
    checks: list[str]
    findings: list[AuditFinding] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_consistent_verdict(self) -> "SemanticAudit":
        has_errors = any(item.severity == "error" for item in self.findings)
        if self.verdict == "pass" and has_errors:
            raise ValueError("A passing audit cannot contain error findings")
        if self.verdict == "fail" and not has_errors:
            raise ValueError("A failing audit requires at least one error finding")
        return self


class LessonReviewReport(StrictModel):
    schema_version: Literal[1]
    lesson_id: str
    source_sha256: str
    overall_verdict: Verdict
    audits: list[SemanticAudit]

    @model_validator(mode="after")
    def require_all_independent_scopes(self) -> "LessonReviewReport":
        kinds = [audit.kind for audit in self.audits]
        required: set[AuditKind] = {
            "rulebook",
            "language",
            "translation-pedagogy",
        }
        if set(kinds) != required or len(kinds) != len(required):
            raise ValueError("A review requires exactly one audit of every kind")
        if self.overall_verdict == "pass" and any(
            audit.verdict != "pass" for audit in self.audits
        ):
            raise ValueError("Every audit must pass before the report can pass")
        return self


class AudioManifest(StrictModel):
    draft_id: str
    status: str
    model_id: str
    voice_id: str
    sample_rate: int
    api_output_format: str
    stored_output_format: str
    pause_seconds: float
    sentence_files: list[str]
    sentence_texts: list[str]
    sentence_sha256: dict[str, str]
    paragraph_file: str
    paragraph_sha256: str
    paragraph_assembled_from_sentence_files: bool
