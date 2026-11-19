# Preserved locked execution

Original lookback: 36 monthly returns. Changed lookback: 30.
Evaluation months, costs, universe, grid, hurdle and trade schedule are held fixed.

|Metric|Before|After|
|-|-:|-:|
|net\_total\_return|0.24850780|0.25885223|
|net\_cagr|0.11736646|0.12198584|
|net\_volatility|0.29611106|0.28689341|
|max\_drawdown\_month\_end|-0.28140528|-0.28140528|
|max\_target\_change\_points|20.00000000|20.00000000|
|infeasible\_rebalances|0.00000000|0.00000000|

Return/volatility/drawdown are decimals. Target movement is in percentage points.

## Student must complete after reviewing the actual result

* Actual decision effect:My recommendation remains firmly to not deploy capital and continue paper research only. Even though the 30-month test showed a slight improvement in net return from 24.85% to 25.89% and a modest drop in volatility, the portfolio still has the exact same structural vulnerabilities. It suffered an identical maximum drawdown of -28.14%, remains heavily concentrated across only four tech stocks, and still lags far behind our simple Equal-Weight benchmark of roughly 71%. A minor statistical uptick in a backtest is nowhere near enough justification to risk real money.
* Prediction reconciliation:My volatility prediction turned out to be accurate, but my target-change prediction was not supported. I predicted that dropping six months of older data would reduce annualized volatility into the 28% to 29% range, and it landed right at 28.69%, down from 29.61%. However, based on our previous 24-month test where allocation shifts jumped to 25 points, I also predicted that target changes would push past our 20-point baseline. Instead, the maximum quarterly target change stayed completely flat at 20.00 points, showing that a 30-month window still had enough data cushion to prevent the aggressive turnover we saw with 24 months.
* Failure diagnosis or why the action did not change:The action did not change because shortening the lookback window is simply tweaking an arbitrary parameter, not fixing the core flaws of the investment strategy. Shaving roughly 0.9% off volatility and adding 1% to total return does not solve the reality that this model concentrated up to 95% of our portfolio into a single stock, trails a basic benchmark by a wide margin, and lacks any live forward testing. A minor lookback adjustment might slightly improve historical numbers, but it does not make an overly aggressive four-stock paper model ready for live deployment.

Do not edit the saved prediction, archive or execution JSON.

