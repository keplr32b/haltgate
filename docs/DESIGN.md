# HaltGate - Design

## Thesis

HaltGate is a reusable GenLayer Intelligent Contract for Autonomous Protocols:

> Emergency halt: mark a target halted when anyone **proves** an active exploit with public HTTPS evidence under multi-validator consensus.

Other contracts read `is_halted(target_id)` and refuse privileged actions. HaltGate does not stop arbitrary bytecode; it provides a consensus-backed halt **flag**.

## Track fit

- Official idea: *Pauses a target contract when anyone proves an active exploit*
- GenLayer-native: live HTTPS fetch + comparative consensus on closed verdict labels

## Adversarial model

| False outcome | Who is hurt |
|---------------|-------------|
| False CONFIRMED | Target/integrators freeze without real exploit |
| False CLEAR | Exploit continues while flag stays open |
| Forced INCONCLUSIVE | Delay without unjustified halt |

Mitigations: host allowlist, empty-fetch cannot CONFIRMED, challenge window with new evidence, comparative equivalence on verdict only.

## Lifecycle

REGISTER (owner) → submit_evidence (anyone) → adjudicate
  → CONFIRMED → halted + challenge window
  → CLEAR / INCONCLUSIVE → not halted

challenge (while open) → new URL → re-verdict (can CLEAR and unhalt)
finalize_halt (after window) → challenge closed
recheck (optional watch_url) → same judgment path
owner_clear_halt → ops recovery only

## Verdicts

CONFIRMED | CLEAR | INCONCLUSIVE

Only CONFIRMED sets is_halted. Note is non-binding for equivalence.

## Integration

if haltgate.view().is_halted(target_id):
    revert

## Non-goals

- Forcing non-integrating contracts
- Multi-sig council as core (challenge is evidence + consensus)
- Global hack radar / unlimited URLs
- Mainnet SLA without audit and real integrators

## Limits

- Studionet demo; challenge window 300s for demo
- Owner controls hosts, registration, and ops clear
- Soft enforce; 1–2 evidence URLs per cycle
- LLM judgment is point-in-time under closed labels

## Live verification

See verification/studionet-e2e.md for addresses and receipts.