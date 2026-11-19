# Changed-input result - assistant analysis, not student reconciliation

The student's 36-to-24-month prediction was preserved before execution. At the
student's explicit request, the assistant froze and ran the case. The saved
prediction was not rewritten. This is not represented as an AI-closed student run.

| Metric | 36-month estimate window | 24-month estimate window |
|---|---:|---:|
| Net cumulative return | 24.85% | 25.52% |
| Net CAGR | 11.74% | 12.04% |
| Annualized realized net volatility | 29.61% | 27.83% |
| Month-end maximum drawdown | -28.14% | -28.13% |
| Largest consecutive quarterly target change | 20 percentage points | 25 percentage points |
| Infeasible quarterly rebalances | 0 | 0 |

Evaluation months, costs, universe, grid, hurdle and trade schedule were held fixed.
The volatility prediction was not borne out: realized net volatility declined by
approximately 1.79 percentage points. The target-instability prediction was supported
on the maximum-change metric: it rose by five percentage points. Those are different
measures; more variable target recommendations do not mechanically imply more
volatile subsequent returns. Drawdown was nearly unchanged and slightly smaller.

Under the existing decision policy, this result does not justify capital deployment.
The shortened-window candidate still trails equal weight's 70.97% net cumulative
return and lacks independent prospective, execution and suitability evidence.
The small cumulative return improvement is descriptive, not evidence of superiority.

The student subsequently supplied their own reflection and retained the recommendation
against deployment. It is preserved verbatim in student-reconciliation.md, with
separate numerical and claim checks. The unit error ".25%" is corrected to a maximum
target change of 25 percentage points, up from 20. The student's explanation involving
noise and timing remains an interpretation, not an isolated causal finding.

The original archive, precommit and execution records are retained unchanged.
See execution-provenance.json for the operator record and remaining course requirement.
