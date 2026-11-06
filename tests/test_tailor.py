"""Unit tests for the resume tailoring engine."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from resume import tailor

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER = REPO_ROOT / "resume" / "master_resume.yaml"


@pytest.fixture(scope="module")
def resume() -> dict:
    return tailor.load_resume(MASTER)


def _titles(ranked):
    out = []
    for r in ranked:
        out.append(r.item.get("name") or r.item.get("title"))
    return out


def test_master_resume_loads(resume):
    assert resume["name"] == "Martin Shijo"
    assert resume["projects"]
    assert resume["experience"]


def test_extract_matches_ignores_substrings(resume):
    vocab = tailor.build_vocabulary(resume)
    # "ai" must not match inside "email" / "available"; "ml" not inside "html".
    matches = tailor.extract_matches("Please email your available html resume", vocab)
    assert "artificial intelligence" not in matches


def test_extract_matches_finds_synonyms(resume):
    vocab = tailor.build_vocabulary(resume)
    matches = tailor.extract_matches("We use machine learning and Roblox.", vocab)
    assert matches.get("artificial intelligence", 0) >= 1
    assert matches.get("game development", 0) >= 1  # "roblox" is a surface form


def test_game_jd_ranks_nightfall_first(resume):
    jd = (REPO_ROOT / "resume" / "examples" / "game_developer_intern.txt").read_text()
    result = tailor.tailor(resume, jd, company="StudioX", role="Game Dev Intern")
    project_titles = _titles(result.ranked["projects"])
    assert project_titles[0] == "Nightfall — Roblox Horror Tycoon"


def test_robotics_jd_ranks_magic_experience_first(resume):
    jd = (REPO_ROOT / "resume" / "examples" / "robotics_hardware_intern.txt").read_text()
    result = tailor.tailor(resume, jd, company="RoboCo", role="Hardware Intern")
    exp_titles = _titles(result.ranked["experience"])
    assert exp_titles[0] == "Robotics Intern"  # MAGIC beats Barista here


def test_swe_jd_prioritizes_code_projects_over_robotics(resume):
    jd = (REPO_ROOT / "resume" / "examples" / "software_engineering_intern.txt").read_text()
    result = tailor.tailor(resume, jd, company="Acme", role="SWE Intern")
    # A pure-code project should outrank the hardware/robotics internship.
    proj_scores = {r.item["name"]: r.score for r in result.ranked["projects"]}
    assert proj_scores["Python Adventure Game"] > 0
    assert proj_scores["Followers Analyzer"] > 0


def test_ranking_is_relevance_ordered(resume):
    jd = (REPO_ROOT / "resume" / "examples" / "software_engineering_intern.txt").read_text()
    result = tailor.tailor(resume, jd, company="Acme")
    for ranked in result.ranked.values():
        scores = [r.score for r in ranked]
        assert scores == sorted(scores, reverse=True)


def test_markdown_contains_company_and_matched_bolding(resume):
    jd = (REPO_ROOT / "resume" / "examples" / "software_engineering_intern.txt").read_text()
    result = tailor.tailor(
        resume, jd, company="Acme Corp", role="SWE Intern", today=dt.date(2026, 9, 16)
    )
    md = result.markdown
    assert "Acme Corp" in md
    assert "# Martin Shijo" in md
    assert "**Python**" in md  # matched language bolded
    assert "tailored for **Acme Corp**" in md
    assert "on 2026-09-16" in md


def test_key_skills_only_real_resume_terms(resume):
    jd = "python java git github data structures algorithms"
    result = tailor.tailor(resume, jd, company="Acme")
    known = tailor._all_skills(resume) | tailor._all_tags(resume)
    assert result.key_skills  # non-empty
    assert all(term in known for term in result.key_skills)


def test_no_summary_and_no_banner_flags(resume):
    jd = "python developer"
    result = tailor.tailor(
        resume, jd, company="Acme", include_summary=False, include_banner=False
    )
    assert "## Summary" not in result.markdown
    assert "tailored for" not in result.markdown


def test_slugify():
    assert tailor._slugify("Acme Corp, Inc.") == "acme-corp-inc"
    assert tailor._slugify("!!!") == "company"
