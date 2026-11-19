# Project 2 completion walkthrough

November 19 update: this walkthrough preserves the earlier preparation sequence.
Actual video URLs/transcripts are now supplied. For current actions use
manual-final-steps.md; for frozen attachments use ../submission-files/.

## Current status

The application, archived data, analysis, three report drafts, rubric audit and
recording scripts exist. Nineteen numerical methods, ten interface checks and a
new clean dependency installation pass; both material outputs reproduce in an
isolated copy. The original prediction, result and edited student reflection are
recorded. Use recording-plan.md for the current screen/narration sequence and
final-remaining-items.md for current gaps. Checkpoint/execution-mode requirements,
human ownership, videos/transcripts, access and submission remain separate.

## 1. Choose an Edition A route

Edition A is the original personal baseline submitted before project-specific
generative work, with a successful Brightspace receipt. No such file or receipt
has been supplied. A new report can be dated now; its date does not establish an
earlier checkpoint. The instructor decides whether a recovery counts.

| Route | What the student does | What remains uncertain |
|---|---|---|
| Approved late checkpoint/recovery - recommended | Ask for an authorized task/window and follow its exact conditions | Whether it is offered and what grading consequence applies |
| Prior-lab alternative | Ask whether preserved Lab 15 evidence and actual Git history can support an approved substitute | Existing labs do not automatically establish the checkpoint or receipt |
| Submit with the gap identified | Finish other requirements and accurately report the missing checkpoint | Instructor determines the point consequence; full credit cannot be assumed |

Do not backdate a new report or call previously reviewed work an untouched baseline.

Suggested message for the student to review and send personally:

"I do not have a Project 2 Edition A submission or receipt. I have already begun
the application with generative assistance and have earlier Lab 15 artifacts.
Is an approved late checkpoint, recovery task or prior-lab substitute available?
Please specify the required evidence and any grading consequence. I will preserve
the actual dates and versions."

Needed: actual checkpoint instructions and the instructor's direction. No message
is sent automatically. Do not store unrelated private correspondence or account data.

## 2. Wording

The app and decision memo focus on finance. Repeated attribution prose was removed
from the research narrative. The published Validation-and-AI-Use requirement and
checkpoint history remain accurate. If an explicit newer instructor rule changes
those requirements, supply it so the package can be reconciled with the real rule.

## 3. Answer the project questions before filming

- What is the actual Brightspace deadline and full assignment brief? Are there
  group/individual, hosting, deployment or other requirements beyond the rubric?
- Do you accept NVDA/MSFT/TSM/QCOM as a thematic research sleeve for a committee,
  rather than a recommendation for an entire client's portfolio?
- Do you accept the inherited long-only full investment, 5-point grid and 10%
  annual historical-mean hurdle? This hurdle is not a forward return guarantee.
- Do you accept the new quarterly target trades, 36-return estimation window and
  10-bps one-way cost assumption? These are study assumptions, not client instructions.
- Do you accept the evidence-based decision against capital deployment and for
  further paper research only?
- Do you accept the inherited 15-point target-instability and 22% volatility
  monitoring limits? The latter uses trailing 12 monthly net returns, sample ddof=1,
  annualized with sqrt(12); it is not the 24-month summary shown in the table.
- Will you use the two-page memo instead of a separate slide deck? The repo permits
  it; confirm that Brightspace has no additional requirement.

Student acceptance is now recorded in student-decisions.md. If assumptions change, revise the
design, affected calculations, report text and scripts together before filming.

## 4. Complete the locked changed-input exercise

The blank form is docs/locked-changed-input-record.md. Before closing the assistant,
prepare only a bounded runnable exercise and execution instructions. Choose a
material case whose specific result has not already been revealed. The displayed
10-to-50-bps case and earlier TSM stress cannot be relabeled as new unseen tests.
The exercise must challenge a consequential claim. The assistant does not supply
or imply the student's prediction.

With generative tools closed:

1. Independently write the old/new input values and units, predicted output direction,
   reasoning and predicted decision effect. Preserve this before any execution.
2. Preserve the exact code/data snapshot and its hash.
3. Execute the changed case using the prepared commands and retain actual output.
4. Record actual before/after results, decision effect and agreement/disagreement
   with the prediction. Explain any mismatch or unchanged action.

Reopen assistance after the designated closed phase ends. Supply the genuine record
for incorporation; its prediction and history must not be rewritten from the result.
Execution instructions are ready in locked-exercise-instructions.md. No
completed locked record or student result is currently claimed.

## 5. Open the application and check setup

From the course repository root, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run projects\project-2\app.py
```

Open the Local URL printed in the terminal. Leave the terminal running. Use a second
terminal for audit commands during recording. Separately, have a clean user follow
README setup unaided, including dependency installation, and record command,
environment, first failure, resolution and visible output. Do not invent a reviewer.
The automated copied-project check reused installed dependencies and is narrower.

## 6. Record three distinct videos

Finalize checkpoint status, assumptions and locked record first. Regenerate reports
and reconcile numbers before filming. Open only relevant windows, increase font
sizes, silence notifications, and make a short audio test. Record separate files.

| Video | Screen sequence | Target / maximum |
|---|---|---|
| 1 - evolution | Lab 15 call -> research-evolution PDF page 2 -> app at 10 bps -> baseline resolution | 2:30-2:45 / 3:00 |
| 2 - technical | README flow -> source ledger/audit_sources -> candidate/replay -> trade_cost -> tests output -> app 50-bps/cap -> completed locked record -> reproduction evidence | 4:15-4:40 / 5:00 |
| 3 - committee | Memo page 1 ask/table -> app wealth/cap -> memo page 2 limits/monitoring -> committee action | 3:30-4:15 / 5:00 |

The three video-N-script.md files contain timed narration and exact screen cues.
Bracketed passages require actual events and results. The suggested timing is not
a measured recording duration. Do not present scripts as transcripts.

Before recording, explain these concepts in your own words: why minimum estimated
volatility can realize more risk; why an unchanged nonbinding stress is limited
evidence; target versus drifted holdings; chronological replay versus untouched
holdout; and what new evidence could reopen the recommendation.

## 7. Supply recordings and access evidence

Provide the three real video files or accessible links, measured durations and
actual transcripts. Correct material finance terms, tickers, code names and numbers.
Add timestamp indices from the recordings, not from suggested script times.
Use the assignment's specified hosting. Verify instructional-team repository/video
access in a separate account/window where feasible. Record what was actually checked.

Choose the review repository and access method; confirm the submission path and
data redistribution terms before public release. Deployment is optional under the
repo checklist but may be affected by additional Brightspace instructions.

## 8. Freeze and submit

Re-run relevant checks after material changes, update human records, rebuild and
visually inspect reports, then run audit_package.py last. Verify agreement among
numbers, dates, recommendations and conditions across every artifact. Complete
the 11 required manifest entries and label the optional deployment row. Submit
through Brightspace and retain the actual successful receipt. A passing local
audit does not establish instructor approval or a completed submission.
