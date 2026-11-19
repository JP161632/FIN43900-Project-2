# Validation and AI-use record

## Decision, version and information boundary
Decision: Continue paper research only; do not approve capital deployment. Material input and code SHA-256 hashes are embedded
in outputs/visible_output.json. Its UTC run timestamp is 2026-11-18T02:25:07.225154+00:00.
Run audit_package.py last to freeze the complete package inventory. There is no
claimed Edition A receipt. The final repository commit and artifact hashes are
recorded in the submission manifest and release evidence when frozen.

## Data ledger and lineage
Each of four archived Yahoo Finance daily responses has its original request URL,
UTC retrieval time, USD currency and SHA-256 in data/price-provenance.json. All were
downloaded October 22, 2026. The adjusted-close field is aggregated to the last
observed trading day in each month, September 2021 through September 2026: 61 prices
and 60 simple monthly returns per stock. All 244 monthly values are reconstructed
from the preserved daily responses; both raw and CSV hashes pass verification.
Source history links: finance.yahoo.com/quote/NVDA/history/ and corresponding
MSFT, TSM and QCOM pages. Exact machine URLs are retained in the source ledger.

No observation is filled or silently dropped. Duplicate, reversed or missing
months, nonfinite and nonpositive prices are rejected. The partial October 2026
month was excluded by the original download policy. Retrospective split/dividend
adjustments are those available at retrieval; original historical vintages were
not reconstructed. This limits point-in-time claims. Public access does not prove
redistribution rights; those rights remain unverified. No credentials or private
client data are required. The full archived package is intended for a private
course-review repository; private access does not resolve redistribution rights.

## Finance and replay conventions
Means use monthly arithmetic returns times 12. Standard deviations use sample ddof=1
times sqrt(12). Covariance uses the same monthly observations and frequency.
The grid searches all 1,771 long-only fully invested four-asset 5-point allocations;
first enumeration order wins a risk tie within 1e-12. The 10% historical mean floor
does not establish a future expected return. A 50% target cap is a separate case.

At each quarterly target trade, estimation uses only the preceding 36 monthly
returns. October 2024-September 2026 comprises 24 evaluation returns. Trade timing
assumes idealized implementation at the preceding boundary; no release-time or
execution-lag proof is supplied. Missing feasible candidates produce zero-yield
cash until the next scheduled review. Holdings drift between trades.

One-way fees apply to purchases plus sales, including initial deployment. With
pretrade equity weights p, target weights w and decimal fee k, solve
c = k * sum(abs((1-c)*w-p)). Monthly net return equals
(1-c)*(1+gross return)-1. This pays fees from portfolio capital rather than borrowing.
Transaction-dollar sums count both sides and initial deployment; they are not
half-turnover. At 10 bps, candidate aggregate traded-NAV ratios sum to
2.5342 over 24 months. Market impact, taxes, actual spreads,
ADR fees, capacity and executable fills are not established.

<!-- pagebreak -->

## Executed validation
The numerical audits ran 19 test methods
with zero failures/errors: 14 core and 5 supplemental.
The actual Streamlit page passed 10 checks. Evidence files preserve
the executed output. These automated checks do not establish independent student authorship.

| Highest-risk issue | Independent check | Observed result / consequence |
|---|---|---|
| Wrong data or transformations | Hash verification plus reconstruct all 244 values | Passed; raw archive retained |
| Portfolio arithmetic | Four independent 20%-vol assets: equal mix vol = 10%; explicit sample covariance products | Passed |
| Cost timing and initial purchase | Exact all-cash deployment and full-switch fee answers; first month manual calculation | Passed |
| Hidden future-return use | Mutate later returns and compare prior start weights | Prior weights unchanged; source-vintage risk remains |
| Optimizer feasibility | Impossible 1000% mean hurdle and 50% target-cap case | Infeasible case returns None; cap enforced at trades |
| Broken inputs | Corrupt hash; missing/duplicate/reversed months; zero and missing prices; invalid cost | Rejected; no fabricated replacement |
| Failure fallback | Force no feasible candidate | Eight cash rebalances; zero cash return |
| Cost sensitivity | 0, 10, 25, 50 bps for all three rules | Higher costs reduce cumulative net wealth |
| Reproducibility | Fresh process, isolated project copy, unrelated working directory | Identical material output except run timestamp |

