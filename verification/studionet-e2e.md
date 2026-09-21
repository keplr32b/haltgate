# HaltGate - Studionet E2E

## Canonical HaltGate (v1 baseline)

| Item | Value |
|------|--------|
| Contract | [`0x577EE00131F183C745e9f9a19B306d7845aF9658`](https://explorer-studio.genlayer.com/address/0x577EE00131F183C745e9f9a19B306d7845aF9658) |
| Deploy | [`0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762`](https://explorer-studio.genlayer.com/tx/0xb4133350dd0408e3a8a34de65ef61a8b9bce23039f020471b70285f9ba888762) |

Features: dual-source evidence · challenge window · watch + recheck · owner_clear_halt · verdicts CONFIRMED / CLEAR / INCONCLUSIVE

### Smoke matrix (v1)

| Step | Result |
|------|--------|
| allow_host docs.genlayer.com + rekt.news | ok |
| vault-1 + https://docs.genlayer.com → adjudicate | CLEAR · is_halted false |
| exploit-1 + https://rekt.news/kiichain-rekt → adjudicate | CONFIRMED · is_halted true · challenge open |
| challenge exploit-1 with https://docs.genlayer.com | CLEAR · is_halted false |
| exploit-freeze-1 + rekt → adjudicate | CONFIRMED · is_halted true |

### Integrator consumers (ExampleGuardedVault)

Cross-contract read: `hg.view().is_halted(target_id)`.

| Role | Address | target_id | Outcome |
|------|---------|-----------|---------|
| CLEAR consumer | [`0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927`](https://explorer-studio.genlayer.com/address/0x46CB5F54340Bf5b975330d7611dD0be1Ad7F0927) | vault-1 | status ACTIVE · act ok · withdraw ok |
| Deploy | [`0xfaecaddf27a8b5444bf56ec34b53800047d12ed9149a2ac0562eb03d2885bda6`](https://explorer-studio.genlayer.com/tx/0xfaecaddf27a8b5444bf56ec34b53800047d12ed9149a2ac0562eb03d2885bda6) | | |
| FROZEN consumer | [`0x49820207488BCF7D2cC50F0D47dee49523da6716`](https://explorer-studio.genlayer.com/address/0x49820207488BCF7D2cC50F0D47dee49523da6716) | exploit-freeze-1 | status FROZEN · act/withdraw ERROR target halted by HaltGate |
| Deploy | [`0x48041810a5e5722c6ad0b0a34b2ee5705b0163f25f481f6ac1b0aca728da6be6`](https://explorer-studio.genlayer.com/tx/0x48041810a5e5722c6ad0b0a34b2ee5705b0163f25f481f6ac1b0aca728da6be6) | | |
| act blocked | [`0x4bad1a306a1d8947cee48d16a6dcacaddc6d684df12b828ccd3f884af9ea6d72`](https://explorer-studio.genlayer.com/tx/0x4bad1a306a1d8947cee48d16a6dcacaddc6d684df12b828ccd3f884af9ea6d72) | | |
| withdraw blocked | [`0x72c7e8dfac28381fe541d5a852952cfaede41634ef63c926089f730976d36a34`](https://explorer-studio.genlayer.com/tx/0x72c7e8dfac28381fe541d5a852952cfaede41634ef63c926089f730976d36a34) | | |

---

## Challenge-fix deploy (resubmit)

**Rule:** Only **CLEAR** or **owner_clear_halt** lifts a halt. **INCONCLUSIVE** on challenge preserves `is_halted` and leaves the challenge window coherent. **CONFIRMED** on challenge keeps halt and finalizes the window.

| Item | Value |
|------|--------|
| Contract | [`0x6dBE2C6Cb3590e48C7aF1E3c17462Cd664a9f63F`](https://explorer-studio.genlayer.com/address/0x6dBE2C6Cb3590e48C7aF1E3c17462Cd664a9f63F) |
| Deploy | [`0xf789b615325418ffecea9f5b637d76e9e6babfe91a9f360c09e227129a216340`](https://explorer-studio.genlayer.com/tx/0xf789b615325418ffecea9f5b637d76e9e6babfe91a9f360c09e227129a216340) |

### Smoke matrix (challenge fix)

| Step | Result | Tx |
|------|--------|-----|
| allow_host docs.genlayer.com + rekt.news | ok | `0x94a526e7…` / `0xa6f16d57…` |
| register chal-fix-1 | ok | `0xb4a76334…` |
| submit + adjudicate chal-fix-1 (rekt) | CONFIRMED · is_halted true | [`0x54b8d115d9b346848280f7c4c648fc270a23e3cb6fef0799047c8d75f01083f7`](https://explorer-studio.genlayer.com/tx/0x54b8d115d9b346848280f7c4c648fc270a23e3cb6fef0799047c8d75f01083f7) |
| challenge chal-fix-1 + docs.genlayer.com | CLEAR · is_halted false | [`0xaa3371f1d8388995faaf288b562ddf0d67cf0793cc92206127838131a466c056`](https://explorer-studio.genlayer.com/tx/0xaa3371f1d8388995faaf288b562ddf0d67cf0793cc92206127838131a466c056) |
| register + adjudicate chal-fix-2 (rekt) | CONFIRMED · is_halted true | [`0xcddc2b050594f0f308633e0b7e0990631ff0c4e1953f9fb852b4eb5a4a49b9e6`](https://explorer-studio.genlayer.com/tx/0xcddc2b050594f0f308633e0b7e0990631ff0c4e1953f9fb852b4eb5a4a49b9e6) |
| challenge chal-fix-2 + nonexistent rekt URL | INCONCLUSIVE · is_halted **true** | [`0x9fb08b62e0ed98ce74880a5c22d8fc8adfb6741fa2ae67a0d3543c96b8f534cb`](https://explorer-studio.genlayer.com/tx/0x9fb08b62e0ed98ce74880a5c22d8fc8adfb6741fa2ae67a0d3543c96b8f534cb) |

---

## Design checks

- Comparative consensus on verdict label only (note non-binding)
- Fail-closed host allowlist; empty fetch must not CONFIRMED
- Challenge = new evidence + consensus (not multi-sig)
- On challenge: only CLEAR lifts halt; INCONCLUSIVE preserves halt
- Owner clear = ops recovery only
- Integrators gate on `is_halted(target_id)` via `view()`
- Anyone may submit evidence; halt only after CONFIRMED consensus