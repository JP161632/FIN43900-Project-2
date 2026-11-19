"""Build an offline recording guide: exact evidence screens and matching narration."""
import hashlib
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'recording'


def pct(value):return f'{value:.2%}'
def esc(value):return html.escape(str(value))
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def check_hashes(document):
    for name,digest in document.get('file_hashes',{}).items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Stale evidence: '+name)


def table(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'


def points(items):return '<ul>'+''.join('<li>'+esc(item)+'</li>' for item in items)+'</ul>'
def metrics(items):return '<div class="metrics">'+''.join('<div><strong>'+esc(value)+'</strong><span>'+esc(label)+'</span></div>' for value,label in items)+'</div>'
def note(text):return '<p class="note">'+esc(text)+'</p>'
def source_code(path,start,end):
    lines=(ROOT/path).read_text(encoding='utf-8-sig').splitlines()
    while end>start and not lines[end-1].strip():end-=1
    content='\n'.join(f'{i:>3}  {lines[i-1]}' for i in range(start,end+1))
    return '<div class="code-label">'+esc(f'{path} · actual source, lines {start}–{end}')+'</div><pre>'+esc(content)+'</pre>'


def main():
    out=read('outputs/visible_output.json');review=read('outputs/review_evidence.json')
    check_hashes(out);check_hashes(review)
    baseline=read('baseline/prior-portfolio-snapshot/personal-results.json')
    tests=read('evidence/verification-results.json');supp=read('evidence/review-verification.json')
    ui=read('evidence/app-verification.json');clean=read('evidence/clean-install.json')
    locked=read('evidence/locked-exercise/execution.json')
    if not all(item['passed'] for item in [tests,supp,ui,clean]):raise ValueError('Evidence checks must pass.')
    before=locked['before']['summary'];after=locked['after']['summary']
    sums={rule:out['replays'][rule+'_10bps']['summary'] for rule in ['equal','inverse_vol','candidate']}
    names={'equal':'Equal weight','inverse_vol':'Inverse volatility','candidate':'Optimized portfolio'}
    compare=table(['Rule','Net cumulative return','Annualized net volatility','Max. month-end drawdown'],[
        [names[rule],pct(item['net_total_return']),pct(item['net_volatility']),pct(item['max_drawdown_month_end'])]
        for rule,item in sums.items()])
    comparison_note='October 2024–September 2026 · 24 replay months · 10 bps one-way cost · initial purchase included'
    original=baseline['runs']['all_months']
    v1=[];v2=[];v3=[]
    def add(target,title,seconds,body,say,source,point):
        number=len(target)+1
        target.append({'screen':number,'title':title,'seconds':seconds,'html':body,
                       'say':say.strip(),'source':source,'point':point})

    add(v1,'Edition A: my starting position',40,
        '<p class="lead">A provisional pilot, with important conditions.</p>'+metrics([
            ('0 / 70 / 25 / 5','NVDA / MSFT / TSM / QCOM weights, percent'),
            (pct(original['volatility']),'Estimated annual volatility')])+points([
            '36-versus-60-month estimates changed an asset weight by 20 percentage points.',
            'A one-point TSM mean cut did not change the chosen weights.',
            'The starting position required forward evidence and monitoring.'])+
        note('Edition A is the selected retrospective baseline. These are historical estimates, not realized strategy returns or a checkpoint receipt.'),
        '''This project asks whether an optimized portfolio of NVIDIA, Microsoft, TSM and Qualcomm is ready for investment use. I use my earlier portfolio results as a retrospective Edition A baseline. The starting allocation was mostly Microsoft and TSM, and the position was a provisional pilot with monitoring. But there was already a warning: changing the estimation window moved one asset's weight by twenty percentage points. The apparently stable TSM stress did not resolve that concern.''',
        'Preserved Edition A: baseline/prior-portfolio-snapshot/personal-results.json and original writeup',
        'Point at the weights, then the 20-percentage-point warning. Stay on this screen for the whole paragraph.')
    add(v1,'Edition B changed the recommendation',45,
        '<p class="lead">Compare the process with simple alternatives.</p>'+compare+
        note(comparison_note),
        '''Edition B adds a rolling comparison with equal weight and inverse volatility, using the same stocks, evaluation months and trading-cost assumptions. This table changed my recommendation. The optimized portfolio returned twenty-four point eight-five percent cumulatively, while equal weight returned seventy point nine-seven percent. The optimized portfolio also had higher realized volatility and a larger drawdown. I therefore moved from a provisional pilot position to no capital deployment and further paper research only.''',
        'outputs/visible_output.json → replays → each rule at 10 bps',
        'Point to optimized versus equal-weight return, then their volatility columns. These returns are cumulative, not annual.')
    add(v1,'More checks strengthened that decision',40,
        table(['Net cumulative return','First 12 months','Last 12 months'],[
            ['Optimized portfolio',pct(review['subperiods']['candidate']['first_12']['net_total_return']),pct(review['subperiods']['candidate']['last_12']['net_total_return'])],
            ['Equal weight',pct(review['subperiods']['equal']['first_12']['net_total_return']),pct(review['subperiods']['equal']['last_12']['net_total_return'])]])+
        metrics([('1','Target-change limit breach'),('9','Trailing-volatility breach months')])+
        note('Post-result diagnostics. No strategy or threshold was retuned. The replay did not stop at the flags.'),
        '''I also checked whether the conclusion depended on one part of the sample. The optimized portfolio trails equal weight in both twelve-month segments. Applying the accepted monitoring limits flags one excessive target change and nine trailing-volatility months. These are diagnostic results; they do not mean a live kill rule was executed. I kept the failures visible instead of changing the thresholds to make the strategy pass.''',
        'outputs/review_evidence.json → subperiods and monitoring',
        'Show both table rows, then point to the two monitoring counts. No scrolling or app switching is needed.')
    change_table=table(['Metric','36-month window','24-month window'],[
        ['Annualized realized net volatility',pct(before['net_volatility']),pct(after['net_volatility'])],
        ['Largest quarterly target change',f"{before['max_target_change_points']:.0f} percentage points",f"{after['max_target_change_points']:.0f} percentage points"],
        ['Net cumulative return',pct(before['net_total_return']),pct(after['net_total_return'])]])
    add(v1,'My prediction was only partly supported',35,
        '<p class="lead">I predicted higher volatility and larger target changes.</p>'+change_table+
        note('The original prediction was preserved. Larger target changes and more volatile realized returns are different measures.'),
        '''My changed-input prediction was only partly supported. Shortening the window to twenty-four months increased the largest quarterly target change from twenty to twenty-five percentage points. But realized net volatility fell from twenty-nine point six-one to twenty-seven point eight-three percent, so my volatility prediction was wrong. This taught me to separate allocation instability from realized risk. The result does not establish a durable improvement, and my recommendation remains unchanged.''',
        'evidence/locked-exercise/precommit.json and execution.json; corrected student reflection',
        'Point to the first two rows. Finish the paragraph, then stop the screen recorder. Video 1 is finished.')

    flow='<div class="flow"><div>Saved daily sources<small>Original responses + hashes</small></div><b>→</b><div>Monthly inputs<small>Aligned adjusted prices</small></div><b>→</b><div>Analysis engine<small>Weights, trades, costs</small></div><b>→</b><div>Frozen results<small>App + reports</small></div></div>'
    add(v2,'How the submitted application works',35,
        flow+metrics([('4','Stocks'),('61','Monthly prices per stock'),('244','Prices reconstructed')])+
        points(['Source: archived Yahoo Finance responses, downloaded October 22, 2026.',
                'Missing or invalid prices are rejected; no missing months are filled.'])+
        note('Price observations end September 2026. Downloaded adjustment factors are not historical vintages.'),
        '''The application has four stages. Saved daily source responses produce the monthly inputs. The analysis engine computes allocations, trades and costs. It exports frozen results, which the app and reports display. Each source retains its URL, retrieval time and hash. The audit reconstructed all two hundred forty-four monthly prices. It rejects missing months and invalid prices rather than filling them. These adjustment factors come from the archived download, so they do not establish historical point-in-time availability.''',
        'analysis.py: audit_sources; data/price-provenance.json; outputs/review_evidence.json',
        'Move your pointer across the four flow boxes, then the 244 count. This is an overview of the actual submitted data flow.')
    add(v2,'The optimizer and rolling window',50,
        source_code('analysis.py',145,148)+source_code('analysis.py',104,111)+
        note('Long-only · Fully invested · Five-percentage-point grid · 10% historical-mean hurdle · Quarterly targets'),
        '''These are excerpts from the actual analysis file. The first excerpt selects only returns before the evaluation month and identifies quarterly rebalance dates. The optimizer then checks candidate allocations against the bounds and historical-mean hurdle, calculates volatility and keeps a lower-risk feasible mix. That is minimum estimated risk under this model, not guaranteed future risk. The ten percent hurdle is a historical filter, not a promised return. Between target trades, holdings drift with market returns.''',
        'Actual source excerpts: analysis.py; generated directly from the submitted file',
        'Point at training = returns.iloc[...] first. Then point at the feasibility checks and lower-volatility selection. Do not read code line by line.')
    add(v2,'Costs are paid from portfolio capital',40,
        '<p class="lead">Charge each dollar bought or sold, including the first purchase.</p>'+
        source_code('analysis.py',128,137)+
        note('Independent fixtures check initial deployment and a full position switch. Actual fills, taxes and market impact are not established.'),
        '''Trading costs apply to purchases and sales, including initial deployment. This code solves the fee from portfolio capital rather than assuming borrowed money pays it. The amount available for the target allocation therefore depends on the fee itself. Independent arithmetic fixtures check both an initial purchase and a full position switch. This is an explicit cost model, but it does not establish actual fills, market impact or tax costs.''',
        'analysis.py: trade_cost; tests.py: test_trade_fee_independent_exact_answers',
        'Point at the iterative fee calculation, then its returned cost and traded amount. The screen contains real saved source, not a live code run.')
    add(v2,'The changed-input record',50,
        '<p class="lead">Prediction: higher realized volatility; more aggressive targets; unchanged action.</p>'+change_table+
        note('Original prediction and first execution preserved. A later AI-closed student rerun is self-reported; its generated result file is not available here.'),
        '''Before the first result, I supplied a prediction for changing the lookback from thirty-six to twenty-four months. I expected higher realized volatility, more aggressive target changes and no change in recommendation. The saved result disagrees with the volatility prediction but supports the target-change concern on this metric. I still do not support deployment. I subsequently reported repeating the archived case with generative tools closed and obtaining the same result. The earlier prediction and execution history remain preserved separately.''',
        'evidence/locked-exercise: precommit.json, snapshot.zip, execution.json and student reconciliation',
        'Point to the prediction at the top, then the volatility and target-change rows. Describe the later rerun as your reported activity, not independently verified output.')
    add(v2,'Monitoring is checked explicitly',40,
        metrics([('15 pp','Target-change threshold'),('22%','Trailing annualized net-volatility threshold')])+
        source_code('review_analysis.py',90,90)+source_code('review_analysis.py',93,94)+
        note('Observed: 1 target-change event; 9 volatility months. The first 11 months lack a 12-return window. This diagnostic did not halt the replay.'),
        '''The supplemental review checks the monitoring rules explicitly. The target-change threshold is fifteen percentage points. The volatility measure uses the latest twelve monthly net returns, annualized consistently. The first eleven months cannot produce that measure. The diagnostic flags one target event and nine volatility months. It did not stop the historical replay at those flags. That distinction matters because a diagnostic comparison is not the same as implementing a live risk-control policy.''',
        'review_analysis.py: monitoring; outputs/review_evidence.json: monitoring observations',
        'Point to the thresholds, then the code’s 12-observation condition and breach flags. You do not need another editor window.')
    core_tail='\n'.join(line for line in tests['output'].strip().splitlines()[-4:] if line.strip() and set(line.strip())!={'-'})
    supp_tail='\n'.join(line for line in supp['output'].strip().splitlines()[-4:] if line.strip() and set(line.strip())!={'-'})
    add(v2,'Saved tests and clean-install evidence',45,
        metrics([(str(tests['tests_run']+supp['tests_run']),'Numerical test methods passed'),(str(len(ui['checks'])),'Interface checks passed')])+
        '<div class="testlogs"><div><h3>Core audit — saved output</h3><pre>'+esc(core_tail)+'</pre></div><div><h3>Supplemental audit — saved output</h3><pre>'+esc(supp_tail)+'</pre></div></div>'+
        points(['New environment installed locked dependencies; no broken requirements.',
                'Both material output files reproduced in an isolated project copy.',
                'Tests cover source lineage, covariance, costs, invalid inputs, constraints and monitoring.'])+
        note('Saved execution evidence, not tests running live during this recording. Automated checks do not establish profitability or an unaided human review.'),
        '''This screen shows saved test output, not commands running live. Fourteen core and five supplemental methods passed, along with ten interface checks. They include independent arithmetic, corrupted-input failures, constraint checks and monitoring edge cases. A new environment installed the locked dependencies and reproduced both material output files from an isolated project copy. The initial missing-pip and restricted-network failures and their resolution are recorded. These checks make the technical result reproducible; they do not establish investment profitability or replace a student explanation.''',
        'evidence/verification-results.json, review-verification.json, app-verification.json and clean-install.json',
        'Point to the two test totals and the saved OK outputs. Finish your paragraph, then stop the recorder. Video 2 is finished.')

    add(v3,'Committee decision',40,
        '<div class="decision">Do not deploy capital in the current process.</div>'+
        '<p class="lead">Authorize further paper research only.</p>'+points([
            'User: committee evaluating a thematic research sleeve.',
            'Universe: NVDA, MSFT, TSM and QCOM.',
            'Same-universe equal weight is the primary comparison.',
            'This does not establish a suitable whole-client allocation.']),
        '''My recommendation is not to deploy capital in the current optimized portfolio process. I am asking the committee to authorize further paper research only. The study concerns a four-stock thematic sleeve containing NVIDIA, Microsoft, TSM and Qualcomm. It evaluates whether the optimization process adds value relative to simple allocations. It does not establish a suitable portfolio for a client's entire wealth.''',
        'Decision-Memo.pdf; docs/research-design.md; accepted student decisions',
        'Keep this screen visible for your opening. Point to the recommendation, then the universe. No other file needs to be open.')
    add(v3,'The simple baseline performed better',50,
        compare+note(comparison_note)+
        '<p class="takeaway">The optimized process earned less and realized more volatility in this replay.</p>',
        '''The comparison uses the same four stocks, the same twenty-four evaluation months and the same ten-basis-point one-way cost assumption, including initial purchase. The optimized portfolio returned twenty-four point eight-five percent cumulatively, compared with seventy point nine-seven percent for equal weight. Its annualized net volatility was twenty-nine point six-one percent, versus twenty-seven point seven-nine percent for equal weight. Its month-end maximum drawdown was also larger. These results do not support adoption of the optimizer merely because it minimizes an estimated risk measure.''',
        'outputs/visible_output.json: 10-bps chronological replays',
        'Point to the optimized and equal-weight rows. Move from return to volatility to drawdown while speaking. Do not call cumulative return annual.')
    cap=out['replays']['candidate_cap50_10bps']['summary']
    add(v3,'Concentration and estimation sensitivity',45,
        metrics([('95%','Largest starting position in the original replay'),(pct(cap['max_start_equity_weight']),'Largest starting position in the 50%-target-cap case')])+
        points(['The 50%-target-cap case returned '+pct(cap['net_total_return'])+' net and still trailed equal weight.',
                'A target cap does not control subsequent market drift.',
                'Changing the estimation window can materially change allocations.'])+
        note('Separate research scenarios. None establishes a client-approved continuous concentration policy.'),
        '''The concern is not just lower return. The original candidate reaches a ninety-five percent position at a replay boundary. A separate fifty percent target-cap scenario improves cumulative return to thirty-three point eight-four percent, but still trails equal weight. Its largest starting position later reaches about sixty-one percent because holdings drift between trades. This illustrates why the committee needs an explicit concentration policy and why a historical covariance estimate should not be treated as a stable description of future risk.''',
        'outputs/visible_output.json: candidate_10bps and candidate_cap50_10bps',
        'Point to 95%, then the drifted 61.04% figure. Explain target versus actual holdings; no app expander needs to be found.')
    add(v3,'The limits affect the action',50,
        points(['The candidate trails equal weight in both 12-month segments.',
                'Monitoring diagnostics flag one target event and nine volatility months.',
                'The data was previously inspected; this is not an untouched holdout.',
                'Historical adjustments and idealized execution limit investability claims.',
                'A historical volume proxy does not establish live capacity.'])+
        note('The descriptive uncertainty interval includes zero for the annualized mean-return difference. No prospective superiority is established.'),
        '''Additional checks reinforce caution. The candidate trails equal weight in both twelve-month subperiods, and the monitoring diagnostics show breaches. The data had already been inspected, so this is a chronological replay rather than an untouched holdout. Price adjustments are retrospective and execution is idealized. The descriptive uncertainty interval includes zero for the mean-return difference. The historical volume proxy also cannot establish live capacity. These limits restrict the action; passing code tests does not make the investment case acceptable.''',
        'outputs/review_evidence.json; paired block interval in outputs/visible_output.json',
        'Move down the bullets while explaining their effect on the recommendation. This screen replaces multiple report pages and app sections.')
    add(v3,'Conditions for further research',55,
        '<div class="roles"><div><h3>Research analyst</h3>'+points([
            'Review quarterly.',
            'Quarantine on provenance failure or infeasibility.',
            'Quarantine above 15 pp target movement.',
            'Quarantine above 22% trailing annualized net volatility.'])+'</div><div><h3>Committee</h3>'+points([
            'Require a frozen prospective paper design.',
            'Review a proposed 12 months of evidence.',
            'Require suitable constraints and independent review.',
            'Require credible execution, costs and capacity evidence.'])+'</div></div>'+
        '<p class="takeaway">No live pilot has occurred. Positive paper results would not automatically authorize capital.</p>',
        '''The research analyst should review the paper process quarterly and quarantine it on missing provenance, infeasibility, excessive target movement or trailing-volatility breaches. The accepted thresholds are fifteen percentage points and twenty-two percent, using the defined monitoring windows. The prospective proposal fixes the rules and a later execution buffer before observing new outcomes, with a proposed twelve-month evaluation. No pilot has begun. Reopening capital consideration requires a suitable mandate, independent review and credible implementation evidence. The immediate committee action remains further evidence gathering, not deployment.''',
        'Decision-Memo.pdf; docs/prospective-protocol.md; accepted monitoring assumptions',
        'Point to the analyst responsibilities, then committee conditions. Deliver the final sentence and stop the recorder. Video 3 is finished.')

    videos=[{'number':1,'name':'Research evolution','limit':180,'slides':v1},
            {'number':3,'name':'Committee presentation','limit':300,'slides':v3}]
    OUT.mkdir(exist_ok=True)
    data={'videos':videos,'recordingOrder':[3,1,2]}
    template=(ROOT/'recording_studio_template.html').read_text(encoding='utf-8')
    template=template.replace('function choose(number,screen=1){',
        "function choose(number,screen=1){if(number===2){location.href='VIDEO-2-START-HERE.html';return;}")
    template=template.replace('You do not need to find report pages, code functions or terminal windows while speaking.',
        'Videos 1 and 3 use the evidence screens below. Video 2 opens separate instructions for the actual repository and a live validation test.')
    template=template.replace('6 screens', 'Actual code + live test')
    template=template.replace("$('videoSelect').value='2';$('videoSelect').dispatchEvent(new Event('change'));const selectionWorks=currentVideo===2&&index===0;",
        "$('videoSelect').value='1';$('videoSelect').dispatchEvent(new Event('change'));const selectionWorks=currentVideo===1&&index===0;")
    (OUT/'START-HERE.html').write_text(template.replace('@@DATA@@',json.dumps(data,ensure_ascii=False).replace('<',chr(92)+'u003c')),encoding='utf-8')
    (OUT/'screens-and-scripts.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    summary=[]
    for video in videos:
        text=[f"VIDEO {video['number']}: {video['name'].upper()}",
              'REHEARSAL SCRIPT - not a transcript of a completed recording.',
              f"Maximum duration: {video['limit']//60} minutes.",
              'Open recording/START-HERE.html in a web browser. Select this video.',
              'The white evidence panel is what you record. The narration panel is what you read.',
              'Click Next screen when each paragraph ends. No file switching is required.','']
        words=0
        for slide in video['slides']:
            text += [f"SCREEN {slide['screen']}: {slide['title']}",'',
                     'DO THIS (do not read aloud): '+slide['point'],'',
                     'SAY THIS:',slide['say'],'',
                     'THEN: '+('Stop your screen recorder.' if slide is video['slides'][-1] else 'Click Next screen.'),'','-'*64,'']
            words+=len(re.findall(r"\b[\w’-]+\b",slide['say']))
        body='\n'.join(text)
        (OUT/f'VIDEO-{video["number"]}-READ-ALOUD.txt').write_text(body,encoding='utf-8-sig')
        (ROOT/f'docs/video-{video["number"]}-script.md').write_text(body,encoding='utf-8')
        summary.append({'video':video['number'],'screens':len(video['slides']),'spoken_words':words,
                        'estimated_seconds_at_125wpm_plus_3_seconds_per_change':round(words/125*60+3*(len(video['slides'])-1)),
                        'maximum_seconds':video['limit']})
    (ROOT/'evidence/recording-studio-content-check.json').write_text(json.dumps({
        'source_contracts_verified':True,'scripts':summary,
        'screen_count':sum(len(v['slides']) for v in videos),
        'note':'Timing is an estimate; final durations and transcripts must come from actual recordings.'},indent=2)+'\n')
    guide='''PROJECT 2: EASY RECORDING GUIDE

This replaces the old instructions that sent you between many files.

1. Open START-HERE.html in Edge or Chrome. If it opens in Word, right-click it,
   choose Open with, and choose Microsoft Edge.
2. Select "Start with Video 3". It opens screen 1 with the matching words beside it.
3. Maximize the browser. The WHITE PANEL ON THE LEFT is what the audience should see.
   The panel on the RIGHT is what you read. It is okay to scroll the right panel;
   the white evidence panel stays fixed.
4. In your screen recorder, choose an AREA/REGION covering ONLY the white panel.
   Leave the narration and the top navigation controls outside that rectangle.
5. Enable your microphone. Make and replay a 15-second test before the full video.
6. Start recording. Read the paragraph on the right. Point to the indicated evidence.
7. When the paragraph ends, click NEXT SCREEN at the top. Both panels update together.
   Do not resize the browser or change the recording rectangle between screens.
8. On the last screen, finish the paragraph and STOP YOUR SCREEN RECORDER.
9. Record Video 1 using the same process. Video 2 uses a DIFFERENT process below.

If your recorder cannot capture a region: choose HIDE NARRATION, record the evidence
view, and read the matching VIDEO-N-READ-ALOUD.txt from paper or another device.
Those .txt files are plain text and open in Notepad without a conversion prompt.

WHAT EACH VIDEO NOW CONTAINS
Video 3: five screens for the decision, comparison, concentration, limits and next steps.
Video 1: four screens for Edition A, what changed, extra checks and your reflection.
Video 2: open VIDEO-2-START-HERE.html for the actual repository walkthrough and live test.

Videos 1 and 3 need only this evidence guide. For Video 2, record VS Code showing
README.md, analysis.py, tests.py and a live four-test demonstration in its terminal.
The separate Video 2 page gives every shortcut, the command and the matching words.
Finish Video 2 by showing the running app as directed in its section 7.
Record your entire display so both VS Code and the browser app are captured.
Do not record Video 2 using the white-panel guide. No PDF is needed for it.

TIME LIMITS
Video 1: maximum 3:00. Video 2: maximum 5:00. Video 3: maximum 5:00.
The scripts leave a margin at a normal speaking pace. Rehearse once and check the
actual duration; estimates are not actual recording lengths.

AFTER RECORDING
Save three separate videos and play each once. Confirm audible voice, readable
figures, correct numbers and duration. Keep small natural pauses; correct substantive
errors. Supply the actual video files or reviewable links and any automatic transcripts.
Actual transcripts and timestamp indices must match what you recorded, not this script.

This HTML guide does not make a recording itself. Use your normal screen recorder.
Its evidence is embedded, so no internet connection or Streamlit launch is needed.
'''
    (OUT/'READ-ME-FIRST.txt').write_text(guide,encoding='utf-8-sig')
    (ROOT/'docs/recording-plan.md').write_text(guide,encoding='utf-8')
    (ROOT/'docs/recording-instructions.md').write_text(guide,encoding='utf-8')
    print(json.dumps(summary,indent=2))
    from build_video2_guide import main as build_video2
    build_video2()


if __name__=='__main__':main()
