"""One entry point for numbered course candidate, audit, and release work.

This command never changes the curriculum blueprint. Creation and audit leave
the published app untouched; publication is a separate explicit action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_AUDIT_MODEL = os.environ.get("NOCHMAL_AUDIT_MODEL", "gpt-6.1-sol")
DEFAULT_AUDIT_REASONING_EFFORT = os.environ.get("NOCHMAL_AUDIT_REASONING_EFFORT", "high")

from nochmal.content.candidates import (  # noqa: E402
    candidate_directory,
    load_candidate_artifact,
    load_candidate_source,
    source_path,
)
from nochmal.content.course_paths import (  # noqa: E402
    authored_root,
    blueprint_path,
    candidate_audio_root,
    course_level,
    course_number,
    published_audio_root,
    published_root,
)
from nochmal.content.source_models import CourseLessonSource  # noqa: E402
from nochmal.validation.models import LessonReviewReport  # noqa: E402
from nochmal.workflows.publish_candidate import load_passing_review, load_verified_audio  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


PREFLIGHT_INPUTS = (
    "nochmal",
    "scripts",
    "tests",
    "docs/grammar-breakdown-rulebook.md",
    "docs/lesson-format.md",
)


def tree_digest(paths: tuple[str, ...] = PREFLIGHT_INPUTS) -> str:
    """Hash the code and rules covered by the recorded full-suite result."""
    hasher = hashlib.sha256()
    for relative in paths:
        path = ROOT / relative
        files = [
            path
        ] if path.is_file() else sorted(
            item for item in path.rglob("*")
            if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc"
        )
        for item in files:
            name = item.relative_to(ROOT).as_posix().encode("utf-8")
            hasher.update(len(name).to_bytes(4, "big"))
            hasher.update(name)
            contents = item.read_bytes()
            hasher.update(len(contents).to_bytes(8, "big"))
            hasher.update(contents)
    return hasher.hexdigest()


def preflight_path(identifier: str) -> Path:
    return candidate_directory(identifier) / "preflight.json"


def preflight_inputs(identifier: str) -> dict[str, str]:
    return {
        "lesson_id": identifier,
        "source_sha256": digest(source_path(identifier)),
        "compiled_lesson_sha256": digest(candidate_directory(identifier) / "compiled-lesson.json"),
        "review_sha256": digest(candidate_directory(identifier) / "review.json"),
        "suite_inputs_sha256": tree_digest(),
    }


def run_preflight(identifiers: list[str]) -> None:
    """Run the complete suite once and bind its passing result to candidates."""
    for identifier in identifiers:
        passing_review(identifier)
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")
    timestamp = datetime.now(timezone.utc).isoformat()
    for identifier in identifiers:
        receipt = {**preflight_inputs(identifier), "passed_at": timestamp}
        preflight_path(identifier).write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Recorded full-suite preflight for {identifier}")


def require_preflight(identifier: str) -> None:
    path = preflight_path(identifier)
    if not path.is_file():
        raise ValueError(
            "Full-suite preflight is missing; run "
            f"scripts/lesson_flow.py preflight {identifier}"
        )
    receipt = json.loads(path.read_text(encoding="utf-8"))
    expected = preflight_inputs(identifier)
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError(
            "Full-suite preflight is stale; rerun "
            f"scripts/lesson_flow.py preflight {identifier}"
        )


def run_process(
    command: list[str], *, input_text: str | None = None, log_path: Path | None = None
) -> None:
    """Run a command, optionally duplicating its terminal output into a log."""
    display = "+ " + " ".join(command)
    print(display, flush=True)
    if log_path is None:
        subprocess.run(command, input=input_text, text=True, cwd=ROOT, check=True)
        return

    with log_path.open("a", encoding="utf-8") as log:
        log.write(display + "\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if input_text is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=ROOT,
        )
        if input_text is not None:
            assert process.stdin is not None
            process.stdin.write(input_text)
            process.stdin.close()
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        if process.wait() != 0:
            raise subprocess.CalledProcessError(process.returncode, command)


def run(*args: str, log_path: Path | None = None) -> None:
    run_process(list(args), log_path=log_path)


def step(name: str, *args: str, log_path: Path | None = None) -> None:
    """Run an internal workflow step; users invoke only this command."""
    run(sys.executable, "-m", f"nochmal.workflows.{name}", *args, log_path=log_path)


def lesson_id(value: str) -> str:
    try:
        level = course_level(value)
        number = course_number(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    if "-course-" not in value or not 1 <= number <= 999:
        raise argparse.ArgumentTypeError(
            "Expected a course lesson ID such as a2-course-013 or b1-course-001"
        )
    return f"{level}-course-{number:03d}"


def authored_record(identifier: str) -> CourseLessonSource:
    matches: list[CourseLessonSource] = []
    root = authored_root(identifier) / "lessons"
    for path in sorted(root.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload if isinstance(payload, list) else [payload]:
            if item.get("id") == identifier:
                matches.append(CourseLessonSource.model_validate(item))
    if len(matches) != 1:
        raise ValueError(f"Expected one authored record for {identifier}; found {len(matches)}")
    return matches[0]


def published_ids(identifier: str) -> set[str]:
    path = published_root(identifier) / "publication.json"
    if not path.is_file():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8"))["published_lesson_ids"])


def passing_review(identifier: str) -> LessonReviewReport:
    source = load_candidate_source(identifier)
    load_candidate_artifact(identifier)
    return load_passing_review(identifier, source)


def prepare(identifier: str) -> None:
    if identifier in published_ids(identifier):
        raise ValueError(f"{identifier} is already published; preparation cannot replace it")
    path = source_path(identifier)
    if path.exists():
        print(f"{identifier}: existing candidate source preserved")
    else:
        record = authored_record(identifier)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{identifier}: copied authored source into an unpublished candidate")
    step("build_lesson_candidate", identifier)


AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_verdict": {"type": "string", "enum": ["pass", "fail", "manual-review"]},
        "audits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["rulebook", "language", "translation-pedagogy"]},
                    "verdict": {"type": "string", "enum": ["pass", "fail", "manual-review"]},
                    "checks": {"type": "array", "items": {"type": "string"}},
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string", "enum": ["error", "warning"]},
                                "location": {"type": "string"},
                                "rule": {"type": "string"},
                                "message": {"type": "string"},
                            },
                            "required": ["severity", "location", "rule", "message"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["kind", "verdict", "checks", "findings"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["overall_verdict", "audits"],
    "additionalProperties": False,
}


def audit(
    identifier: str,
    *,
    model: str,
    reasoning_effort: str = "high",
    log_path: Path | None = None,
) -> bool:
    source = load_candidate_source(identifier)
    load_candidate_artifact(identifier)
    source_hash = digest(source_path(identifier))
    blueprint = blueprint_path(identifier)
    blueprint_instruction = (
        f"Read the exact Lesson {course_number(identifier)} entry in {blueprint.relative_to(ROOT)}, then "
        if blueprint.is_file()
        else "No blueprint exists for this level yet; use the candidate source as the curriculum scope, then "
    )
    prompt = f"""Independently audit {identifier} in this repository. You are the reviewer, not the author.
