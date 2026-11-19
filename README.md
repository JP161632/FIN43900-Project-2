# Project 2 - Portfolio Committee Review

Evaluate whether a four-stock minimum-estimated-volatility process deserves adoption
relative to equal-weight and inverse-volatility baselines. The current decision is
**do not deploy capital; continue paper research only**. Read
`Decision-Memo.pdf` and `outputs/visible_output.json` without running code.

## Reviewer start

- `submission-manifest.csv` contains reviewer URLs, evidence timestamps and artifact hashes.
- `Decision-Memo.pdf` is the two-page decision; `Research-Evolution.pdf` records the
  retrospective baseline and current evidence; `Validation-and-AI-Use.pdf` records checks and attribution.
- Video 1: https://youtu.be/tMAmXiDBVBg (research evolution).
- Video 2: https://youtu.be/EZolrbd3xOQ (codebase and live validation).
- Video 3: https://youtu.be/sqgNrHPguZ4 (committee presentation).
- Corrected transcripts: `docs/transcript-video-1.txt`, `docs/transcript-video-2.txt`,
  `docs/transcript-video-3.txt`. Editorial changes and remaining audio uncertainties are disclosed.
- `docs/manual-final-steps.md` gives exact remaining student actions; `evidence/package-readiness.json`
  separates mechanical completeness from unresolved human/access evidence.

The full package is intended for a private course-review repository because market-data
redistribution rights are unverified. The instructional team must receive access.

For recording the videos, open `recording/START-HERE.html` in a browser. It contains
numbered evidence screens and matching narration for Videos 1 and 3.
For **Video 2**, open `recording/VIDEO-2-START-HERE.html`: record the actual
repository in VS Code, the live validation demonstration, and the running app, following its exact
shortcuts and script. Read `recording/READ-ME-FIRST.txt` for the short process.
Regenerate the guide with `python build_recording_studio.py` after material changes.

## Setup and run

From this folder with Python 3.13 (the tested interpreter):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe analysis.py
.\.venv\Scripts\python.exe review_analysis.py
.\.venv\Scripts\python.exe tests.py
.\.venv\Scripts\python.exe test_review.py
.\.venv\Scripts\python.exe verify_app.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or from the course repository root using its existing environment:

```powershell
.\.venv\Scripts\python.exe projects\project-2\analysis.py
.\.venv\Scripts\python.exe projects\project-2\review_analysis.py
.\.venv\Scripts\python.exe projects\project-2\tests.py
.\.venv\Scripts\python.exe projects\project-2\test_review.py
.\.venv\Scripts\python.exe projects\project-2\verify_app.py
.\.venv\Scripts\python.exe -m streamlit run projects\project-2\app.py
```

No credentials, network access or download step is required for the analysis or app.
Use the URL printed by Streamlit. Installing dependencies requires package access.
The clean-install record verifies a new environment, installed locked dependencies,
an isolated project copy, matching material outputs, 19 numerical checks and ten
interface checks. This automated event does not claim an unaided human reviewer.

To create a fresh project environment from the existing course interpreter:

```powershell
.\.venv\Scripts\python.exe -m venv projects\project-2\.venv
.\projects\project-2\.venv\Scripts\python.exe -m pip install -r projects\project-2\requirements-lock.txt
.\projects\project-2\.venv\Scripts\python.exe -m streamlit run projects\project-2\app.py
```

The existing course environment has no pip module. Creating the new venv bootstraps
pip; use that new interpreter for dependency installation. The pinned top-level
requirements remain in requirements.txt; requirements-lock.txt also freezes the
resolved transitive dependencies from the successful clean installation.

To regenerate reports, install `requirements-docs.txt` and run `python build_reports.py`.
Run `python audit_package.py` last for current file hashes and honest readiness gaps.

## Evidence flow and file map

`data/sources/` archived daily responses -> audited `data/prices.csv` ->
`analysis.py` and inherited `vendor/portfolio.py` -> `tests.py` ->
`outputs/visible_output.json` -> `app.py` and `build_reports.py`.

- `docs/research-design.md`: decision contract, new assumptions and study limits.
- `data/price-provenance.json`: original download URLs, times and source hashes.
- `outputs/visible_output.json`: material inputs, all replay outputs, selection ledger,
  costs, weight paths, uncertainty interval and source checks.
- `outputs/review_evidence.json`: subperiods, per-trade target constraints, an
  illustrative historical liquidity proxy, actual monitoring flags and the
  preserved changed-input comparison. Added after the initial result; no retuning.
- `evidence/`: executed numerical, interface and reproduction checks.
- `docs/`: report source text, recording drafts and human-only evidence forms.
- `locked_exercise.py`: freeze the student's genuine prediction and code/data
  archive, then execute the designated case. Read `docs/locked-exercise-instructions.md`
  first; no personal prediction or case is pre-run.
- `baseline/prior-portfolio-snapshot/`: unchanged selected prior evidence and hashes;
  original checkpoint acceptance remains unverified.
- `submission-manifest.csv`: 12-row linked inventory, video indices and remaining access checks.
- Three root PDFs: decision memo, research evolution, validation and AI-use record.
- `Edition-A-Retrospective-Baseline.pdf`: summary of the selected unchanged earlier
  results, used as Edition A in the comparison. See `docs/edition-boundary.md` for
  the distinction between this designation and the original checkpoint receipt.

## Conventions and limits

The universe is NVDA, MSFT, TSM and QCOM. Four stocks do not provide broad asset-class
diversification. Prices are archived USD adjusted closes, September 2021-September
2026, downloaded October 22, 2026. Missing months and invalid prices are rejected.
Monthly simple returns use aligned observations. Means multiply by 12; sample
volatility multiplies by sqrt(12). Covariance is annualized consistently.

Rolling replay uses 36 prior monthly returns at each quarterly target trade; weights
drift between trades. Cost is one-way bps times each dollar bought or sold, including
initial purchase, with a self-financing fee calculation. Transaction-dollar sums
include initial deployment and count purchases plus sales; they are not half-turnover.
Cash fallback on an infeasible candidate earns zero until the next quarterly review.
The 10% historical mean hurdle is not a forecast. The 50% cap scenario constrains
trade targets, not drifted holdings. Equal weight is the primary same-universe benchmark.

The final 24 months are a previously inspected chronological replay, not an untouched
holdout. Current adjustment factors, retrospective universe selection and idealized
boundary execution prevent a historical point-in-time investability claim. No tax,
market-impact, ADR-fee or execution-delay model is supplied. No live pilot has run.
Source redistribution rights are not independently cleared: keep the retained archive
in the course workspace/private review package pending rights verification; do not
interpret public access as a redistribution license. No publication is performed.

## Ownership and submission status

The baseline engine and data come from the selected Edition A evidence; original
source paths and earlier files remain unchanged in the provenance archive.
Project additions and their independent checks are recorded in `docs/validation-and-ai-use.md`.
No original Edition A or checkpoint receipt has been provided. The original student
prediction, assistant execution, and later reported personal rerun are preserved
with their actual provenance. Three video links and corrected transcripts have now
been supplied; no full audiovisual review, webcam confirmation or instructional-team
access verification is inferred. The Brightspace receipt remains a post-submission
student action. See `docs/manual-final-steps.md` for exact remaining actions.
