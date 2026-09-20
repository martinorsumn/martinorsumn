# Resume Tailoring Toolkit

Tailor Martin's resume to each company you apply to. The tool reads a single
**master resume** (`master_resume.yaml`) and a **job description**, then
produces a tailored Markdown resume that:

- reorders **Experience**, **Projects**, and **Leadership** by how well each
  entry matches the posting,
- **bolds** the skills the job asks for and floats them to the front,
- writes a short, company-aware **summary** highlighting your matched strengths,
- prints a transparent **match report** so you can see *why* things reordered.

It is fully offline and deterministic — no API keys, no network, no secrets.

## Setup

The project virtualenv (created by `.cursor/install.sh`) already has everything
installed. If you're starting fresh:

```bash
bash .cursor/install.sh
```

## Usage

```bash
# Using a job-description file:
bash resume/tailor.sh \
  --company "Acme" \
  --role "Software Engineer Intern" \
  --job resume/examples/software_engineering_intern.txt

# Or paste the description inline:
bash resume/tailor.sh --company "Acme" --job-text "We use Python and Java..."

# Or pipe it in:
pbpaste | bash resume/tailor.sh --company "Acme"
```

Output is written to `resume/build/<company>.md` (git-ignored). The command
prints a preview URL you can open while the README/preview server is running:

```
http://localhost:6419/?doc=resume/build/acme.md
```

### Handy flags

| Flag | Effect |
| --- | --- |
| `--role "..."` | Sets the target role used in the summary line. |
| `--out path.md` | Write to a specific path. |
| `--print` | Also print the tailored Markdown to the terminal. |
| `--no-summary` | Omit the tailored summary section. |
| `--no-banner` | Omit the "tailored for … on <date>" footer. |
| `--top-skills N` | Limit the Key Skills callout to N items (default 10). |

## Keeping it accurate

`master_resume.yaml` is the single source of truth. As you gain experience:

1. Add entries under `experience`, `projects`, or `leadership`.
2. Give each entry accurate lowercase `tags` (skills/tools/domains it shows).
   Tags are what the matcher scores against.
3. Extend the `synonyms` map so job-description phrasing (e.g. "ML",
   "additive manufacturing") maps to your canonical skills.

## How matching works

1. A vocabulary is built from your `synonyms`, skills, and every tag.
2. The job description is scanned for whole-word hits of each surface form
   (so "ai" won't match "email").
3. Each resume entry is scored by summing the JD-hit counts of the tags it
   carries, then sections are stably sorted by descending score.
4. Matched skills become the Key Skills callout and get bolded in-line.

Run the tests with:

```bash
source .venv/bin/activate && pytest -q
```
