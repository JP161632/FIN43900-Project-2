# Preserved locked execution

Original lookback: 36 monthly returns. Changed lookback: 24.
Evaluation months, costs, universe, grid, hurdle and trade schedule are held fixed.

| Metric | Before | After |
|---|---:|---:|
| net_total_return | 0.24850780 | 0.25519312 |
| net_cagr | 0.11736646 | 0.12035402 |
| net_volatility | 0.29611106 | 0.27825264 |
| max_drawdown_month_end | -0.28140528 | -0.28127128 |
| max_target_change_points | 20.00000000 | 25.00000000 |
| infeasible_rebalances | 0.00000000 | 0.00000000 |

Return/volatility/drawdown are decimals. Target movement is in percentage points.

## Student reconciliation supplied after reviewing the result

- Actual decision effect: The recommendation remains against capital deployment of the current process and in favor of further paper research. The four-stock thematic sleeve remains concentrated, still trails equal weight in the replay, and lacks independent prospective validation and implementation evidence.
- Prediction reconciliation: The largest quarterly target change rose from 20 to 25 percentage points, supporting the separate target-instability concern. Annualized realized net volatility fell from 29.61% to 27.83%, contrary to the original volatility prediction. Target instability and realized return volatility are distinct metrics.
- Why the action did not change: The small performance improvement does not resolve the concentration, baseline underperformance or validation limitations. Recent observations, noise or timing are possible explanations for changed results, but this one replay does not isolate the cause or establish persistence.

The corrected presentation version is in docs/student-reflection.md. It was edited
for accuracy at the student's request; the original response is preserved below.

## Original student response - verbatim

"The fact that the tarfget weights jumped over .25% shows that our worry about sample size sensitivity. Shorter lookback periods made the optimizer act more to recent noise. This caused aggressive quarterly rebalancing. While volatility decreased slightly, i believe it was just a timing thing and not something that is sustainable. The findings also did not change the fact that the fundamental issue of having a 4 stock model is too aggressive and does not support having real capital deployed"

## Numerical and claim checks for presentation

- Largest quarterly target change: 20 to 25 percentage points, an increase of five percentage points. The original response's ".25%" is a unit error; use 25 percentage points when presenting the actual result.
- Annualized realized net volatility decreased from 29.61% to 27.83%, contrary to the original volatility prediction. The separate target-instability prediction was supported on the maximum-change metric.
- This single replay does not isolate noise as a cause or establish that the volatility improvement will be unsustainable. Those explanations remain hypotheses.
- A four-stock thematic sleeve is concentrated. This study does not establish that every four-stock strategy is universally unsuitable; the current recommendation is specific to this process, evidence and stated use case.

The response was supplied by the student in chat and transcribed here. Actual
execution provenance is preserved separately.

## Later personal rerun - student report

The student reports completing an AI-closed student rerun and obtaining matching
results, and reiterates that the original prediction and reasoning were their own.
This later activity is labelled "AI-closed student rerun - self-reported". The
generated student-rerun.json was not available in this workspace at review, so the
matching-output claim is recorded as reported, not independently verified. The
rerun followed review of the original result; the earlier records remain unchanged.

Do not edit the saved prediction, archive or execution JSON.
