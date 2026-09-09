# HaltGate

Evidence-gated **emergency halt** for GenLayer (Autonomous Protocols track).

Anyone submits public HTTPS evidence (one or two URLs). Validators fetch the pages and reach comparative consensus on a closed verdict: `CONFIRMED` | `CLEAR` | `INCONCLUSIVE`. Only `CONFIRMED` sets `is_halted(target_id)`. While a challenge window is open, anyone may submit challenge evidence and re-adjudicate; `CLEAR` lifts the halt. Integrator contracts read `is_halted` and refuse privileged actions.

> Track idea: *Pauses a target contract when anyone proves an active exploit.*

HaltGate does **not** forcibly stop arbitrary bytecode. It exposes a consensus-backed halt **flag**; integrators must check `is_halted`.

## Live Studionet

| Role | Address |
|------|---------|
| HaltGate | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |

| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |

Proven on-chain:

- CLEAR on `https://docs.genlayer.com` → not halted
- CONFIRMED on `https://rekt.news/kiichain-rekt` → halted, challenge open
- Challenge with docs evidence → CLEAR → halt lifted

Full receipts: [`verification/studionet-e2e.md`](verification/studionet-e2e.md)

## Core API

| Method | Who |
|--------|-----|
| `allow_host` / `register_target` | Owner |
| `submit_evidence` (1–2 URLs) | Anyone |
| `adjudicate` | Anyone (consensus) |
| `challenge` | Anyone while challenge open |
| `finalize_halt` | Anyone after challenge window |
| `recheck` | Anyone if `watch_url` set |
| `owner_clear_halt` | Owner (ops recovery) |
| `is_halted` / `read_case` | Views |

## Integration

```text
if HaltGate.is_halted(target_id):
    revert
```

Demo consumer pattern: contracts/example_guarded_vault.py

## Design

docs/DESIGN.md

## Limits

- Studionet development network, not a production SLA
- Owner controls host allowlist and registration criteria
- Challenge window uses transaction-pinned time (time.time); demo window 300 seconds
- Owner may clear a halt (ops recovery, not a second AI appeal)
- One or two evidence URLs per cycle; not a global hack radar
- Does not forcibly stop arbitrary non-integrating contracts
- LLM judgment is point-in-time under closed verdict labels