Full-sample estimates reconcile with the preserved Edition A search. Changing only TSM's
mean by minus one point leaves weights unchanged; the return hurdle is nonbinding.
Changing the sample from 60 to 36 returns shifts a weight by 20 points. The candidate's
rolling target changes reach 20 points. It also
underperforms equal weight and realizes higher volatility in the replay. These
failures restrict the decision; successful arithmetic does not justify adoption.

## Holdout, uncertainty and selection
The evaluation segment is chronologically later than each estimation window, but
the data and prior outputs had already been inspected. It is not an untouched
holdout or preregistered discovery. outputs/visible_output.json records all 17
research cases: 12 cost/rule replays, one target-cap replay and four static
estimation/failure cases. The preserved 24-month exercise and added review cases are
separately disclosed in execution.json and review_evidence.json. Test mutations are
listed in tests.py and test_review.py. No case was discarded for unattractive results.

The paired monthly return-difference interval uses 2,000 circular moving-block
resamples with 3-month blocks and fixed seed 439. The annualized arithmetic mean
difference interval is -35.38% to 5.99%.
It includes zero. Twenty-four months and the chosen block length provide weak
regime coverage; this descriptive interval is not prospective skill evidence,
a CAGR interval, or a correction for universe selection and timing limitations.

<!-- pagebreak -->

## Supplemental robustness, constraints and implementation review
These additions were made after the original results were observed. They are
descriptive diagnostics, not new independent holdouts or an optimized redesign.
The main strategy, evaluation months, costs and recommendation remain unchanged.

The first segment is October 2024-September 2025; the second is October
2025-September 2026. Candidate underperformance persists in both segments.

| Rule | First 12 months net return | Last 12 months net return |
|---|---:|---:|
| Equal weight | 34.29% | 27.31% |
| Inverse volatility | 30.56% | 24.21% |
| Candidate | 19.55% | 4.43% |


## Target constraints and monitoring
The per-trade audit checks nonnegative weights, funding, the candidate historical
mean hurdle and the separate 50% target cap. Baseline and candidate trade records
retain the actual values. These target checks do not certify suitability or future
losses. Drifted holdings can exceed the 50% target after market movements.

Applying the accepted 15-point movement and 22% trailing-12-month volatility
thresholds diagnostically flags 1 target
event and 9 volatility months.
The first 11 months have too
few observations for that volatility measure. The replay was not stopped at these
flags, so this is not a simulation of a functioning kill-rule strategy. The evidence
supports quarantine/review rather than retrospective threshold relaxation.

## Historical liquidity proxy, not executable capacity
For each trade, compute raw daily close times raw daily volume over the prior 20
valid trading observations ending no later than the estimation cutoff. Do not mix
adjusted prices with unadjusted share volume. At an explicitly illustrative fixed
$1 million pretrade NAV, maximum participation across the three rules is
0.0174% of that average.
Per-asset trade fractions reconcile to the self-financing cost convention.
The 1% participation threshold is a scenario assumption, not a market standard
or permission to allocate. The proxy does not establish spreads, impact, fills,
liquidity under stress, intraday availability or executable capacity. It does not
override the failed investment comparison.

## Clean installation and independent process replay
A new venv without system-site-packages installed the pinned requirements from
the package index. An isolated project copy from an unrelated working directory
reproduced both material output files and passed 19 numerical and 10 interface
checks. Dependency checking found no broken requirements; resolved packages are
frozen in requirements-lock.txt. The first failure was absent pip in the existing
course environment, followed by blocked sandbox networking. Creating a new venv
bootstrapped pip; approved network installation resolved the download failure.
The clean replay took 23.39 seconds after installation.
This is automated evidence, not an observed unaided human reviewer or student defense.
The proposed prospective protocol fixes future timing, comparison metrics and stop
conditions. It does not repair the historical holdout or claim future observations.

<!-- pagebreak -->

## Locked record and later student rerun
The student's prediction was preserved before the first execution, performed
through the assistant. The snapshot, hashes and student reconciliation remain
recorded. Local hashes do not independently establish authorship or tool state.

