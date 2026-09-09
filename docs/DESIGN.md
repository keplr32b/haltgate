# HaltGate - Studionet E2E

## Canonical HaltGate

| Item | Value |
|------|--------|
| Contract | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |
| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |

Features: dual-source evidence (1–2 URLs) · challenge window · watch + `recheck` · `owner_clear_halt` · verdicts CONFIRMED / CLEAR / INCONCLUSIVE

## Smoke matrix

| Step | Result |
|------|--------|
| allow_host `docs.genlayer.com` + `rekt.news` | ok |
| `vault-1` + https://docs.genlayer.com → adjudicate | **CLEAR** · is_halted false |
| `exploit-1` + https://rekt.news/kiichain-rekt → adjudicate | **CONFIRMED** · is_halted true · challenge open |
| challenge `exploit-1` with https://docs.genlayer.com | **CLEAR** · is_halted **false** |

## Design checks

- Comparative consensus on verdict label only (note non-binding)
- Fail-closed host allowlist; empty fetch must not CONFIRMED
- Challenge = new evidence + consensus (not multi-sig)
- Owner clear = ops recovery only
- Integrators gate on `is_halted(target_id)`
- Anyone may submit evidence; halt only after CONFIRMED consensus
