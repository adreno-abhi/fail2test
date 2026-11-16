# Windows HTTP rejection connection close

16 November 2026. Follow-up to merged PR1 CI run
[43846144604](https://github.com/adreno-abhi/fail2test/actions/runs/43846144604),
Windows/Python 3.14 job 133226686226. The Host-rejection test raised WinError 10053
in `HTTPConnection.getresponse` before it could inspect the intended 403 response.
Both updated Actions completed successfully; the aggregate correctly failed and
Pages was skipped. The remaining five matrix jobs and quality job passed.

## Diagnosis

A focused local client sends invalid Host headers, waits 10 ms, then sends the body.
Before the fix, all 30 attempts failed with the same Windows connection abort.
The committed regression covers Host, Origin and session-token rejection; all three
cases also failed on the original code. This separates the transport symptom from
application execution or dependency installation.

The early HTTP rejection closes before a separately sent request body arrives.
Windows can reset the TCP connection when incoming data races that close, preventing
the client from reading the rejection. Bounded graceful close removes the failure in
the same probe without changing validation or response content. No retries or relaxed
assertions are used.

## Change and boundaries

LocalServer half-closes the response side after the handler completes, then discards
incoming bytes for at most 100 ms and 64 KiB before final socket close. Data is never
parsed or passed to the workspace. A monotonic total deadline prevents a trickling
client from extending the drain indefinitely. Socket errors still end cleanup.
The existing per-connection input timeout, request-size bound, Host/Origin/token
checks and response security headers remain intact.

This is a bounded best-effort graceful close, not a guarantee that an arbitrary slow
or oversized upload receives a response. Once either drain limit is reached the
connection closes. Existing loopback-only, single-owner deployment scope remains.

## Local validation

- Windows/Python 3.13.5: new delayed-body regressions red before the fix; all 30
  HTTP-server tests pass after it, including existing adversarial boundaries.
- Windows/Python 3.14.3: all 30 HTTP-server tests pass; original 30-attempt probe
  passes without retries. CI used Python 3.14.10, so hosted verification is pending.
- Idle-peer test confirms cleanup returns without the client completing its body.
- Ruff, changed-file formatting and mypy (20 source files) pass.
- Full local suite intentionally not run; final PR CI should provide the full gate.

Ignored probes and captured local outputs are under this review worktree's
`local-artifacts/`. No instrumentation or throwaway probes belong in the commit.
Future early-rejection tests should include headers/body sent separately, so a normal
small localhost write does not hide transport-close races.

The targeted Chromium failure-to-fixed-pytest-export workflow also passed on Windows/Python 3.13.5 (1 passed, 9 deselected).
