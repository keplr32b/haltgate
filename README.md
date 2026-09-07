# HaltGate

Evidence-gated **emergency halt** for GenLayer (Autonomous Protocols track).

Anyone submits a public HTTPS evidence URL. Validators fetch the page and reach comparative consensus on a closed verdict (`CONFIRMED` | `CLEAR` | `INCONCLUSIVE`). Only `CONFIRMED` sets `is_halted(target_id)`. Other contracts read that flag and refuse privileged actions. The owner may clear a halt for ops recovery.

> Track idea: *Pauses a target contract when anyone proves an active exploit.*

HaltGate does **not** forcibly stop arbitrary bytecode. It exposes a consensus-backed halt **flag**; integrators must check `is_halted` (see demo consumer).

## Live Studionet

| Role | Address |
|------|---------|
| **HaltGate (canonical v2)** | [`0x67b8AAB3caD42b55eF2Fe7fE72fF33CF8413E27A`](https://explorer-studio.genlayer.com/address/0x67b8AAB3caD42b55eF2Fe7fE72fF33CF8413E27A) |
| Deploy | [`0x2f8496131e3f826c6c197a172fbc6c83f34761bc023c972db8bc1587150d6201`](https://explorer-studio.genlayer.com/tx/0x2f8496131e3f826c6c197a172fbc6c83f34761bc023c972db8bc1587150d6201) |

Proven on v2: CLEAR (docs) · CONFIRMED (rekt.news incident) · `owner_clear_halt` → not halted.

Full receipts: [`verification/studionet-e2e.md`](verification/studionet-e2e.md)

## Core API

| Method | Who |
|--------|-----|
| `allow_host` / `register_target` | Owner |
| `submit_evidence` | Anyone |
| `adjudicate` | Anyone (consensus) |
| `owner_clear_halt` | Owner |
| `is_halted` / `read_case` | Views |

## Integration

```text
if HaltGate.is_halted(target_id):
    revert
```

Demo: contracts/example_guarded_vault.py

## Design
See docs/DESIGN.md.

## Limits

- Studionet demo network, not a production SLA
- Owner controls host allowlist and registration criteria (governance surface)
- Owner may clear a CONFIRMED halt (owner_clear_halt); this is ops recovery, not a second AI appeal
- Single evidence URL per adjudication cycle in v1
- LLM judgment is point-in-time; closed verdict labels reduce wording drift
- Not a legal determination of an exploit
