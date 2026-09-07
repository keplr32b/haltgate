# HaltGate - Studionet E2E

## Canonical HaltGate (v2)

| Item | Value |
|------|--------|
| Contract | [`0x67b8AAB3caD42b55eF2Fe7fE72fF33CF8413E27A`](https://explorer-studio.genlayer.com/address/0x67b8AAB3caD42b55eF2Fe7fE72fF33CF8413E27A) |
| Deploy | [`0x2f8496131e3f826c6c197a172fbc6c83f34761bc023c972db8bc1587150d6201`](https://explorer-studio.genlayer.com/tx/0x2f8496131e3f826c6c197a172fbc6c83f34761bc023c972db8bc1587150d6201) |
| Features | Evidence consensus · `is_halted` · `owner_clear_halt` |

## Smoke matrix (v2)

| Step | Result |
|------|--------|
| allow_host docs.genlayer.com + rekt.news | ok |
| vault-1 + https://docs.genlayer.com → adjudicate | **CLEAR** · is_halted false |
| exploit-1 + https://rekt.news/kiichain-rekt → adjudicate | **CONFIRMED** · is_halted true |
| owner_clear_halt(exploit-1) | ok · is_halted **false** |

## Earlier integration demos (v1 HaltGate)

These prove the consumer pattern against a prior HaltGate instance (same API).

| Role | Address |
|------|---------|
| HaltGate v1 | [`0xD1dC70c83046f99ae2813D311272Cc8DDEa87740`](https://explorer-studio.genlayer.com/address/0xD1dC70c83046f99ae2813D311272Cc8DDEa87740) |
| Consumer blocked | [`0x34973C101915525797a3A850F3C36A771b33A2C9`](https://explorer-studio.genlayer.com/address/0x34973C101915525797a3A850F3C36A771b33A2C9) |
| Consumer allowed | [`0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5`](https://explorer-studio.genlayer.com/address/0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5) |

| Case | Tx / outcome |
|------|----------------|
| Host reject example.com | [`0x3e419d4e…`](https://explorer-studio.genlayer.com/tx/0x3e419d4eccbccf0d5f32141d69b168b5bd2d7e8336a6986cf42672635b421166) |
| CONFIRMED kiichain | [`0x2ed2c095…`](https://explorer-studio.genlayer.com/tx/0x2ed2c095d71144f14dcff91b0776148b505683389f7f4e539ec523e3f35b6d88) |
| act() halted | [`0x1923260e…`](https://explorer-studio.genlayer.com/tx/0x1923260ec001d2fd3ab857831453edf652ca4b0e4b943dc448efc74863465d88) ERROR |
| act() clear | [`0xf1eea18f…`](https://explorer-studio.genlayer.com/tx/0xf1eea18f93ee2299ab994e110e205074b546310944712c083be9336e27516c7c) SUCCESS ok |

## Design checks

- Comparative consensus: CONFIRMED \| CLEAR \| INCONCLUSIVE
- Fail-closed host allowlist; empty fetch does not CONFIRMED
- Integrators gate on `is_halted`
- Owner may `owner_clear_halt` after CONFIRMED (ops recovery)
