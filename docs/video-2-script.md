VIDEO 2 — ACTUAL REPOSITORY WALKTHROUGH (maximum 5 minutes)
This replaces the old Video 2 white-panel presentation. Videos 1 and 3 are unchanged.
This is a rehearsal script, not a transcript of a completed recording.

BEFORE RECORDING — DO THIS ONCE
1. Open Visual Studio Code. Choose File > Open Workspace from File.
   Select projects/project-2/recording/Video-2.code-workspace.
   If you are already in the course repository, that is the path from its root.
   The Explorer on the left should show the project-2 files, including analysis.py.
2. Open these three files using Ctrl+P: README.md, analysis.py, tests.py.
3. Choose Terminal > New Terminal. Check its prompt ends in project-2.
   Run the command below ONCE as a practice check. Expect Ran 4 tests and OK.
   This command runs existing tests; it does not change the locked record or results.
   Also have the running Portfolio Committee Review app open in your browser.
   If it is not running, use a SECOND terminal in project-2 and run:
   & ..\..\.venv\Scripts\python.exe -m streamlit run app.py
   Open the Local URL it prints. Leave that server terminal running.
4. Keep this script on a phone, printed page or second display outside your capture.
5. Record the ENTIRE DISPLAY with your mic so switching from VS Code to the browser
   app at section 7 is captured. A VS Code-only window recording will miss the app.
   Close unrelated windows. Do not record this instruction page. No PDF is needed.
6. Start at README.md and follow the seven sections below. Only read SAY THIS aloud.
   Leave time for navigation. Rehearse under 5:00; aim for about 4 minutes.

COMMAND (paste exactly; use the VS Code terminal in the project-2 folder):
& ..\..\.venv\Scripts\python.exe .\recording\video2_demo.py

If the prompt is in a different folder, first enter:
Set-Location 'C:\Users\13177\FIN43900-Fall2026\projects\project-2'

During the recording, run the command again at section 6 so the test is shown live.
This is not a request to repeat the locked exercise or change your prediction.

SECTION 1: README.md: architecture and reproduction

DO THIS (do not read):
Press Ctrl+P, type README.md, press Enter. Press Ctrl+Home. Explain the setup commands. Then press Ctrl+F, type Evidence flow and file map, press Escape. Point across the arrow-separated file map.

SAY THIS:
This repository evaluates a four-stock portfolio process against simple baselines. A clean user creates a Python environment, installs requirements-lock.txt, runs analysis.py and review_analysis.py, and runs the tests. Streamlit then displays the saved results. No credentials or fresh data download are needed for the analysis. The file map shows archived daily sources flowing into audited monthly prices, the analysis engine, frozen results and the application. The saved adjustment factors do not establish historical point-in-time data availability.

SECTION 2: analysis.py: the optimizer

DO THIS (do not read):
Press Ctrl+P, type analysis.py, press Enter. Press Ctrl+G, type 92, press Enter. Point at the cap, hurdle and lower-volatility checks. If needed, scroll a little to keep candidate() visible.

SAY THIS:
The candidate function searches long-only, fully invested allocations on a five-percentage-point grid. It rejects allocations above the position cap or below the ten percent historical-mean hurdle, and keeps the feasible allocation with the lowest estimated volatility. This is a historical optimization criterion, not a promised return or a guarantee of low future risk.

SECTION 3: analysis.py: prevent future returns entering the estimates

DO THIS (do not read):
Stay in analysis.py. Press Ctrl+G, type 138, press Enter. Point to training = returns.iloc[i-lookback:i], then rebalance = (i-36) % 3 == 0.

SAY THIS:
The replay selects training returns before the evaluation month. The slice ends before index i, and rebalancing occurs every three months. The evaluation start remains fixed when the lookback changes, so the comparison uses the same evaluation months. Holdings drift between trades. This protects the estimation window from using that month’s return, but it does not prove executable same-close trading.

SECTION 4: analysis.py: trading costs

DO THIS (do not read):
Press Ctrl+G, type 112, press Enter. Point at the fee equation in the function description and bps / 10000. Scroll a little to show cost and traded near the end of this function.

SAY THIS:
The trade-cost function charges purchases and sales, including initial deployment. Basis points are divided by ten thousand. It solves the fee from portfolio capital, because the fee also changes how much capital remains to buy the target holdings. It checks invalid inputs rather than silently accepting unfunded trades. It does not model taxes or actual market impact.

SECTION 5: tests.py: explain the independent answer before running

DO THIS (do not read):
Press Ctrl+P, type tests.py, press Enter. Press Ctrl+G, type 33, press Enter. Point to .20, .25 and the .10 volatility assertion in test_independent_known_answer.

SAY THIS:
The highest-risk claims include the risk calculation and net-return accounting. This fixture uses four uncorrelated assets, each with twenty percent volatility and equal weights. The independent answer is ten percent portfolio volatility: twenty percent divided by the square root of four. The test checks both that result and the optimizer’s equal-weight answer. Other tests check exact fee arithmetic, reject a corrupted source hash, and reconstruct the first month’s net return and subsequent weight drift.

SECTION 6: Integrated terminal: run the demonstration live

DO THIS (do not read):
Choose Terminal > New Terminal from the VS Code top menu. Paste the command below and press Enter. Wait for the command to finish. Show all four test names and the final Ran 4 tests / OK. Read this paragraph ONLY if all four actually pass. If any fail, stop recording and investigate. You may enlarge the terminal by dragging its top edge upward.

COMMAND:
& ..\..\.venv\Scripts\python.exe .\recording\video2_demo.py

SAY THIS:
I am now running those four existing checks from the submitted repository. This is a live validation demonstration, separate from the locked changed-input exercise. All four checks pass. The known-answer and fee fixtures challenge numerical logic, the corruption test checks a failure condition, and the first-month calculation checks the link from returns through costs to holdings. Passing these tests supports the implementation; it does not establish investment profitability.

SECTION 7: Running app: show the finished product and conclude

DO THIS (do not read):
Switch to the running Portfolio Committee Review app in your browser. Scroll to Compare portfolio rules. Set One-way trading cost (basis points) to 10. Show the three-rule results table and scroll slightly to the wealth chart. Change the cost to 25 to show the interface updating, then RETURN IT TO 10 before quoting the numbers below. Keep the table visible for the conclusion. Stop your recorder after the paragraph. This is the app, not START-HERE.html.

SAY THIS:
This is the finished Portfolio Committee Review app. It displays the saved research results rather than recalculating the optimizer in the browser. The cost selector switches between precomputed scenarios, updating the comparison and wealth chart. Returning to ten basis points, the optimized portfolio earned twenty-four point eight-five percent cumulatively, compared with seventy point nine-seven percent for equal weight. The four tests I just ran check selected calculations and failure handling; the broader saved validation covers additional cases. The short evaluation period and concentrated four-stock universe remain material limitations. My recommendation is no capital deployment and further paper research only.

AFTER RECORDING
Play the file once: check audible voice, readable code and terminal, actual successful
test output, visible running app, and duration no longer than 5:00. Save as Video 2.
The final transcript must match your actual recording, not simply copy this draft.
