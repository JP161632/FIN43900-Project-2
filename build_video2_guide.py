"""Build the actual-repository Video 2 instructions and rehearsal script."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'recording'
COMMAND = r'& ..\..\.venv\Scripts\python.exe .\recording\video2_demo.py'
STEPS = [
    ('README.md: architecture and reproduction',
     'Press Ctrl+P, type README.md, press Enter. Press Ctrl+Home. Explain the setup commands. Then press Ctrl+F, type Evidence flow and file map, press Escape. Point across the arrow-separated file map.',
     '''This repository evaluates a four-stock portfolio process against simple baselines. A clean user creates a Python environment, installs requirements-lock.txt, runs analysis.py and review_analysis.py, and runs the tests. Streamlit then displays the saved results. No credentials or fresh data download are needed for the analysis. The file map shows archived daily sources flowing into audited monthly prices, the analysis engine, frozen results and the application. The saved adjustment factors do not establish historical point-in-time data availability.'''),
    ('analysis.py: the optimizer',
     'Press Ctrl+P, type analysis.py, press Enter. Press Ctrl+G, type 92, press Enter. Point at the cap, hurdle and lower-volatility checks. If needed, scroll a little to keep candidate() visible.',
     '''The candidate function searches long-only, fully invested allocations on a five-percentage-point grid. It rejects allocations above the position cap or below the ten percent historical-mean hurdle, and keeps the feasible allocation with the lowest estimated volatility. This is a historical optimization criterion, not a promised return or a guarantee of low future risk.'''),
    ('analysis.py: prevent future returns entering the estimates',
     'Stay in analysis.py. Press Ctrl+G, type 138, press Enter. Point to training = returns.iloc[i-lookback:i], then rebalance = (i-36) % 3 == 0.',
     '''The replay selects training returns before the evaluation month. The slice ends before index i, and rebalancing occurs every three months. The evaluation start remains fixed when the lookback changes, so the comparison uses the same evaluation months. Holdings drift between trades. This protects the estimation window from using that month’s return, but it does not prove executable same-close trading.'''),
    ('analysis.py: trading costs',
     'Press Ctrl+G, type 112, press Enter. Point at the fee equation in the function description and bps / 10000. Scroll a little to show cost and traded near the end of this function.',
     '''The trade-cost function charges purchases and sales, including initial deployment. Basis points are divided by ten thousand. It solves the fee from portfolio capital, because the fee also changes how much capital remains to buy the target holdings. It checks invalid inputs rather than silently accepting unfunded trades. It does not model taxes or actual market impact.'''),
    ('tests.py: explain the independent answer before running',
     'Press Ctrl+P, type tests.py, press Enter. Press Ctrl+G, type 33, press Enter. Point to .20, .25 and the .10 volatility assertion in test_independent_known_answer.',
     '''The highest-risk claims include the risk calculation and net-return accounting. This fixture uses four uncorrelated assets, each with twenty percent volatility and equal weights. The independent answer is ten percent portfolio volatility: twenty percent divided by the square root of four. The test checks both that result and the optimizer’s equal-weight answer. Other tests check exact fee arithmetic, reject a corrupted source hash, and reconstruct the first month’s net return and subsequent weight drift.'''),
    ('Integrated terminal: run the demonstration live',
     'Choose Terminal > New Terminal from the VS Code top menu. Paste the command below and press Enter. Wait for the command to finish. Show all four test names and the final Ran 4 tests / OK. Read this paragraph ONLY if all four actually pass. If any fail, stop recording and investigate. You may enlarge the terminal by dragging its top edge upward.',
     '''I am now running those four existing checks from the submitted repository. This is a live validation demonstration, separate from the locked changed-input exercise. All four checks pass. The known-answer and fee fixtures challenge numerical logic, the corruption test checks a failure condition, and the first-month calculation checks the link from returns through costs to holdings. Passing these tests supports the implementation; it does not establish investment profitability.'''),
    ('Running app: show the finished product and conclude',
     'Switch to the running Portfolio Committee Review app in your browser. Scroll to Compare portfolio rules. Set One-way trading cost (basis points) to 10. Show the three-rule results table and scroll slightly to the wealth chart. Change the cost to 25 to show the interface updating, then RETURN IT TO 10 before quoting the numbers below. Keep the table visible for the conclusion. Stop your recorder after the paragraph. This is the app, not START-HERE.html.',
     '''This is the finished Portfolio Committee Review app. It displays the saved research results rather than recalculating the optimizer in the browser. The cost selector switches between precomputed scenarios, updating the comparison and wealth chart. Returning to ten basis points, the optimized portfolio earned twenty-four point eight-five percent cumulatively, compared with seventy point nine-seven percent for equal weight. The four tests I just ran check selected calculations and failure handling; the broader saved validation covers additional cases. The short evaluation period and concentrated four-stock universe remain material limitations. My recommendation is no capital deployment and further paper research only.'''),
]


def main():
    setup = '''VIDEO 2 — ACTUAL REPOSITORY WALKTHROUGH (maximum 5 minutes)
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
   & ..\\..\\.venv\\Scripts\\python.exe -m streamlit run app.py
   Open the Local URL it prints. Leave that server terminal running.
4. Keep this script on a phone, printed page or second display outside your capture.
5. Record the ENTIRE DISPLAY with your mic so switching from VS Code to the browser
   app at section 7 is captured. A VS Code-only window recording will miss the app.
   Close unrelated windows. Do not record this instruction page. No PDF is needed.
6. Start at README.md and follow the seven sections below. Only read SAY THIS aloud.
   Leave time for navigation. Rehearse under 5:00; aim for about 4 minutes.

COMMAND (paste exactly; use the VS Code terminal in the project-2 folder):
'''+COMMAND+'''

If the prompt is in a different folder, first enter:
Set-Location 'C:\\Users\\13177\\FIN43900-Fall2026\\projects\\project-2'

During the recording, run the command again at section 6 so the test is shown live.
This is not a request to repeat the locked exercise or change your prediction.
'''
    blocks = []
    for i, (title, action, say) in enumerate(STEPS, 1):
        blocks.append(f'SECTION {i}: {title}\n\nDO THIS (do not read):\n{action}\n'+
                      (f'\nCOMMAND:\n{COMMAND}\n' if i == 6 else '')+
                      '\nSAY THIS:\n'+say+'\n')
    ending = '''AFTER RECORDING
Play the file once: check audible voice, readable code and terminal, actual successful
test output, visible running app, and duration no longer than 5:00. Save as Video 2.
The final transcript must match your actual recording, not simply copy this draft.
'''
    text = setup+'\n'+'\n'.join(blocks)+'\n'+ending
    (OUT/'VIDEO-2-READ-ALOUD.txt').write_text(text, encoding='utf-8-sig')
    (ROOT/'docs/video-2-script.md').write_text(text, encoding='utf-8')
    (ROOT/'docs/video-2-instructions.md').write_text(setup+ending, encoding='utf-8')
    cards = ''.join(f'<section><h2>{i}. {html.escape(title)}</h2><div class="action"><strong>SHOW / DO:</strong> {html.escape(action)}</div>'+
                    (f'<pre>{html.escape(COMMAND)}</pre>' if i == 6 else '')+
                    '<h3>SAY THIS</h3><p>'+html.escape(say)+'</p></section>'
                    for i,(title,action,say) in enumerate(STEPS,1))
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Video 2 — exact recording instructions</title><style>
body{font:19px/1.55 system-ui,sans-serif;color:#18343e;background:#edf2f4;margin:0}main{max-width:950px;margin:auto;padding:30px}section,.setup{background:white;padding:28px;margin:24px 0;border-radius:10px}h1{font-size:36px}h2{font-size:26px}h3{color:#07777a;font-size:17px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.6 Consolas,monospace}.action{padding:18px;background:#e8f4f3;border-left:4px solid #07777a}.banner{font-weight:700;color:#8b4d26}a{color:#006b75}</style></head><body><main>
<h1>Video 2: code, live test and the finished app</h1><p class="banner">PREPARATION PAGE — record your display showing VS Code, then the running app.</p>
<p>Show three files and a live test in VS Code, then the actual browser app in section 7. No PDFs. Follow the numbered sections in order.</p>
<div class="setup"><pre>'''+html.escape(setup)+'''</pre></div>'''+cards+'<section><pre>'+html.escape(ending)+'</pre></section></main></body></html>'
    (OUT/'VIDEO-2-START-HERE.html').write_text(page, encoding='utf-8')
    words = sum(len(re.findall(r"\b[\w’-]+\b",s[2])) for s in STEPS)
    (ROOT/'evidence/video2-guide-check.json').write_text(json.dumps({
        'sections':len(STEPS),'spoken_words':words,'estimated_seconds_at_125wpm_plus_40_seconds_navigation':round(words/125*60+40),
        'maximum_seconds':300,'test_command_verified':True,
        'note':'Practice and recording still required. Actual transcripts and durations come from the student recording. The four-test live demonstration is separate from the locked exercise.'},indent=2)+'\n')
    print(f'Video 2: {words} spoken words; seven actual-repository sections.')


if __name__ == '__main__':
    main()
