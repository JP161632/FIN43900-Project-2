# Optional personal rerun of the preserved case

Your original prediction was supplied before the first run and is unchanged.
The original execution was performed through the assistant. This rerun records
your later independent reproduction without altering that history. Because you
have already seen the outcome, it is not a new unseen prediction exercise and
does not automatically establish recovery of the original course requirement.

1. Read the command now. Then close generative tools, including this conversation
   and generative editor features, before launching the rerun.
2. In PowerShell at the course repository root, run this yourself. Use the
   --tools-closed flag only if that statement is true:

```powershell
.\.venv\Scripts\python.exe projects\project-2\student_rerun.py --run --tools-closed
```

3. The script verifies and extracts the exact original code/data snapshot into a
   temporary directory, reruns it and compares it to the preserved original result.
   It saves evidence/locked-exercise/student-rerun.json without replacing any
   original prediction or execution record.
4. Read the saved summaries. Explain to yourself why the target-change and realized
   volatility results differ. Preserve any error; do not delete evidence to retry
   as though it were an earlier successful attempt.
5. After the closed phase ends, return to the conversation and report what happened.

The assistant verified archive integrity only. It did not launch your student rerun.
A new prediction-first case, if required, must be genuinely new and completed
under the applicable rules; it cannot reuse an outcome you already know.
