# Fresh 30-month prediction received - before execution

LATER STATUS: The student has now frozen and executed the 30-month case and completed the reconciliation. Saved hashes and arithmetic are verified in evidence/fresh-execution-verification.json. This document retains the original pre-run receipt/instructions; no repeat run is needed.

The student supplied the prediction and affirmed independent authorship with generative tools closed. The assistant transcribed the four answers without substantive changes into `fresh-prediction-input.json` and retained the supplied text in `fresh-prediction-original.txt`. The authorship/tool-state statement is self-attested, not independently observed.

The earlier frozen review report described this form as blank. That description records its earlier preparation state; it is superseded by this dated receipt for the prediction's current status. The 30-month case remains unexecuted. No feedback on the prediction's accuracy or reasoning has been supplied before the student's run.

The input changes from 36 to 30 monthly returns. The student references the previously seen 24-month result in their explanation; that history is preserved rather than relabeled as unseen evidence. No result for the new 30-month case is supplied here.

## Next action - student with generative tools closed

The JSON is already filled. Do not edit the prediction after seeing any result. At the original course repository root, run these commands yourself, one at a time, only while generative tools are closed:

```powershell
.\.venv\Scripts\python.exe projects\project-2\fresh_locked_exercise.py --freeze projects\project-2\docs\fresh-prediction-input.json --tools-closed
.\.venv\Scripts\python.exe projects\project-2\fresh_locked_exercise.py --execute --tools-closed
```

The first command preserves your prediction and a code/data snapshot without executing the case. The second preserves actual results in `evidence/fresh-locked-exercise/execution.json` and creates `student-reconciliation.md` in the same folder. Complete the reconciliation yourself while generative tools remain closed: actual values/units, agreement or disagreement, actual decision effect and an evidence-supported explanation. Preserve any failure. Do not overwrite an existing freeze or execution.

After the closed phase ends, supply the actual result and your reconciliation for checking and incorporation into refreshed reports and a new final submission snapshot. The original 24-month records remain unchanged.
