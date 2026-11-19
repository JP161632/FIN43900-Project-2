# Personal locked exercise - prepare, close tools, predict, freeze, execute

STATUS UPDATE: The selected 24-month case has now been frozen and executed by the
assistant at the student's request. Preserve the records; do not rerun or overwrite
them. The instructions below document the prepared workflow, not proof that a
student completed an AI-closed execution. See execution-provenance.json and
docs/changed-input-results.md. Student reconciliation remains pending.

This exercise changes the estimation-window length while keeping the same 24
evaluation months and other study conventions fixed. It addresses the project's
material estimation-sensitivity claim. No direction or decision prediction is
provided in the original instructions. The selected case has since been run as
documented in the status update above.

Read these commands first. Then close generative tools before choosing the change,
writing the prediction, freezing and executing the exercise. Disable generative
autocomplete while editing the prediction. Remain within the published closed phase.

## From the course repository root, while tools are closed

1. Open projects/project-2/docs/locked-prediction-input.json in an ordinary editor.
2. Choose an integer new lookback from 12 to 35 monthly returns. The old value is
   36. Do not choose a case whose exact result you have already inspected elsewhere.
3. In your own words, fill all four text fields: predicted output direction,
   finance reasoning, expected decision effect and an accurate authorship/tool-use
   attestation. You may predict unchanged, higher, lower, ambiguous or infeasible
   outcomes if that is genuinely your reasoning. Do not obtain the answer first.
4. Save the JSON with double-quoted strings. Preserve the prediction before running:

```powershell
.\.venv\Scripts\python.exe projects\project-2\locked_exercise.py --freeze projects\project-2\docs\locked-prediction-input.json
```

5. This writes an exclusive-create prediction record and exact code/data ZIP under
   evidence/locked-exercise. Record the printed snapshot hash. No case runs yet.
   Do not edit the model, data, precommit record or archive after freezing.
6. Run the designated exercise, still with generative tools closed:

```powershell
.\.venv\Scripts\python.exe projects\project-2\locked_exercise.py --execute
```

7. Read evidence/locked-exercise/student-reconciliation.md and fill its final three
   fields yourself: actual decision effect, prediction reconciliation, and failure
   diagnosis or why the action did not change. Values in the table are decimals,
   except target movement in percentage points and the infeasibility count.
8. Preserve all files. If a command fails, retain the error and original evidence;
   do not delete the prediction and create a purported earlier successful one.

After the closed phase ends, reopen assistance and report that the exercise is
complete. The record can then be integrated without altering your saved prediction.
The archive and local timestamp support reproducibility; they are not an external
timestamp authority, evidence of attendance, or proof of authorship.
