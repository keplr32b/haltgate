# HaltGate - Studionet E2E

## Canonical HaltGate

| Item | Value |
|------|--------|
| Contract | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |
| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |

Features: dual-source evidence (1–2 URLs) · challenge window (`time.time` deadline) · watch + `recheck` · `owner_clear_halt` · closed verdicts CONFIRMED / CLEAR / INCONCLUSIVE

## Smoke matrix (live)

| Step | Result |
|------|--------|
| allow_host `docs.genlayer.com` + `rekt.news` | ok |
| `vault-1` + https://docs.genlayer.com → adjudicate | **CLEAR** · is_halted false |
| `exploit-1` + https://rekt.news/kiichain-rekt → adjudicate | **CONFIRMED** · is_halted true · challenge open |
| challenge `exploit-1` with https://docs.genlayer.com | **CLEAR** · is_halted **false** (halt lifted) |

## Earlier integration demos (prior HaltGate instance)

Same consumer pattern: `is_halted` gates `act()`.

| Role | Address |
|------|---------|
| Prior HaltGate | [`0xD1dC70c83046f99ae2813D311272Cc8DDEa87740`](https://explorer-studio.genlayer.com/address/0xD1dC70c83046f99ae2813D311272Cc8DDEa87740) |
| Consumer blocked | [`0x34973C101915525797a3A850F3C36A771b33A2C9`](https://explorer-studio.genlayer.com/address/0x34973C101915525797a3A850F3C36A771b33A2C9) |
| Consumer allowed | [`0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5`](https://explorer-studio.genlayer.com/address/0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5) |

| Case | Outcome |
|------|---------|
| Host reject example.com | ERROR host not allowed |
| act() when halted | ERROR target halted by HaltGate |
| act() when clear | SUCCESS ok |

## Design checks

- Comparative consensus on verdict label only (note non-binding)
- Fail-closed host allowlist; empty fetch must not CONFIRMED
- Challenge is evidence + consensus, not multi-sig vote
- Owner clear is last-resort ops recovery
- Integrators must opt in via `is_halted`