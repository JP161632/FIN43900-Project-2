"""Build consistent Markdown and PDF reports from frozen, executed evidence."""
import html
import json
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent


def pct(value): return f'{value:.2%}'


def render_pdf(text, path):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyResearch', fontName='Helvetica', fontSize=9.5, leading=13, spaceAfter=7))
    styles.add(ParagraphStyle(name='TableResearch', fontName='Helvetica', fontSize=8, leading=10))
    styles['Title'].fontSize = 21
    styles['Title'].leading = 25
    styles['Title'].textColor = colors.HexColor('#16324f')
    styles['Heading2'].fontSize = 12
    styles['Heading2'].keepWithNext = True
    styles['Heading2'].textColor = colors.HexColor('#16324f')
    story, paragraph, table_rows = [], [], []

    def clean(value):
        value = html.escape(value)
        return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', value)

    def flush():
        if paragraph:
            story.append(KeepTogether([Paragraph(clean(' '.join(paragraph)), styles['BodyResearch'])]))
            paragraph.clear()
        if table_rows:
            rows = [[Paragraph(clean(cell), styles['TableResearch']) for cell in row] for row in table_rows]
            width = 504/len(rows[0])
            table = Table(rows, colWidths=[width]*len(rows[0]), repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff5')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#ccd6df')),
                ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table, Spacer(1,9)])
            table_rows.clear()

    for line in text.splitlines():
        if line == '<!-- pagebreak -->':
            flush()
            story.append(PageBreak())
        elif line.startswith('|'):
            if paragraph: flush()
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+', cell or '-') for cell in cells): table_rows.append(cells)
        elif line.startswith('#'):
            flush()
            title = line.lstrip('#').strip()
            story.append(Paragraph(clean(title), styles['Title'] if line.startswith('# ') else styles['Heading2']))
        elif not line.strip(): flush()
        elif line.startswith('- '):
            flush()
            story.append(Paragraph('- '+clean(line[2:]), styles['BodyResearch']))
        else:
            if table_rows: flush()
            paragraph.append(line.strip())
    flush()

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor('#ccd6df'))
        canvas.line(54,43,558,43)
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#536576'))
        canvas.drawString(54,31,'FIN 43900 | Project 2 | Historical research review')
        canvas.drawRightString(558,31,str(doc.page))

    SimpleDocTemplate(str(path), pagesize=(612,792), rightMargin=54, leftMargin=54,
                      topMargin=45,bottomMargin=57,title=path.stem.replace('-',' '),
                      author='FIN 43900 Project 2').build(story,onFirstPage=footer,onLaterPages=footer)