Read docs/grammar-breakdown-rulebook.md and docs/lesson-format.md in full, then {blueprint_instruction}the candidate's
lesson-source.json, compiled-lesson.json, and preview.md. Inspect every sentence token
left to right and every word/phrase card, visible form change, case trigger, full
verb/inflection reference, translation, and blueprint constraint. Check repeated
forms, source order, and unsupported guesses. Perform three separate scopes:
rulebook, German language, and translation-pedagogy. Give exact sentence/card
locations and actionable findings. Use manual-review if you cannot establish a
fact. Return pass only if all three scopes pass with no error findings. Do not
edit files, launch another agent, call lesson_flow.py audit, generate audio,
publish, or deploy. Ignore any existing review.json verdict. Return only the
requested JSON. This is the pre-audio candidate audit: pending audio, absent
audio paths, and later live desktop/mobile release inspection are expected at
this stage. Record them as non-blocking warnings under a passing rulebook scope;
do not return manual-review solely because those later release gates remain.
Use manual-review only for a candidate-content fact required by this audit that
cannot be established from the supplied source, compiled artifact, preview, or
repository tests.

The candidate source schema uses `sentences`, with `de` for German and `en` for
English; it does not have `text`, `natural_meaning`, or `breakdown_groups` fields.
Inspect it in small sections with `rg`/`sed` (or first inspect its keys) rather than
using a fixed `jq` projection for a different schema. Use the compiled artifact and
preview for generated cards. Do not return a placeholder JSON before completing the
three scopes: your final response must be the audit result.
"""
    with tempfile.TemporaryDirectory(prefix="nochmal-audit-") as temp:
        schema = Path(temp) / "schema.json"
        output = Path(temp) / "result.json"
        schema.write_text(json.dumps(AUDIT_SCHEMA), encoding="utf-8")
        command = [
            "codex", "exec", "-C", str(ROOT), "--ephemeral", "--sandbox", "read-only",
            "--model", model, "--config", f"model_reasoning_effort={reasoning_effort}",
            "--output-schema", str(schema), "--output-last-message", str(output), "-",
        ]
        run_process(command, input_text=prompt, log_path=log_path)
        result = json.loads(output.read_text(encoding="utf-8"))
    if digest(source_path(identifier)) != source_hash:
        raise ValueError("Candidate source changed during its audit; discard the result and rerun")
    report = LessonReviewReport.model_validate({
        "schema_version": 1,
        "lesson_id": identifier,
        "source_sha256": source_hash,
        "overall_verdict": result["overall_verdict"],
        "audits": [
            {**entry, "reviewer": f"{model} {reasoning_effort}, independent Codex audit"}
            for entry in result["audits"]
        ],
    })
    path = candidate_directory(identifier) / "review.json"
    path.write_text(json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{identifier}: {report.overall_verdict}; saved {path}")
    return report.overall_verdict == "pass"


def rebuild_after_repair_if_needed(identifier: str, *, log_path: Path | None = None) -> bool:
    """Rebuild once when an agent's final source edit outlives its own build."""
    try:
        load_candidate_artifact(identifier)
        return False
    except ValueError as error:
        stale_artifact_errors = (
            "compiled artifact does not match the deterministic compiler output",
            "candidate source changed after the compiled artifact was built",
        )
        if not any(message in str(error) for message in stale_artifact_errors):
            raise
        print(f"{identifier}: final candidate changed after its build; rebuilding automatically")
        step("build_lesson_candidate", identifier, log_path=log_path)
        load_candidate_artifact(identifier)
        return True


