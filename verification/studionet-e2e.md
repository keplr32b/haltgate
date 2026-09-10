# HaltGate - Studionet E2E

## Canonical HaltGate

| Item | Value |
|------|--------|
| Contract | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |
| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |

Features: dual-source evidence · challenge window · watch + `recheck` · `owner_clear_halt` · verdicts CONFIRMED / CLEAR / INCONCLUSIVE

## Smoke matrix (HaltGate)

| Step | Result |
|------|--------|
| allow_host `docs.genlayer.com` + `rekt.news` | ok |
| `vault-1` + https://docs.genlayer.com → adjudicate | **CLEAR** · is_halted false |
| `exploit-1` + https://rekt.news/kiichain-rekt → adjudicate | **CONFIRMED** · is_halted true · challenge open |
| challenge `exploit-1` with https://docs.genlayer.com | **CLEAR** · is_halted **false** |
| `exploit-freeze-1` + rekt → adjudicate | **CONFIRMED** · is_halted true |

## Integrator consumers (ExampleGuardedVault)

Cross-contract read: `hg.view().is_halted(target_id)`.

| Role | Address | target_id | Outcome |
|------|---------|-----------|---------|
| CLEAR consumer | [`0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927`](https://explorer-studio.genlayer.com/address/0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927) | `vault-1` | status ACTIVE · act ok · withdraw ok |
| Deploy | [`0xfaecaddf27a8b5444bf56ec34b53800047d12ed9149a2ac0562eb03d2885bda6`](https://explorer-studio.genlayer.com/tx/0xfaecaddf27a8b5444bf56ec34b53800047d12ed9149a2ac0562eb03d2885bda6) | | |
| FROZEN consumer | [`0x49820207488BCF7D2cC50F0D47dee49523da6716`](https://explorer-studio.genlayer.com/address/0x49820207488BCF7D2cC50F0D47dee49523da6716) | `exploit-freeze-1` | status FROZEN · act/withdraw ERROR `target halted by HaltGate` |
| Deploy | [`0x48041810a5e5722c6ad0b0a34b2ee5705b0163f25f481f6ac1b0aca728da6be6`](https://explorer-studio.genlayer.com/tx/0x48041810a5e5722c6ad0b0a34b2ee5705b0163f25f481f6ac1b0aca728da6be6) | | |
| act blocked | [`0x4bad1a306a1d8947cee48d16a6dcacaddc6d684df12b828ccd3f884af9ea6d72`](https://explorer-studio.genlayer.com/tx/0x4bad1a306a1d8947cee48d16a6dcacaddc6d684df12b828ccd3f884af9ea6d72) | | |
| withdraw blocked | [`0x72c7e8dfac28381fe541d5a852952cfaede41634ef63c926089f730976d36a34`](https://explorer-studio.genlayer.com/tx/0x72c7e8dfac28381fe541d5a852952cfaede41634ef63c926089f730976d36a34) | | |

## Design checks

- Comparative consensus on verdict label only (note non-binding)
- Fail-closed host allowlist; empty fetch must not CONFIRMED
- Challenge = new evidence + consensus (not multi-sig)
- Owner clear = ops recovery only
- Integrators gate on `is_halted(target_id)` via `view()`
- Anyone may submit evidence; halt only after CONFIRMED consensus