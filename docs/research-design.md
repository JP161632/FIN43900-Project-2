# Research design and status

This build uses the selected earlier portfolio evidence, labelled Edition A as a
retrospective baseline. An original successful checkpoint receipt is not established
by that selection. Preserve the original dates and source provenance; the label
does not turn this material into an earlier AI-off checkpoint submission.

## Decision contract

Intended user: a classroom investment committee evaluating a four-stock thematic
research sleeve. Action: decide whether the existing minimum-variance method merits
further paper research relative to equal-weight and inverse-volatility rules.
No real capital allocation is authorized by this study.

Inherited universe: NVDA, MSFT, TSM, QCOM. Inherited candidate: long-only, fully
invested, minimum estimated annual volatility on a five-percentage-point grid,
subject to a 10% annualized historical arithmetic mean hurdle, no reserve minimum.
The hurdle is a model filter, not a forward expected return or guaranteed goal.
No positive weight in any individual stock is required. There is no issuer cap in
the inherited case; a 50% cap is tested separately. This is a concentrated equity
sleeve, not a diversified whole-client portfolio or the Meridian mandate.

New study assumptions: quarterly target rebalancing, a rolling 36-return estimation
window, and 10 bps per dollar bought or sold. These are explicit research assumptions,
not preferences supplied by a real client. Equal weight is the primary naive
benchmark within the same universe; inverse volatility is the second baseline.
The 24-month replay spans October 2024 through September 2026. The subsequent paper
research horizon would be 12 months, with quarterly reviews; no such pilot has run.

## Registered build scope

Compare three rules at 0, 10, 25 and 50 bps; candidate only with a 50% target cap;
all-60 versus final-36 estimation windows; TSM mean minus one percentage point;
infeasible hurdle, bad source hash, missing month, invalid prices, and invalid costs.
Record every case in the generated selection ledger, including failed or infeasible
cases. This design is written after the dataset and prior lab outputs were inspected;
it is not a preregistered independent holdout. Do not optimize it after seeing results.

All replay decisions use returns ending before each test month. Execution is idealized
at the preceding monthly boundary with no additional availability or order delay;
same-close execution is not demonstrated. Today's archived adjusted-price factors and
the universe were selected retrospectively. Therefore this is a chronological replay,
not a point-in-time investable backtest, untouched holdout, or proof of predictive skill.

## Decision policy

Do not approve capital deployment: missing independent holdout, execution timing,
client suitability and implementation evidence are adoption blockers regardless of
historical performance. Permit only further paper research if reproducibility and
mechanical checks pass. Report relative replay performance, cost sensitivity,
concentration, estimation instability and uncertainty as descriptive evidence.
Do not change failure thresholds to make the candidate pass.

For future paper monitoring, carry forward Lab 15's 15-percentage-point limit on
changes between consecutive quarterly rolling-36 target recommendations, and its
22% realized-volatility limit. Define realized volatility as sample standard deviation
of the trailing 12 monthly net sleeve returns times sqrt(12), once 12 returns exist.
Do not describe this one-year estimate as precise. Quarantine on a missing source,
infeasible candidate, target instability above 15 points, or volatility above 22%.
Research analyst owns quarterly review; committee owns reopening or changing policy.

## Human-only evidence still required

The student must complete the Locked Changed-Input Record prediction before running
that designated exercise with AI closed, explain the submitted code, record videos,
verify access and obtain checkpoint guidance. Automated tests do not establish any
of those events. Draft scripts are not transcripts of recordings.
