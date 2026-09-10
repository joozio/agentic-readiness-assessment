# Reversible feedback-loop probe

Use primary verification on the traced change path. A documentation typo does not
prove application behavior tests detect a defect.

1. Record the baseline check result. Choose one covered behavior.
2. Preserve exact original bytes; prefer a disposable copy of the assessed revision.
   Never edit code consumed by a live service or another worker.
   Before executing in the copy, confirm the intended cwd, source/check files and
   their baseline hashes. A failed or incomplete copy must stop execution: test
   discovery in an empty directory can import an unrelated installed package.
   Use explicit source paths and fail-fast setup rather than unchecked shell chains.
3. Introduce one small defect: reverse a boundary, alter a return value, omit a
   schema field or violate a policy. Never plant real secrets.
4. Run the existing relevant check. Record detection and whether file/line/message
   locates the defect. If nothing fails, confirm the mutation changes a required
   observable outcome and the check exercises the edited source/artifact. An
   equivalent mutation or wrong import/build path is an invalid probe, not a gap.
   A relevant exercised defect left green is a gap; do not keep mutating until red.
5. In a cleanup/finally path, restore only the exact edited bytes. Re-run the same
   check and compare against baseline. Never bulk-reset or clean a tree.

Avoid stale compiled results when an edit is reversed quickly. For Python, a clean
disposable source copy and bytecode writing disabled before baseline/probe execution
avoid same-size, same-timestamp cache confusion. Other build systems may need their
documented rebuild command. Clean only audit-created caches; preserve existing ones.
Cache effects caused solely by your probe are audit limitations, not repo findings.

Passed requires attributable detection and baseline restoration. If baseline was
failing, distinguish a new failure from the old one. An existing failure is usable
when a temporary repair makes its check pass and restoration recovers the original
failure; Primary checks still has a Gap. Do not describe that baseline as green.
State the fault shape and task this probe supports; one detected defect does not
prove general suite quality or support unrelated components.

Unavailable mutation/execution/restoration means Unverified. Do not use an unrelated
metadata check to claim a successful behavior probe. If cleanup fails, disclose the
exact remaining edit immediately and prioritize restoration over report polish.
