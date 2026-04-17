from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agents_entry_point_references_repo_operating_docs() -> None:
    body = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "./docs/en/explanation/engineering_operating_principles.md" in body
    assert "./docs/en/status/experiment_plan.md" in body
    assert "./docs/en/explanation/documentation_writing_principles.md" in body
    assert "./plugins/dpf-working-rules/" in body
    assert "study the relevant official docs or other strong external references" in body


def test_repo_local_workflow_plugin_manifest_and_marketplace_exist() -> None:
    manifest_path = ROOT / "plugins" / "dpf-working-rules" / ".codex-plugin" / "plugin.json"
    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

    assert manifest["name"] == "dpf-working-rules"
    assert manifest["skills"] == "./skills/"
    assert manifest["interface"]["displayName"] == "DPF Working Rules"

    assert marketplace["name"] == "driving-preference-field-local"
    assert marketplace["plugins"][0]["name"] == "dpf-working-rules"
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/dpf-working-rules"


def test_repo_local_workflow_skill_routes_to_repo_docs_without_copying_them() -> None:
    skill_path = ROOT / "plugins" / "dpf-working-rules" / "skills" / "dpf-working-rules" / "SKILL.md"
    body = skill_path.read_text(encoding="utf-8")
    openai_yaml = (
        ROOT
        / "plugins"
        / "dpf-working-rules"
        / "skills"
        / "dpf-working-rules"
        / "agents"
        / "openai.yaml"
    ).read_text(encoding="utf-8")

    assert "docs/en/explanation/engineering_operating_principles.md" in body
    assert "docs/en/status/experiment_plan.md" in body
    assert "docs/en/explanation/documentation_writing_principles.md" in body
    assert "clean baseline" in body
    assert "one meaningful hypothesis per branch or worktree" in body
    assert "Study external references first" in body
    assert "Do not copy the full operating principles or experiment plan into the skill." in body
    assert 'display_name: "DPF Working Rules"' in openai_yaml
    assert 'default_prompt: "Use $dpf-working-rules' in openai_yaml


def test_readmes_and_doc_portals_point_to_workflow_guard() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    docs_en = (ROOT / "docs" / "en" / "index.md").read_text(encoding="utf-8")
    docs_ko = (ROOT / "docs" / "ko" / "index.md").read_text(encoding="utf-8")

    assert "./AGENTS.md" in readme_en
    assert "./AGENTS.md" in readme_ko
    assert "./plugins/dpf-working-rules/" in readme_ko
    assert "../../AGENTS.md" in docs_en
    assert "../../plugins/dpf-working-rules/" in docs_en
    assert "../../AGENTS.md" in docs_ko
    assert "../../plugins/dpf-working-rules/" in docs_ko