AI-closed student rerun - self-reported: the student reports matching results and personal prediction/reasoning. The generated student-rerun.json is unavailable; matching output is not independently verified. This rerun followed outcome review; the original execution remains preserved.

## Preserved prediction and executed window change
Material input: rolling estimation window, 36 to 24 monthly returns. The 24
evaluation months, four stocks, 10-bps one-way costs, hurdle, grid and trade schedule
were held fixed. Prediction preserved at 2026-11-17T22:39:57.225144+00:00.
Code/data snapshot SHA-256 (continued on next line):
13b2936d21cc2c64a4e2d449a48eceeb
53a8a95d897fa94c58f9364b1aae8742
Exact original prediction, before/after outputs and operator record are in
evidence/locked-exercise/precommit.json, execution.json and execution-provenance.json.

The preserved student prediction expected higher realized net volatility, more
aggressive target movement and an unchanged recommendation under the 24-month
lookback. The student's stated reasoning was fewer observations and greater
estimation noise in the concentrated technology sleeve. This reasoning was a
prediction, not an empirically isolated causal explanation. Expected decision:
continue paper research only. Actual decision: unchanged.

Net cumulative return changed from 24.85% to
25.52%; annualized realized net volatility fell from
29.61% to 27.83%, contrary to the
volatility prediction. Maximum quarterly target movement rose from
20 to 25
percentage points, supporting that separate instability prediction. Maximum drawdown
was almost unchanged. The decision policy still does not support capital deployment.

The exact code/data ZIP, its SHA-256, the original prediction and full execution
output are preserved. The student's corrected reflection acknowledges the incorrect
volatility prediction, the separate target-instability result and the unchanged
recommendation. The concentrated process still trails equal weight and lacks
prospective and implementation evidence. Noise and timing remain hypotheses,
not isolated causes. The edited presentation is in docs/student-reflection.md;
the original response remains in student-reconciliation.md. Target movement does
not mechanically determine realized return volatility. The revealed scenario
cannot become a new unseen prediction exercise.


## Remaining original and submission evidence
Original Edition A checkpoint acceptance, full audiovisual ownership evidence,
grader access and successful Brightspace submission remain to be verified.
The current videos are retained at the student's preference; Video 1's missing
explicit AI-output identification remains a known communication/evidence gap.
The manual checklist supplies exact actions. Missing checkpoint
history is not repaired by a retrospective label or an already-seen test.
The actual Brightspace rubric was inspected November 19; the final assignment
displays November 23, 2026 at 11:59 PM and directs students to the course repository.
Its rubric reference and evidence map are retained in docs/. The fresh 30-month prediction, student execution and reconciliation are now saved and hash/arithmetic verified. The older 24-month rerun remains a historical self-report rather than the basis for this new record.


<!-- pagebreak -->

## Fresh student-completed locked exercise: 36 to 30 monthly returns
This separate case was completed after the earlier 24-month result was known.
Its specific 30-month result was not supplied before the prediction. The same
dataset remains previously inspected; this is not a new holdout or prospective test.
The student reports closed-tool drafting and execution. The assistant verified
saved hashes and monthly-ledger arithmetic afterward; no scenario was rerun.

Input: estimation window, 36 to 30 monthly returns. Four stocks, 24 evaluation
months, quarterly trades, 10-bps one-way costs, hurdle and grid were held fixed.
Prediction freeze: 2026-11-19T19:17:02.548547+00:00. Execution: 2026-11-19T19:17:03.784544+00:00.
Snapshot SHA-256: 584b032a0ed508fb26e19cc47edfd51a 38145a33020003a8a85693e27eef5d50.
Exact original text, archive and full results remain under evidence/fresh-locked-exercise/.

## Human prediction before this run (preserved)
I expect our annualized realized net volatility will end up slightly lower (probably somewhere between 28% and 29%), while our largest quarterly target change will be higher (likely pushing past our 20-point baseline).

The student's stated reasoning was that fewer observations would increase
target sensitivity while the retained estimation window might produce lower
realized volatility. Expected decision: no deployment; further paper research only.
The verbatim reasoning and authorship attestation remain in precommit.json and
the unchanged docs/fresh-prediction-input.json; accuracy is assessed after the run.

