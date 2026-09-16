#!/usr/bin/env python3
"""Tailor a master resume to a specific company's job description.

The tool is fully offline and deterministic: it reads a structured master
resume (``resume/master_resume.yaml``), matches a job description against the
skills/tags in that resume, then produces a tailored Markdown resume that

  * reorders Experience / Projects / Leadership by relevance to the posting,
  * bolds and floats matched skills to the front of each skill category,
  * writes a company-aware summary highlighting the strengths that matched, and
  * prints a transparent "match report" explaining the ordering.

No network calls, API keys, or secrets are involved.

Usage:
    python resume/tailor.py --company "Acme" --role "Software Engineer Intern" \\
        --job resume/examples/software_engineering_intern.txt

The generated Markdown can be previewed in the browser via the repo's preview
server, e.g. http://localhost:6419/?doc=resume/build/acme.md
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESUME = Path(__file__).resolve().parent / "master_resume.yaml"

# Pretty display overrides for canonical terms whose Title Case would be wrong.
_DISPLAY_OVERRIDES = {
    "ai-assisted development": "AI-Assisted Development",
    "artificial intelligence": "Artificial Intelligence",
    "object-oriented programming": "Object-Oriented Programming",
    "3d printing": "3D Printing",
    "cad": "CAD",
    "cli": "CLI",
    "ui": "UI",
    "vex robotics": "VEX Robotics",
    "stem": "STEM",
    "pos": "POS",
    "git": "Git",
    "github": "GitHub",
    "api integration": "API Integration",
}


# --------------------------------------------------------------------------- #
# Loading & vocabulary
# --------------------------------------------------------------------------- #
def load_resume(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    return data


def _all_tags(resume: dict) -> set[str]:
    tags: set[str] = set()
    for section in ("experience", "projects", "leadership"):
        for item in resume.get(section) or []:
            for tag in item.get("tags") or []:
                tags.add(str(tag).strip().lower())
    return tags


def _all_skills(resume: dict) -> set[str]:
    skills: set[str] = set()
    for values in (resume.get("skills") or {}).values():
        for skill in values or []:
            skills.add(str(skill).strip().lower())
    return skills


def build_vocabulary(resume: dict) -> dict[str, list[str]]:
    """Map each canonical term to the surface forms that signal it in a JD.

    Canonical terms come from the resume's ``synonyms`` map plus every skill
    and tag used anywhere in the resume (so nothing is unmatchable).
    """
    vocab: dict[str, set[str]] = {}

    for canonical, surfaces in (resume.get("synonyms") or {}).items():
        key = str(canonical).strip().lower()
        forms = {key}
        for surface in surfaces or []:
            forms.add(str(surface).strip().lower())
        vocab.setdefault(key, set()).update(forms)

    for term in _all_skills(resume) | _all_tags(resume):
        vocab.setdefault(term, set()).add(term)

    return {canonical: sorted(forms) for canonical, forms in vocab.items()}


# --------------------------------------------------------------------------- #
# Matching & scoring
# --------------------------------------------------------------------------- #
def extract_matches(jd_text: str, vocabulary: dict[str, list[str]]) -> dict[str, int]:
    """Return {canonical term: number of surface-form hits in the JD}."""
    text = jd_text.lower()
    matches: dict[str, int] = {}
    for canonical, surfaces in vocabulary.items():
        count = 0
        for surface in surfaces:
            # Whole-token match so "ai" doesn't match "email", "ml" not "html".
            pattern = r"(?<![\w-])" + re.escape(surface) + r"(?![\w-])"
            count += len(re.findall(pattern, text))
        if count:
            matches[canonical] = count
    return matches


def score_item(item: dict, matches: dict[str, int]) -> tuple[int, list[str]]:
    """Score one resume item by how strongly its tags match the JD."""
    item_tags = {str(t).strip().lower() for t in (item.get("tags") or [])}
    matched = sorted(item_tags & set(matches))
    score = sum(matches[t] for t in matched)
    return score, matched


@dataclass
class RankedItem:
    item: dict
    score: int
    matched: list[str] = field(default_factory=list)


def rank_section(items: Iterable[dict], matches: dict[str, int]) -> list[RankedItem]:
    """Stable-sort items by descending relevance score (ties keep JD order)."""
    ranked = [RankedItem(item, *score_item(item, matches)) for item in items]
    ranked.sort(key=lambda r: r.score, reverse=True)
    return ranked


def key_skills(resume: dict, matches: dict[str, int], limit: int) -> list[str]:
    """Canonical terms that (a) matched the JD and (b) are real resume skills/tags."""
    known = _all_skills(resume) | _all_tags(resume)
    candidates = [c for c in matches if c in known]
    candidates.sort(key=lambda c: (-matches[c], c))
    return candidates[:limit]


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #
def pretty(term: str, skill_display: dict[str, str] | None = None) -> str:
    key = term.strip().lower()
    if skill_display and key in skill_display:
        return skill_display[key]
    if key in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[key]
    return key.title()


def _skill_display_map(resume: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for values in (resume.get("skills") or {}).values():
        for skill in values or []:
            mapping[str(skill).strip().lower()] = str(skill)
    return mapping


def _humanize_list(items: list[str]) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


# --------------------------------------------------------------------------- #
# Tailoring
# --------------------------------------------------------------------------- #
@dataclass
class TailorResult:
    markdown: str
    matches: dict[str, int]
    ranked: dict[str, list[RankedItem]]
    key_skills: list[str]


def tailor(
    resume: dict,
    jd_text: str,
    company: str,
    role: str | None = None,
    *,
    include_summary: bool | None = None,
    include_banner: bool = True,
    top_skills: int = 10,
    today: _dt.date | None = None,
) -> TailorResult:
    vocab = build_vocabulary(resume)
    matches = extract_matches(jd_text, vocab)
    skill_display = _skill_display_map(resume)

    ranked = {
        section: rank_section(resume.get(section) or [], matches)
        for section in ("experience", "projects", "leadership")
    }
    top_skill_terms = key_skills(resume, matches, top_skills)

    lines: list[str] = []
    name = resume.get("name", "")
    headline = resume.get("headline", "")
    lines.append(f"# {name}")
    if headline:
        lines.append(f"{headline}")
    lines.append("")

    # Contact line.
    c = resume.get("contact") or {}
    contact_bits: list[str] = []
    if c.get("email"):
        contact_bits.append(str(c["email"]))
    if c.get("phone"):
        contact_bits.append(str(c["phone"]))
    if c.get("location"):
        contact_bits.append(str(c["location"]))
    if c.get("github"):
        contact_bits.append(f"[GitHub]({c['github']})")
    if c.get("linkedin"):
        contact_bits.append(f"[LinkedIn]({c['linkedin']})")
    if c.get("website"):
        contact_bits.append(f"[Website]({c['website']})")
    if contact_bits:
        lines.append(" · ".join(contact_bits))
        lines.append("")

    # Summary.
    want_summary = resume.get("include_summary", True) if include_summary is None else include_summary
    if want_summary and resume.get("summary_template"):
        role_text = role or "software"
        skills_text = _humanize_list(
            [pretty(t, skill_display) for t in top_skill_terms[:3]]
        ) or "software development"
        summary = str(resume["summary_template"]).format(
            company=company, role=role_text, skills=skills_text
        )
        summary = " ".join(summary.split())
        lines.append("## Summary")
        lines.append(summary)
        lines.append("")

    # Key skills callout (matched, ordered by relevance).
    if top_skill_terms:
        lines.append("## Key Skills")
        badges = " · ".join(f"`{pretty(t, skill_display)}`" for t in top_skill_terms)
        lines.append(badges)
        lines.append("")

    # Full skills, with matched ones bolded and floated to the front.
    skills = resume.get("skills") or {}
    if skills:
        lines.append("## Technical Skills")
        for category, values in skills.items():
            ordered = sorted(
                values or [],
                key=lambda s: (str(s).strip().lower() not in matches, list(values).index(s)),
            )
            rendered = [
                f"**{s}**" if str(s).strip().lower() in matches else str(s)
                for s in ordered
            ]
            lines.append(f"- **{category}:** " + ", ".join(rendered))
        lines.append("")

    # Experience / Projects / Leadership, reordered by relevance.
    _render_experience(lines, ranked["experience"])
    _render_projects(lines, ranked["projects"])
    _render_leadership(lines, ranked["leadership"])

    # Education (kept in given order).
    education = resume.get("education") or []
    if education:
        lines.append("## Education")
        for edu in education:
            head = edu.get("school", "")
            lines.append(f"### {head}")
            deg_bits = [b for b in [edu.get("degree"), edu.get("dates")] if b]
            if deg_bits:
                lines.append(" — ".join(deg_bits))
            for detail in edu.get("details") or []:
                lines.append(f"- {detail}")
            lines.append("")

    if include_banner:
        stamp = (today or _dt.date.today()).isoformat()
        role_suffix = f" · {role}" if role else ""
        lines.append("---")
        lines.append(f"_Resume tailored for **{company}**{role_suffix} on {stamp}._")

    markdown = "\n".join(lines).rstrip() + "\n"
    return TailorResult(markdown, matches, ranked, top_skill_terms)


def _render_experience(lines: list[str], ranked: list[RankedItem]) -> None:
    if not ranked:
        return
    lines.append("## Experience")
    for r in ranked:
        it = r.item
        header = ", ".join([b for b in [it.get("title"), it.get("org")] if b])
        loc = it.get("location")
        if loc:
            header += f" — {loc}"
        lines.append(f"### {header}")
        if it.get("dates"):
            lines.append(f"*{it['dates']}*")
        for bullet in it.get("bullets") or []:
            lines.append(f"- {bullet}")
        lines.append("")


def _render_projects(lines: list[str], ranked: list[RankedItem]) -> None:
    if not ranked:
        return
    lines.append("## Projects")
    for r in ranked:
        it = r.item
        name = it.get("name", "")
        title = f"[{name}]({it['url']})" if it.get("url") else name
        dates = f" — {it['dates']}" if it.get("dates") else ""
        lines.append(f"### {title}{dates}")
        if it.get("subtitle"):
            lines.append(f"*{it['subtitle']}*")
        for bullet in it.get("bullets") or []:
            lines.append(f"- {bullet}")
        lines.append("")


def _render_leadership(lines: list[str], ranked: list[RankedItem]) -> None:
    if not ranked:
        return
    lines.append("## Leadership & Activities")
    for r in ranked:
        it = r.item
        header = ", ".join([b for b in [it.get("title"), it.get("org")] if b])
        lines.append(f"### {header}")
        if it.get("dates"):
            lines.append(f"*{it['dates']}*")
        for bullet in it.get("bullets") or []:
            lines.append(f"- {bullet}")
        lines.append("")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "company"


def _read_jd(args: argparse.Namespace) -> str:
    if args.job_text:
        return args.job_text
    if args.job:
        return Path(args.job).read_text(encoding="utf-8")
    return sys.stdin.read()


def _print_report(result: TailorResult, company: str, role: str | None) -> None:
    role_txt = f" ({role})" if role else ""
    print(f"\nMatch report — {company}{role_txt}")
    print("=" * (14 + len(company) + len(role_txt)))
    if result.matches:
        top = sorted(result.matches.items(), key=lambda kv: (-kv[1], kv[0]))
        joined = ", ".join(f"{term} ×{n}" for term, n in top)
        print(f"JD keywords matched: {joined}")
    else:
        print("JD keywords matched: (none — check the job description text)")
    for section in ("experience", "projects", "leadership"):
        ranked = result.ranked.get(section) or []
        if not ranked:
            continue
        print(f"\n{section.capitalize()} order (by relevance):")
        for i, r in enumerate(ranked, 1):
            label = r.item.get("name") or ", ".join(
                b for b in [r.item.get("title"), r.item.get("org")] if b
            )
            reasons = ", ".join(r.matched) if r.matched else "—"
            print(f"  {i}. {label}  [score {r.score}: {reasons}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tailor a master resume to a company's job description."
    )
    parser.add_argument("--company", required=True, help="Company you're applying to.")
    parser.add_argument("--role", default=None, help="Target role/title (optional).")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--job", "-j", help="Path to a job-description text file.")
    src.add_argument("--job-text", help="Inline job-description text.")
    parser.add_argument(
        "--resume", default=str(DEFAULT_RESUME), help="Path to master resume YAML."
    )
    parser.add_argument("--out", default=None, help="Output Markdown path.")
    parser.add_argument("--print", action="store_true", dest="to_stdout", help="Print the resume to stdout.")
    parser.add_argument("--no-summary", action="store_true", help="Omit the tailored summary.")
    parser.add_argument("--no-banner", action="store_true", help="Omit the tailored-for footer.")
    parser.add_argument("--top-skills", type=int, default=10, help="Max key skills to list.")
    args = parser.parse_args(argv)

    resume = load_resume(Path(args.resume))
    jd_text = _read_jd(args)
    if not jd_text.strip():
        parser.error("No job description provided (use --job, --job-text, or stdin).")

    result = tailor(
        resume,
        jd_text,
        company=args.company,
        role=args.role,
        include_summary=False if args.no_summary else None,
        include_banner=not args.no_banner,
        top_skills=args.top_skills,
    )

    out_path = Path(args.out) if args.out else REPO_ROOT / "resume" / "build" / f"{_slugify(args.company)}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.markdown, encoding="utf-8")

    _print_report(result, args.company, args.role)
    print(f"\nWrote: {out_path}")
    try:
        rel = out_path.relative_to(REPO_ROOT)
        print(f"Preview: http://localhost:6419/?doc={rel}")
    except ValueError:
        pass
    if args.to_stdout:
        print("\n" + "-" * 60 + "\n")
        print(result.markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