def audio(identifier: str) -> None:
    source = load_candidate_source(identifier)
    passing_review(identifier)
    authored = authored_record(identifier)
    if [(s.de, s.en) for s in source.sentences] != [(s.de, s.en) for s in authored.sentences]:
        raise ValueError("Candidate and authored passage differ; reconcile before generating audio")
    step("generate_staged_elevenlabs_audio", source.source_draft_id)
    step("attach_candidate_audio", identifier)
    passing_review(identifier)


def audio_manifest_path(identifier: str) -> Path:
    return candidate_audio_root(identifier) / identifier / "manifest.json"


def review_findings(identifier: str) -> str:
    """Give the chat editor a short, precise repair list from a failed audit."""
    report = LessonReviewReport.model_validate_json(
        (candidate_directory(identifier) / "review.json").read_text(encoding="utf-8")
    )
    findings = [
        f"- {finding.location}: {finding.message}"
        for scope in report.audits
        for finding in scope.findings
        if finding.severity == "error"
    ]
    return "\n".join(findings) if findings else f"Review verdict: {report.overall_verdict}"


def ready(identifiers: list[str], *, model: str, reasoning_effort: str) -> None:
    """Move chat-edited candidates through audit, audio, preview build, and preflight."""
    for identifier in identifiers:
        if identifier in published_ids(identifier):
            raise ValueError(f"{identifier} is already published; ready is for candidates")
        rebuild_after_repair_if_needed(identifier)
        try:
            passing_review(identifier)
            print(f"{identifier}: current audit already passes")
        except (ValueError, OSError):
            if not audit(identifier, model=model, reasoning_effort=reasoning_effort):
                raise ValueError(
                    f"{identifier}: audit found candidate issues. Ask Codex in chat to fix:\n"
                    + review_findings(identifier)
                )

    for identifier in identifiers:
        source = load_candidate_source(identifier)
        try:
            load_verified_audio(source)
            print(f"{identifier}: matching audio already attached")
        except ValueError:
            audio(identifier)
        step("mobile_lesson", "prepare-candidate", identifier)

    try:
        for identifier in identifiers:
            require_preflight(identifier)
    except (ValueError, OSError):
        run_preflight(identifiers)
    print("Ready for release: " + ", ".join(identifiers))


def upload_receipt_path(identifier: str) -> Path:
    return candidate_directory(identifier) / "r2-upload.json"


def published_manifest(identifier: str) -> Path:
    return published_audio_root(identifier) / identifier / "manifest.json"


