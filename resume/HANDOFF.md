# Resume work — handoff notes

Context for any agent (or person) picking up Martin's resume work.

## Where things live

- `resume/master_resume.yaml` — single source of truth for resume content (education, skills, experience, projects, leadership) plus keyword `synonyms`.
- `resume/tailor.py` — offline tool that tailors the master resume to a job description (reorders/emphasizes by relevance). See `resume/README.md`.
- `resume/export/` — scripts that render a formatted, one-page resume:
  - `make_icons.py` — regenerates the contact-row logo icons into `resume/export/icons/` (icons are committed, so this is rarely needed).
  - `make_pdf.py` — writes `resume/build/Martin_Shijo_Resume_Steelcase.pdf`.
  - `make_docx.py` — writes `resume/build/Martin_Shijo_Resume_Steelcase.docx`.
- `resume/build/` — generated output (git-ignored).

## Regenerate the resume

```bash
bash .cursor/install.sh                 # sets up .venv with all deps
source .venv/bin/activate
python resume/export/make_pdf.py
python resume/export/make_docx.py
```

## Formatting preferences (agreed with Martin)

- One page, **Times New Roman** (PDF uses the metric-identical "Tinos" font).
- Contact row = logo icon + handle, as clickable links (email, phone, GitHub, LinkedIn).
- Font sizes/spacing are tuned in the `# tunable sizing` block at the top of `make_pdf.py`; the content is sized to fill one page.
- In drafted prose (summaries, cover answers), avoid hyphens/em dashes.

## Current facts

- UMD CS, graduating **May 2029** (early, via credits).
- FIRE research program — **Climate Computing** stream (Spring 2027), listed under Education.
- Leadership includes **Bitcamp 2027 Logistics Organizer (Hardware)**.
- The committed example is tailored for a **Steelcase IT Summer Intern** application; change the summary and ordering in `make_pdf.py`/`make_docx.py` (or regenerate from `master_resume.yaml`) for other companies.
- A **Google Software Engineering Intern** example is `python resume/export/make_google_pdf.py`, which writes `resume/build/Martin_Shijo_Resume_Google.pdf`. The sample posting is `resume/examples/google_software_engineering_intern.txt`. Passport stays on the Steelcase page; this example uses Python Adventure Game, Followers Analyzer, and Nightfall instead.

See PR for history.
