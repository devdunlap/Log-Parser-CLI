# How this project was built with Claude Code

FDE postings ask for AI-assisted engineering. This file is the honest
record of it for this repo: spec-first, with a human reviewing and
owning the result. Updated as the work happens, not reconstructed later.

## Method

- A written spec came first (`log-parser-cli-spec.md`, Nov 21, 2026):
  behavior, repo structure, edge cases, checkpoint - before code.
- Work proceeds milestone by milestone; tests define "done" for each
  parser before it is written.

## Scaffold disclosure (Nov 22, 2026)

The repo scaffold was generated with Muse at my request so the first
build session starts with building, not setup. It contains: the repo
structure, packaging (pyproject), the CLI argument plumbing, the output
writers, the shared record shape, synthetic sample logs, the CI
workflow, and test files written as executable specs.

**The four parsers and the dedupe logic are mine to write.** The logback
tests in `tests/test_parsers.py` fail until `parse_logback` is
implemented - making them pass is Weekend 1.

## Delegated / reviewed / changed

<!-- Per milestone, a few lines each. Examples of what belongs here:
     "Asked Claude Code to draft the syslog regex; it missed the
     space-padded day - caught by the Nov 3 sample line, fixed by hand."
     If nothing went wrong, say what you verified instead. -->

- Weekend 1:
- Week 1 evenings:
- Weekend 2:

## Where the model got things wrong

<!-- The checkpoint requires at least one real entry here before this
     project is called done. -->

- (to be filled in during the build)