def main(only=None):
    result = json.loads((ROOT/'outputs/visible_output.json').read_text())
    tests = json.loads((ROOT/'evidence/verification-results.json').read_text())
    ui = json.loads((ROOT/'evidence/app-verification.json').read_text())
    cold = json.loads((ROOT/'evidence/cold-run.json').read_text())
    review = json.loads((ROOT/'outputs/review_evidence.json').read_text())
    review_tests = json.loads((ROOT/'evidence/review-verification.json').read_text())
    clean = json.loads((ROOT/'evidence/clean-install.json').read_text())
    if not review_tests['passed'] or not clean['passed']:
        raise ValueError('Supplemental validation or clean installation failed.')
    for name,digest in review['file_hashes'].items():
        import hashlib
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Stale supplemental evidence: '+name)
    if not all(x['passed'] for x in [tests,ui,cold]):
        raise ValueError('Cannot publish reports while executed checks fail.')
    summaries = {name: result['replays'][f'{name}_10bps']['summary'] for name in ['equal','inverse_vol','candidate']}
    a,b = summaries['candidate'],summaries['equal']
    cap = result['replays']['candidate_cap50_10bps']['summary']
    interval = result['paired_block_interval']
    table = '| Rule | Net total | Net CAGR | Net volatility | Max drawdown |\n|---|---:|---:|---:|---:|\n'
    for name,label in [('equal','Equal weight'),('inverse_vol','Inverse volatility'),('candidate','Candidate')]:
        s=summaries[name]
        table += f"| {label} | {pct(s['net_total_return'])} | {pct(s['net_cagr'])} | {pct(s['net_volatility'])} | {pct(s['max_drawdown_month_end'])} |\n"

    memo = f'''# Portfolio process: do not adopt

## Decision and committee ask
Do not approve capital deployment of the four-stock minimum-estimated-volatility
process. Authorize only further paper research against equal weight. In this study,
the optimizer delivered less return and more realized volatility than the naive
benchmark. Independent forward validation and executable timing evidence are missing.
The evidence does not establish equal weight as suitable for a client's whole portfolio.

## User, mandate and evidence boundary
The intended user is a classroom investment committee evaluating a thematic equity
research sleeve containing NVDA, MSFT, TSM and QCOM. The inherited candidate is
long-only, fully invested and minimizes estimated volatility on a 5-point weight
grid subject to a 10% historical annual arithmetic mean hurdle. The hurdle is not
a forward forecast. No reserve floor or issuer cap governs the inherited case.
Quarterly target rebalancing, a 36-month lookback, 10 bps per dollar bought or sold,
and a prospective 12-month paper-research horizon are explicit study assumptions.

## Comparison: October 2024-September 2026
The same archived USD adjusted prices, evaluation months and transaction-cost
conventions are used across rules. Weights drift between quarterly trades.
Initial purchase costs are included. Volatility is annualized sample monthly net
volatility; drawdown is measured at month ends, including initial wealth.

{table}

## What changes the decision
The candidate's net cumulative return trails equal weight by
{(b['net_total_return']-a['net_total_return'])*100:.2f} percentage points, while its
annualized net volatility is {(a['net_volatility']-b['net_volatility'])*100:.2f}
points higher. This challenges the assumption that minimizing historical estimated
risk reliably reduces subsequent realized risk. The unconstrained candidate reaches
{pct(a['max_start_equity_weight'])} in one security at a replay month boundary.
Full-sample versus recent-window estimates shift an asset weight by 20 points.
An isolated one-point TSM mean cut leaves the full-sample allocation unchanged
because the historical return floor is nonbinding; that single stress is weak evidence
of general stability.

<!-- pagebreak -->

## Sensitivities and uncertainty
A separate 50% target-cap scenario returns {pct(cap['net_total_return'])} net,
still below equal weight, with {pct(cap['net_volatility'])} volatility. Its drifted
largest position reaches {pct(cap['max_start_equity_weight'])}: a target cap is not
a continuous holdings cap. Candidate net total return at 50 bps is
{pct(result['replays']['candidate_50bps']['summary']['net_total_return'])}.
A paired 3-month block bootstrap gives a descriptive 95% interval of
{pct(interval['lower'])} to {pct(interval['upper'])} for the annualized arithmetic
mean return difference, candidate minus equal weight. It includes zero and cannot
establish superiority or repair research selection.

## Additional model-risk evidence
The candidate trails equal weight in both 12-month replay segments: candidate
{pct(review['subperiods']['candidate']['first_12']['net_total_return'])} and
{pct(review['subperiods']['candidate']['last_12']['net_total_return'])}, versus
{pct(review['subperiods']['equal']['first_12']['net_total_return'])} and
{pct(review['subperiods']['equal']['last_12']['net_total_return'])}. Applying the
accepted monitoring limits diagnostically flags one target-change breach and nine
trailing-volatility months; the first 11 months lack the required 12-return history.
No strategy or threshold was retuned. A historical liquidity proxy at an illustrative
$1 million pretrade NAV shows maximum participation of
{review['capacity_proxy']['max_participation_fraction']*100:.4f}% of prior 20-session
average dollar volume. This is not executable capacity or permission to deploy.

## Limits, monitoring and reopening
These 24 months were previously inspected; this is a chronological replay, not an
untouched holdout. Source snapshots were downloaded October 22, 2026 and prices end
September 30, 2026. Current adjustment factors, retrospectively chosen securities
and idealized same-boundary execution limit historical implementability claims.
Costs omit market impact, taxes, ADR fees and actual fills. No live pilot occurred.
The four-stock sleeve retains shared technology and market risk.

The research analyst owns quarterly paper reviews. Quarantine if consecutive
rolling-36 target recommendations change more than 15 points in any asset, trailing
12-month net sample volatility exceeds 22% annualized, inputs fail provenance, or
the candidate is infeasible. These inherited monitoring limits are governance
assumptions, not statistically calibrated guarantees. Reopen capital consideration
only after a new frozen prospective design, client mandate, operational execution,
cost/capacity evidence and independent validation have been reviewed. The companion
prospective protocol fixes the future paper comparison, execution buffer and stop
conditions; no future outcomes or pilot completion are claimed.
Named AI assistance and its verification are disclosed in Validation-and-AI-Use.pdf,
including the corrected transcripts and preserved execution history.
'''
    evolution = f'''# Research evolution and baseline status

## Edition A - selected retrospective baseline
Edition A is the student's selected earlier portfolio results, preserved unchanged
as the comparison baseline. The accompanying Edition-A-Retrospective-Baseline.pdf
summarizes those results and their limitations. Seven original files and their
hashes/provenance remain under baseline/prior-portfolio-snapshot.

The retrospective designation does not establish the original designated Brightspace
checkpoint submission or receipt. No date or authorship history is changed. Edition B
is the current process evaluation, with the accepted assumptions and recommendation
recorded in docs/student-decisions.md.

## Existing lab evidence, preserved separately
The mandate and risk-engine exercises supply decision framing and baseline checks.
Edition A supplies the four-stock universe, monthly prices, grid optimizer and
stability evidence. The provenance and point-in-time exercises supply
provenance and information-availability discipline. The completed Legend Investor
and Legend Panel labs provide business/accounting screens, not return forecasts or
an independent portfolio holdout. Project 1 contributes packaging patterns.

No earlier source files were overwritten. The inherited engine's functions are
reused for covariance, weights and risk calculations. Original paths remain in
the provenance manifest; a display label does not change their origin.

## Current research conclusion
{result['decision']} The chronological comparison challenges the case for adopting
the optimizer: candidate net total return is {pct(a['net_total_return'])} versus
{pct(b['net_total_return'])} for equal weight; candidate net volatility is
{pct(a['net_volatility'])} versus {pct(b['net_volatility'])}. These are outputs of
the archived study, not current forecasts or proof of a universal ranking.

<!-- pagebreak -->

## Edition A to Edition B evidence comparison
| Topic | Edition A retrospective baseline | Edition B evidence and implication | Driver |
|---|---|---|---|
| Portfolio decision | Provisional pilot | Reject capital deployment; permit further paper research only | New analysis and explicit claim limits |
| Stability | Single TSM mean stress leaves weights unchanged | Window shift and rolling target instability remain material | Prior evidence plus added replay |
| Evaluation | Full-sample estimated metrics | Three rules on a rolling chronological replay, with costs | Implementation and independent tests |
| Concentration | No personal issuer cap | Up to 95% starting weight; 50% target-cap case retained separately | Added failure analysis |
| Timing | Archived source provenance | Prior-return alignment verified; historical-vintage and executable timing limitations preserved | Labs 16-17 discipline |
| Reproducibility | Installed course environment | New clean environment reproduces material outputs and all numerical/interface checks | Added installation audit |
| Baseline boundary | Earlier results selected retrospectively as Edition A | Same original history; checkpoint receipt remains unestablished | Student baseline selection |

This is an Edition A-to-B comparison using the selected retrospective baseline;
it is not proof that the original checkpoint was completed.
Development contributions and checks are documented in the companion validation
record. No peer event or student prediction is inferred. Student review must identify
accepted assumptions and the resulting decision in docs/student-decisions.md.

## What changed, why, and what remains uncertain
The decision changed from a provisional monitored pilot to paper research only.
The driver was mixed: earlier course/lab discipline, student review of assumptions,
and AI-assisted implementation and validation. The same-universe, costed comparison
and source reconstruction justify qualifying the optimizer rather than adopting it.
Numerical correctness is accepted on the tests below; future risk superiority is rejected.

## AI-output check and disposition
Codex helped implement the covariance/grid optimizer and propose its comparison.
The independent known-answer fixture uses four uncorrelated assets, each with 20%
volatility and equal weights: 20% / sqrt(4) = 10% portfolio volatility. tests.py
checks that value and the optimizer's equal-weight answer. The implementation passes;
the claim that lower estimated risk warrants deployment is rejected by the costed
replay. This is an independently derived fixture executed through the assistant,
not an independent human review. See the named AI-use register for attribution.

## Recording and original-process evidence
Three actual YouTube links and student-supplied captions are now retained in the
manifest and docs/transcript-video-1.txt through transcript-video-3.txt. Corrected
transcripts preserve the recorded conclusion. Full audiovisual and access checks
remain separate. Video 1's supplied text does not explicitly identify an AI output;
this written check supplements the report and does not claim that it was spoken.
Original Edition A checkpoint evidence and the saved personal rerun remain unresolved.
The prediction, first assistant execution and later self-report are preserved honestly;
a later rerun cannot recreate an earlier AI-closed execution or checkpoint.
'''
    # Use page one's free space for the decision/AI check, keeping the comparison
    # and recording-status paragraph together on page two.
    extra_start=evolution.index('## What changed, why, and what remains uncertain')
    extra_end=evolution.index('## Recording and original-process evidence')
    evidence_explanation=evolution[extra_start:extra_end]
    evolution=evolution[:extra_start]+evolution[extra_end:]
    evolution=evolution.replace('<!-- pagebreak -->',evidence_explanation+'\n<!-- pagebreak -->',1)
    original=json.loads((ROOT/'baseline/prior-portfolio-snapshot/personal-results.json').read_text())
    original_manifest=json.loads((ROOT/'baseline/prior-portfolio-snapshot/baseline-manifest.json').read_text())
    for item in original_manifest['files']:
        import hashlib
        if hashlib.sha256((ROOT/'baseline/prior-portfolio-snapshot'/item['preserved_file']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Preserved baseline file changed: '+item['preserved_file'])
    baseline_rows='| Historical estimate | NVDA / MSFT / TSM / QCOM weights | Annual mean | Annual volatility |\n|---|---|---:|---:|\n'
    for key,label in [('all_months','All 60 monthly returns'),('last_36','Final 36 monthly returns'),('TSM_minus_1_point','TSM mean minus 1 point')]:
        item=original['runs'][key]
        weights=' / '.join(f'{value*100:.0f}%' for value in item['weights'].values())
        baseline_rows+=f"| {label} | {weights} | {pct(item['return'])} | {pct(item['volatility'])} |\n"
    baseline_text=f'''# Edition A - retrospective baseline

## Designation and preserved history
The student selected the earlier portfolio results as Edition A for comparison
with Edition B. This summary is prepared now from the unchanged retained evidence;
it is not represented as an original AI-off checkpoint PDF or a Brightspace receipt.
The baseline archive was preserved at {original_manifest['preserved_at_utc']}.
All seven retained file hashes pass verification. Original source paths and dates
remain in baseline/prior-portfolio-snapshot/baseline-manifest.json.

## Decision and method at the baseline
The selected baseline supports a provisional monitored pilot, subject to further
evidence. Its universe is NVDA, MSFT, TSM and QCOM. The method minimizes estimated
volatility among long-only fully invested five-point allocations, subject to a
10% annual historical arithmetic-mean hurdle and no reserve floor. A universe
member may have zero weight. The securities do not constitute a broadly diversified
whole-client portfolio.

## Preserved results
The dataset has 61 month-end adjusted prices and 60 monthly returns, ending
September 2026, downloaded October 22, 2026. The table reports estimated annual
arithmetic means and sample volatility, gross of costs; these are not forecasts
or realized rolling-strategy cumulative returns.

{baseline_rows}

## Original limits and conditional action
The isolated TSM mean stress leaves allocation weights unchanged because the
historical return floor remains nonbinding. The 60-versus-36-window comparison
changes an asset weight by 20 percentage points, exposing estimation sensitivity.
The baseline's provisional-pilot position calls for forward tracking and quarterly
stability review, with the retained 15-point target-change and 22% realized-volatility
limits. No live pilot outcome is claimed.

## What Edition B adds
Edition B compares three rules on a rolling, costed chronological replay, audits
constraints and monitoring, adds subperiod and historical liquidity evidence, and
verifies a clean installation. It changes the action to no capital deployment and
further paper research only. The retrospective baseline designation supplies the
comparison record; original checkpoint compliance remains a separate unresolved item.
'''
    changed_record = ''
    student_rerun_note='No later student rerun has been recorded.'
    attestation_path=ROOT/'evidence/locked-exercise/student-rerun-attestation.json'
    student_rerun_path=ROOT/'evidence/locked-exercise/student-rerun.json'
    if attestation_path.exists():
        student_rerun_note=('AI-closed student rerun - self-reported: the student reports matching results '
            'and personal prediction/reasoning. The generated student-rerun.json is unavailable; '
            'matching output is not independently verified. This rerun followed outcome review; '
            'the original execution remains preserved.')
    if student_rerun_path.exists():
        personal=json.loads(student_rerun_path.read_text())
        preserved=json.loads((ROOT/'evidence/locked-exercise/execution.json').read_text())
        if personal.get('tools_closed_self_attestation') is True and personal.get('matches_original_result') is True and personal.get('before')==preserved['before']['summary'] and personal.get('after')==preserved['after']['summary'] and personal.get('original_snapshot_sha256')==preserved['snapshot_sha256']:
            student_rerun_note=('A later AI-closed student rerun is recorded with tools-closed self-attestation. '
                'Its saved summaries and snapshot hash match the original evidence. The rerun followed '
                'review of the original outcome, and the original prediction/execution history is retained. '
                'Tool state and operator identity are self-attested, not independently observed.')
    changed_path = ROOT/'evidence/locked-exercise/execution.json'
    if changed_path.exists():
        changed = json.loads(changed_path.read_text())
        precommit = json.loads((ROOT/'evidence/locked-exercise/precommit.json').read_text())
        before, after = changed['before']['summary'], changed['after']['summary']
        changed_record = f'''## Preserved prediction and executed window change
Material input: rolling estimation window, 36 to 24 monthly returns. The 24
evaluation months, four stocks, 10-bps one-way costs, hurdle, grid and trade schedule
were held fixed. Prediction preserved at {precommit['precommitted_at_utc']}.
Code/data snapshot SHA-256 (continued on next line):
{precommit['snapshot_sha256'][:32]}
{precommit['snapshot_sha256'][32:]}
Exact original prediction, before/after outputs and operator record are in
evidence/locked-exercise/precommit.json, execution.json and execution-provenance.json.

The preserved student prediction expected higher realized net volatility, more
aggressive target movement and an unchanged recommendation under the 24-month
lookback. The student's stated reasoning was fewer observations and greater
estimation noise in the concentrated technology sleeve. This reasoning was a
prediction, not an empirically isolated causal explanation. Expected decision:
continue paper research only. Actual decision: unchanged.

Net cumulative return changed from {pct(before['net_total_return'])} to
{pct(after['net_total_return'])}; annualized realized net volatility fell from
{pct(before['net_volatility'])} to {pct(after['net_volatility'])}, contrary to the
volatility prediction. Maximum quarterly target movement rose from
{before['max_target_change_points']:.0f} to {after['max_target_change_points']:.0f}
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
'''
    subperiod_table='| Rule | First 12 months net return | Last 12 months net return |\n|---|---:|---:|\n'
    for rule,label in [('equal','Equal weight'),('inverse_vol','Inverse volatility'),('candidate','Candidate')]:
        item=review['subperiods'][rule]
        subperiod_table+=f"| {label} | {pct(item['first_12']['net_total_return'])} | {pct(item['last_12']['net_total_return'])} |\n"
    validation = f'''# Validation and AI-use record

## Decision, version and information boundary
Decision: {result['decision']} Material input and code SHA-256 hashes are embedded
in outputs/visible_output.json. Its UTC run timestamp is {result['generated_at_utc']}.
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
{a['traded_nav_sum']:.4f} over 24 months. Market impact, taxes, actual spreads,
ADR fees, capacity and executable fills are not established.

<!-- pagebreak -->

## Executed validation
The numerical audits ran {tests['tests_run'] + review_tests['tests_run']} test methods
with zero failures/errors: {tests['tests_run']} core and {review_tests['tests_run']} supplemental.
The actual Streamlit page passed {len(ui['checks'])} checks. Evidence files preserve
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
rolling target changes reach {a['max_target_change_points']:.0f} points. It also
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
difference interval is {pct(interval['lower'])} to {pct(interval['upper'])}.
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

{subperiod_table}

## Target constraints and monitoring
The per-trade audit checks nonnegative weights, funding, the candidate historical
mean hurdle and the separate 50% target cap. Baseline and candidate trade records
retain the actual values. These target checks do not certify suitability or future
losses. Drifted holdings can exceed the 50% target after market movements.

Applying the accepted 15-point movement and 22% trailing-12-month volatility
thresholds diagnostically flags {review['monitoring']['target_breach_count']} target
event and {review['monitoring']['volatility_breach_count']} volatility months.
The first {review['monitoring']['unavailable_volatility_months']} months have too
few observations for that volatility measure. The replay was not stopped at these
flags, so this is not a simulation of a functioning kill-rule strategy. The evidence
supports quarantine/review rather than retrospective threshold relaxation.

## Historical liquidity proxy, not executable capacity
For each trade, compute raw daily close times raw daily volume over the prior 20
valid trading observations ending no later than the estimation cutoff. Do not mix
adjusted prices with unadjusted share volume. At an explicitly illustrative fixed
$1 million pretrade NAV, maximum participation across the three rules is
{review['capacity_proxy']['max_participation_fraction']*100:.4f}% of that average.
Per-asset trade fractions reconcile to the self-financing cost convention.
The 1% participation threshold is a scenario assumption, not a market standard
or permission to allocate. The proxy does not establish spreads, impact, fills,
liquidity under stress, intraday availability or executable capacity. It does not
override the failed investment comparison.

## Clean installation and independent process replay
A new venv without system-site-packages installed the pinned requirements from
the package index. An isolated project copy from an unrelated working directory
reproduced both material output files and passed 19 numerical and {len(ui['checks'])} interface
checks. Dependency checking found no broken requirements; resolved packages are
frozen in requirements-lock.txt. The first failure was absent pip in the existing
course environment, followed by blocked sandbox networking. Creating a new venv
bootstrapped pip; approved network installation resolved the download failure.
The clean replay took {clean['elapsed_seconds']:.2f} seconds after installation.
This is automated evidence, not an observed unaided human reviewer or student defense.
The proposed prospective protocol fixes future timing, comparison metrics and stop
conditions. It does not repair the historical holdout or claim future observations.

<!-- pagebreak -->

## Locked record and later student rerun
The student's prediction was preserved before the first execution, performed
through the assistant. The snapshot, hashes and student reconciliation remain
recorded. Local hashes do not independently establish authorship or tool state.

{student_rerun_note}

{changed_record}

## Named material AI-use register
| Tool / exposed version / date | Material contribution | Check and disposition |
|---|---|---|
| Codex; exact model/version not exposed in the working tools; November 17, 2026 | Project research design, code, validation, interface, reports, rehearsal drafts and requested changed-input execution | Source reconstruction, independent numeric fixtures, mutation tests and interface replay; student accepted assumptions and recommendation; exact user prediction and later reflection preserved; execution provenance retained |
| Codex, GPT-6 (system-exposed identity; exact backend build not exposed); November 19, 2026 | Editorial correction of supplied YouTube captions; submission audit; documentation, report, manifest and private publication preparation | Material quoted results checked against frozen outputs; timestamps retained from supplied captions; substantive uncertainties flagged; human-only events and media review not fabricated |

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
Video 1: https://youtu.be/tMAmXiDBVBg - captions end at 2:53.120 (maximum 3:00).
Video 2: https://youtu.be/EZolrbd3xOQ - captions end at 4:57.280 (maximum 5:00).
Video 3: https://youtu.be/sqgNrHPguZ4 - captions end at 3:14.400 (maximum 5:00).
These are caption endpoints, not independently measured media durations. Section
indices are in the manifest. Actual video/audio alignment and access need verification.
Separately, November 19 public YouTube page metadata reports playable status,
captions and durations of 2:52, 4:56 and 3:13, all within limits. Caption endpoints
can extend beyond the reported media endpoint; the supplied section indices
remain inside each duration. Metadata is not full playback verification.
Caption corrections include Edition A/B, Streamlit, requirements-lock.txt, square
root of four, allocation instability and capital deployment. Video 3's immediate
spoken correction is consolidated to 70.97%. No later written improvement is
represented as original speech. Personal names are omitted from the retained text.

Video 1's concentration explanation is not an isolated causal finding. The
comparison establishes realized differences, not their sole cause. Video 2's
captioned line 12 is retained and flagged against the guide's line 112. The
Video 1 AI-output requirement and webcam requirement cannot be certified from
the supplied text. Do not conceal these limits by rewriting the transcript.

## Remaining original and submission evidence
Original Edition A checkpoint acceptance, the saved personal rerun, actual oral
ownership evidence, grader access and the successful Brightspace submission remain
to be verified. The manual checklist supplies exact actions. Missing checkpoint
history is not repaired by a retrospective label or an already-seen test.
'''
    docs = [('Edition-A-Retrospective-Baseline','edition-a-retrospective-baseline',baseline_text),
            ('Decision-Memo', 'decision-memo', memo),
            ('Research-Evolution', 'research-evolution', evolution),
            ('Validation-and-AI-Use', 'validation-and-ai-use', validation)]
    summary=f'''# Verification summary for recording

- Core financial/source test methods: {tests['tests_run']}, passed.
- Supplemental monitoring/constraint/liquidity test methods: {review_tests['tests_run']}, passed.
- Total numerical methods: {tests['tests_run']+review_tests['tests_run']}.
- Actual interface checks: {len(ui['checks'])}, passed, including missing/malformed output handling.
- All 244 monthly prices reconstructed from preserved sources; no filling.
- New clean environment: installed dependencies; pip check found no broken requirements.
- Both main and supplemental material outputs reproduced in an isolated project copy.
- First setup failures: absent pip in the original course environment and restricted networking.
- Resolution: new venv with pip bootstrap, approved downloads, complete dependency lock.
- Clean replay after installation: {clean['elapsed_seconds']:.2f} seconds.
- Candidate diagnostic flags: one target-change event; nine trailing-volatility months.
- First 11 months do not have a full 12-return volatility window.
- These are automated checks, not an observed unaided human reviewer.

Evidence: verification-results.json, review-verification.json, app-verification.json
and clean-install.json under evidence/. Financial/model limitations remain in the
validation report. No grade, human authorship or checkpoint acceptance is inferred.
'''
    (ROOT/'docs/verification-summary.md').write_text(summary,encoding='utf-8')
    counts_path = ROOT/'evidence/pdf-page-counts.json'
    page_counts = json.loads(counts_path.read_text()) if counts_path.exists() else {}
    for filename, source, text in docs:
        if only and filename != only:
            continue
        (ROOT/f'docs/{source}.md').write_text(text.strip()+'\n',encoding='utf-8')
        path = ROOT/f'{filename}.pdf'
        render_pdf(text,path)
        (ROOT/f'docs/{source}.pdf').write_bytes(path.read_bytes())
        page_counts[filename] = len(PdfReader(path).pages)
    if page_counts['Decision-Memo'] > 2:
        raise ValueError('Memo exceeds two pages.')
    (ROOT/'evidence/pdf-page-counts.json').write_text(json.dumps(page_counts,indent=2)+'\n')
    print(json.dumps(page_counts))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',choices=['Edition-A-Retrospective-Baseline','Decision-Memo','Research-Evolution','Validation-and-AI-Use'])
    main(parser.parse_args().only)
