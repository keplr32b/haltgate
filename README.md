# HaltGate

Evidence-gated emergency halt for GenLayer (Autonomous Protocols track).

Anyone submits public HTTPS evidence (one or two URLs). Validators fetch the pages and reach comparative consensus on a closed verdict: CONFIRMED | CLEAR | INCONCLUSIVE. Only CONFIRMED sets `is_halted(target_id)`. While a challenge window is open, anyone may submit challenge evidence; **only CLEAR** (or `owner_clear_halt`) lifts the halt. **INCONCLUSIVE on challenge preserves the halt.** Integrator contracts read `is_halted` and refuse privileged actions.

Track idea: *Pauses a target contract when anyone proves an active exploit.*

HaltGate does not forcibly stop arbitrary bytecode. It exposes a consensus-backed halt flag; integrators must check `is_halted`.

## Live Studionet

### v1 baseline

| Role | Address |
|------|---------|
| HaltGate | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |
| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |
| Consumer CLEAR (vault-1) | [`0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927`](https://explorer-studio.genlayer.com/address/0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927) |
| Consumer FROZEN (exploit-freeze-1) | [`0x49820207488BCF7D2cC50F0D47dee49523da6716`](https://explorer-studio.genlayer.com/address/0x49820207488BCF7D2cC50F0D47dee49523da6716) |

### Challenge-fix deploy (resubmit)

| Role | Address |
|------|---------|
| HaltGate (fixed challenge) | [`0x6dBE2C6Cb3590e48C7aF1E3c17462Cd664a9f63F`](https://explorer-studio.genlayer.com/address/0x6dBE2C6Cb3590e48C7aF1E3c17462Cd664a9f63F) |
| Deploy | [`0xf789b615325418ffecea9f5b637d76e9e6babfe91a9f360c09e227129a216340`](https://explorer-studio.genlayer.com/tx/0xf789b615325418ffecea9f5b637d76e9e6babfe91a9f360c09e227129a216340) |

**Proven on-chain:**

- CLEAR on https://docs.genlayer.com → not halted → consumer ACTIVE, act/withdraw ok
- CONFIRMED on https://rekt.news/kiichain-rekt → halted → consumer FROZEN, act/withdraw blocked
- Challenge with docs → CLEAR → halt lifted
- Challenge with unusable/404 evidence → **INCONCLUSIVE → halt preserved**

Full receipts: [verification/studionet-e2e.md](verification/studionet-e2e.md)

## Core API

| Method | Who |
|--------|-----|
| allow_host / register_target | Owner |
| submit_evidence (1–2 URLs) | Anyone |
| adjudicate | Anyone (consensus) |
| challenge | Anyone while challenge open |
| finalize_halt | Anyone after challenge window |
| recheck | Anyone if watch_url set |
| owner_clear_halt | Owner (ops recovery) |
| is_halted / read_case | Views |

**Challenge rule:** only CLEAR or `owner_clear_halt` lifts a halt. INCONCLUSIVE on challenge preserves `is_halted` (challenge window stays coherent until CLEAR, CONFIRMED-finalize, or window end + `finalize_halt`).

## Integration

```python
hg = gl.get_contract_at(haltgate_addr)
if hg.view().is_halted(target_id):
    revert  # FROZEN
```

Demo: contracts/example_guarded_vault.py (act + withdraw both gated).

## Design

docs/design.md

## Who uses this

Vaults, agents, and protocols that opt in: before withdraw/act, call is_halted(target_id). HaltGate is a shared consensus signal, not a chain-wide kill switch.

Production note: treat owner as deployment governance; prefer multi-sig/timelock on owner_clear_halt and longer challenge windows off Studionet.

## Limits

- Studionet development network, not a production SLA
- Owner controls host allowlist and registration criteria
- Challenge window uses transaction-pinned time (time.time); demo window 300 seconds
- Owner may clear a halt (ops recovery, not a second AI appeal)
- One or two evidence URLs per cycle; not a global hack radar
- Does not forcibly stop arbitrary non-integrating contracts
- LLM judgment is point-in-time under closed verdict labels