def upload(identifier: str) -> None:
    if identifier not in published_ids(identifier):
        raise ValueError("Only published lessons can be uploaded to R2")
    step("upload_published_audio_to_r2", identifier, "--upload")
    upload_receipt_path(identifier).write_text(json.dumps({
        "lesson_id": identifier,
        "published_audio_manifest_sha256": digest(published_manifest(identifier)),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2) + "\n", encoding="utf-8")


def require_upload(identifier: str) -> None:
    path = upload_receipt_path(identifier)
    if not path.is_file() or not published_manifest(identifier).is_file():
        raise ValueError(f"{identifier} has no verified R2 upload receipt")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if (receipt.get("lesson_id") != identifier or
            receipt.get("published_audio_manifest_sha256") != digest(published_manifest(identifier))):
        raise ValueError(f"{identifier} has a stale R2 upload receipt")


def mobile_package(identifier: str) -> Path:
    return ROOT / "web" / "prepared" / identifier / "lesson-data.json"


def deploy(identifiers: list[str]) -> None:
    """Deploy already installed lessons to the live mobile app."""
    for identifier in identifiers:
        require_upload(identifier)
        if not (ROOT / "web" / "dist" / "lesson-data" / f"{identifier}.json").is_file():
            raise ValueError(f"{identifier} is not installed in the mobile app")
    run("npx", "wrangler", "pages", "deploy", "web/dist", "--project-name", "nochmal", "--branch", "main")


def release(identifiers: list[str]) -> None:
    """Run all release checks, then publish, install, and deploy lessons."""
    unpublished = [
        identifier for identifier in identifiers
        if identifier not in published_ids(identifier)
    ]
    if unpublished:
        ready(
            unpublished,
            model=DEFAULT_AUDIT_MODEL,
            reasoning_effort=DEFAULT_AUDIT_REASONING_EFFORT,
        )
    for identifier in identifiers:
        if identifier in published_ids(identifier):
            require_upload(identifier)
            continue

    for identifier in identifiers:
        if identifier not in published_ids(identifier):
            step("publish_candidate", identifier)
            step("validate_release", identifier)
            step("compact_lesson_audio", identifier, "--apply")
            upload(identifier)
        else:
            print(f"{identifier} is already published; resuming mobile release")
        step("mobile_lesson", "prepare", identifier)
        step("mobile_lesson", "install", identifier)
        step("compact_lesson_audio", identifier, "--apply")

    deploy(identifiers)


def status(identifier: str) -> None:
    source = source_path(identifier)
    candidate = source.is_file()
    already_published = identifier in published_ids(identifier)
    review = "missing"
    if candidate:
        try:
            passing_review(identifier)
            review = "pass"
        except (ValueError, OSError) as error:
            review = f"blocked: {error}"
    audio_ready = audio_manifest_path(identifier).is_file()
    preflight = "not required (already published)" if already_published else "missing"
    if candidate and not already_published:
        try:
            require_preflight(identifier)
            preflight = "pass"
        except (ValueError, OSError) as error:
            preflight = f"blocked: {error}"
    mobile = ROOT / "web" / "dist" / "lesson-data" / f"{identifier}.json"
    print(json.dumps({
        "lesson": identifier,
        "authored_source": True,
        "candidate": candidate,
        "audit": review,
        "preflight": preflight,
        "audio_attached": audio_ready,
        "mobile_preview_ready": mobile_package(identifier).is_file(),
        "published": already_published,
        "r2_upload_recorded": upload_receipt_path(identifier).is_file(),
        "mobile_installed": mobile.is_file(),
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("status", "prepare", "ready", "audit", "audio", "preview", "preflight", "publish", "upload", "mobile-prepare", "mobile-install", "release"):
        command = sub.add_parser(action)
        command.add_argument("lesson_ids", nargs="+", type=lesson_id)
        if action in {"ready", "audit"}:
            command.add_argument("--model", default=DEFAULT_AUDIT_MODEL)
            command.add_argument(
                "--reasoning-effort",
                choices=("low", "medium", "high", "xhigh", "max"),
                default=DEFAULT_AUDIT_REASONING_EFFORT,
                help=f"Model reasoning effort (default: {DEFAULT_AUDIT_REASONING_EFFORT}).",
            )
    deploy = sub.add_parser("deploy")
    deploy.add_argument("lesson_ids", nargs="+", type=lesson_id)
    args = parser.parse_args()
    if args.action == "deploy":
        deploy(args.lesson_ids)
        return
    if args.action == "release":
        release(args.lesson_ids)
        return
    if args.action == "ready":
        ready(args.lesson_ids, model=args.model, reasoning_effort=args.reasoning_effort)
        return
    if args.action == "preflight":
        run_preflight(args.lesson_ids)
        return
    if args.action == "publish":
        # Check the whole batch before the first publication-side write.
        for identifier in args.lesson_ids:
            if identifier in published_ids(identifier):
                raise ValueError(f"{identifier} is already published; replacement needs a separate review")
            passing_review(identifier)
            require_preflight(identifier)
    for identifier in args.lesson_ids:
        if args.action == "status":
            authored_record(identifier)
            status(identifier)
        elif args.action == "prepare":
            prepare(identifier)
        elif args.action == "audit":
            if not audit(identifier, model=args.model, reasoning_effort=args.reasoning_effort):
                raise SystemExit(1)
        elif args.action == "audio":
            audio(identifier)
        elif args.action == "preview":
            passing_review(identifier)
            step("mobile_lesson", "prepare-candidate", identifier)
        elif args.action == "publish":
            step("publish_candidate", identifier)
            step("validate_release", identifier)
            step("compact_lesson_audio", identifier, "--apply")
        elif args.action == "upload":
            upload(identifier)
        elif args.action == "mobile-prepare":
            step("mobile_lesson", "prepare", identifier)
        elif args.action == "mobile-install":
            step("mobile_lesson", "install", identifier)
            step("compact_lesson_audio", identifier, "--apply")


if __name__ == "__main__":
    main()
