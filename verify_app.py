"""Exercise the actual Streamlit page against frozen output offline."""
import json
import tempfile
import shutil
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent
results = []
app = AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
assert not app.exception, list(app.exception)
results.append('Initial page executes without exceptions')
assert 'paper research' in app.warning[0].value.lower()
results.append('Committee action displayed')
assert len(app.dataframe) >= 2
assert '24.85%' in app.dataframe[0].value.to_string()
results.append('Default candidate net cumulative return reconciles to frozen output')
app.selectbox[0].select(50).run(timeout=30)
assert not app.exception
assert '23.59%' in app.dataframe[0].value.to_string()
results.append('Cost selection renders the 50-bps computed scenario')
assert len(app.json) >= 2
results.append('Concentration and uncertainty evidence rendered')
assert any(element.value=='Model-risk review' for element in app.header)
assert any(element.value=='Edition A - retrospective baseline' for element in app.subheader)
results.append('Model-risk review section rendered')
assert any('36 months' in frame.value.to_string() and '27.83%' in frame.value.to_string() for frame in app.dataframe)
results.append('Preserved changed-input comparison reconciles with original execution')
assert any(element.label=='Quarterly target-change breaches' and element.value=='1' for element in app.metric)
assert any(element.label=='Trailing-volatility breach months' and element.value=='9' for element in app.metric)
results.append('Diagnostic monitoring counts displayed correctly')
with tempfile.TemporaryDirectory() as temporary:
    target=Path(temporary)
    shutil.copy2(ROOT/'app.py',target/'app.py')
    missing=AppTest.from_file(str(target/'app.py')).run(timeout=30)
    assert not missing.exception and missing.error
    assert 'Run python analysis.py first' in missing.error[0].value
    results.append('Missing output gives an actionable error without a page crash')
    (target/'outputs').mkdir()
    (target/'outputs/visible_output.json').write_text('{bad-json')
    malformed=AppTest.from_file(str(target/'app.py')).run(timeout=30)
    assert not malformed.exception and malformed.error
    results.append('Malformed output gives a controlled error without fabricated results')
(ROOT/'evidence/app-verification.json').write_text(json.dumps({'passed': True, 'checks': results}, indent=2)+'\n')
print(f'{len(results)} interface checks passed.')
