# HaltGate - Design

## Thesis

HaltGate is a reusable GenLayer Intelligent Contract for Autonomous Protocols:

> Emergency halt: mark a target halted when anyone proves an active exploit with public HTTPS evidence under multi-validator consensus.

Other contracts read `is_halted(target_id)` and refuse privileged actions. HaltGate does not stop arbitrary bytecode; it provides a consensus-backed halt flag.

## Track fit

- Official idea: *Pauses a target contract when anyone proves an active exploit*
- GenLayer-native: live HTTPS fetch + comparative consensus on closed verdict labels

## Adversarial model

| False outcome | Who is hurt |
|---------------|-------------|
| False CONFIRMED | Target/integrators freeze without real exploit |
| False CLEAR | Exploit continues while flag stays open |
| Forced INCONCLUSIVE | Delay without unjustified halt |

Mitigations: host allowlist, empty-fetch cannot CONFIRMED, challenge window with new evidence, comparative equivalence on verdict only. **On challenge, INCONCLUSIVE does not unhalt** (avoids clearing a real halt via empty/failed pages).

## Lifecycle

```text
REGISTER (owner)
  → submit_evidence (anyone)
  → adjudicate
       → CONFIRMED → halted + challenge window open
       → CLEAR / INCONCLUSIVE → not halted

challenge (while open, target already halted)
  → CLEAR → unhalt, window closed
  → INCONCLUSIVE → halt preserved, window stays open
  → CONFIRMED → halt kept, window closed / finalized

finalize_halt (after window) → challenge closed, still halted
recheck (optional watch_url) → same judgment path as adjudicate
owner_clear_halt → ops recovery only (lifts halt)
```

## Verdicts

CONFIRMED | CLEAR | INCONCLUSIVE

- First adjudicate / recheck: only CONFIRMED sets is_halted.

- Challenge: only CLEAR (or owner_clear_halt) lifts is_halted. INCONCLUSIVE preserves halt.

- Note is non-binding for equivalence.

## Integration

```text
if haltgate.view().is_halted(target_id):
    revert
```

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

See verification/studionet-e2e.md for addresses and receipts (v1 baseline + challenge-fix deploy).