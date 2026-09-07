# HaltGate

Evidence-gated **emergency halt** for GenLayer — Autonomous Protocols.

Anyone submits a public HTTPS evidence URL. Validators fetch and reach consensus on a closed verdict (`CONFIRMED` | `CLEAR` | `INCONCLUSIVE`). Only `CONFIRMED` sets `is_halted(target_id)`. Other contracts read that flag and refuse privileged actions.

> Official track idea: *Pauses a target contract when anyone proves an active exploit.*

HaltGate does **not** forcibly stop arbitrary bytecode. It is a consensus-backed halt **flag**; integrators must check `is_halted` (see demo consumers).

## Live Studionet

| Role | Address |
|------|---------|
| HaltGate | [`0xD1dC70c83046f99ae2813D311272Cc8DDEa87740`](https://explorer-studio.genlayer.com/address/0xD1dC70c83046f99ae2813D311272Cc8DDEa87740) |
| Consumer (blocked) | [`0x34973C101915525797a3A850F3C36A771b33A2C9`](https://explorer-studio.genlayer.com/address/0x34973C101915525797a3A850F3C36A771b33A2C9) |
| Consumer (allowed) | [`0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5`](https://explorer-studio.genlayer.com/address/0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5) |

Full receipts: [`verification/studionet-e2e.md`](verification/studionet-e2e.md)

## Proven paths

- **CLEAR** — GenLayer docs evidence → not halted → consumer `act()` succeeds  
- **Host reject** — `example.com` → revert  
- **CONFIRMED** — public incident article (rekt.news) → halted → consumer `act()` reverts  

## Core API (HaltGate)

| Method | Who |
|--------|-----|
| `allow_host` / `register_target` | Owner |
| `submit_evidence` | Anyone |
| `adjudicate` | Anyone (consensus) |
| `is_halted` / `read_case` | Views |

## Integration

```text
halted = HaltGate.is_halted(target_id)
if halted: revert
```

Demo: contracts/example_guarded_vault.py

## Design
See docs/DESIGN.md.

## Limits

- Studionet demo network, not a production SLA
- Owner controls host allowlist and criteria at registration (governance surface)
- Single evidence URL per adjudication cycle in v1
- LLM judgment is point-in-time; labels are closed to reduce wording drift
- Not a legal determination of an exploit