| Metric | Before: 36 months | After: 30 months |
|---|---:|---:|
| Net cumulative return | 24.85% | 25.89% |
| Annualized realized net volatility | 29.61% | 28.69% |
| Month-end max drawdown | -28.14% | -28.14% |
| Largest quarterly target movement | 20 percentage points | 20 percentage points |

## Student reconciliation and actual decision
The student explicitly acknowledges that the 28%-29% volatility prediction was
supported but the prediction of target movement above 20 points was not. Actual
action remains no deployment: the process still trails equal weight, retains the
same reported drawdown and lacks prospective/implementation evidence.

The original explanation is preserved in student-reconciliation.md. Its proposed
"data cushion" explanation is a hypothesis, not an isolated cause. Maximum target
movement is not turnover. Lower realized volatility does not establish persistence.
The changes are 0.92 percentage points lower volatility and 1.03 points higher
cumulative return. The 30-month maximum starting security weight is 95.26%.

Independent saved-ledger checks reconcile compounding, CAGR, sample volatility,
drawdown and target movement for both cases. Original prediction/archive hashes
match; collected prediction precedes freeze and execution in local records.
Tool state and identity remain student self-attestations. This new evidence
addresses the final locked-record requirement without relabeling the original run.
It is added after recording; none of it is invented as earlier video narration.

<!-- pagebreak -->


## Named material AI-use register
| Tool / exposed version / date | Material contribution | Check and disposition |
|---|---|---|
| Codex; exact model/version not exposed in the working tools; November 17, 2026 | Project research design, code, validation, interface, reports, rehearsal drafts and requested changed-input execution | Source reconstruction, independent numeric fixtures, mutation tests and interface replay; student accepted assumptions and recommendation; exact user prediction and later reflection preserved; execution provenance retained |
| Codex, GPT-6 (system-exposed identity; exact backend build not exposed); November 19, 2026 | Editorial correction of supplied YouTube captions; submission audit; documentation, report, manifest and private publication preparation | Material quoted results checked against frozen outputs; timestamps retained from supplied captions; substantive uncertainties flagged; human-only events and media review not fabricated |
| Codex, GPT-6; November 19, 2026, after fresh student execution | Preserve supplied prediction and original reconciliation; independently check saved record hashes/monthly arithmetic; update reports and submission snapshot | Original files retained; new scenario not run by assistant; numerical changes reconciled; causal interpretations qualified separately; current videos unchanged |

Checks executed through the same assistant are reproducible engineering evidence,
not an independent human review or independent source corroboration. Student
acceptance is recorded in docs/student-decisions.md. Detailed independent reasoning
and code mastery are not inferred from that acceptance.

## Monitoring, limits and unresolved evidence
Quarterly paper reviews: monitor provenance, feasibility, target changes and trailing
12-month sample net volatility. Quarantine above 15 points of target movement or
22% annualized trailing volatility; no retrospective threshold relaxation. Committee
review is required before deployment or policy changes. A 24-month realized-volatility
summary is not the defined 12-month monitoring statistic.

Clean dependency installation and automated replay pass. An unaided human reviewer
remains unobserved. The three actual video URLs and corrected student-supplied
transcripts are now present. This supersedes earlier missing-recording inventory notes,
without certifying audiovisual content, webcam presence or logged-out playback.

## Submitted recordings and transcript corrections
Video 1: https://youtu.be/tMAmXiDBVBg - metadata duration 2:52, maximum 3:00.
Video 2: https://youtu.be/EZolrbd3xOQ - metadata duration 4:56, maximum 5:00.
Video 3: https://youtu.be/sqgNrHPguZ4 - metadata duration 3:13, maximum 5:00.
November 19 public metadata reports playable status and captions; the student
confirms the links work. A webcam is visible in Video 1's opening sample.
Full audiovisual alignment and Videos 2/3 webcam coverage remain unverified.
The manifest supplies section indices; transcript headers retain caption endpoints,
which can extend past the media endpoint. Captions were corrected for recognition
errors, finance terms and code names. Video 3's immediate self-correction is
consolidated to 70.97%. Later written results are not presented as original speech.

Video 1's concentration explanation is not an isolated causal finding; its explicit
AI-output identification is absent from supplied speech. Video 2's captioned line
12 is flagged against guide line 112. Original speech is not silently rewritten.
