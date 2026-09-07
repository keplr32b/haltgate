# HaltGate - Studionet E2E

## Contracts

| Role | Address |
|------|---------|
| HaltGate | [`0xD1dC70c83046f99ae2813D311272Cc8DDEa87740`](https://explorer-studio.genlayer.com/address/0xD1dC70c83046f99ae2813D311272Cc8DDEa87740) |
| GuardedVault (CONFIRMED target) | [`0x34973C101915525797a3A850F3C36A771b33A2C9`](https://explorer-studio.genlayer.com/address/0x34973C101915525797a3A850F3C36A771b33A2C9) |
| GuardedVault (CLEAR target) | [`0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5`](https://explorer-studio.genlayer.com/address/0x0D04c7FFb279340cfa053Debe54e07bEC631bAf5) |

## HaltGate deploy

[`0x6c87d3e9f0ae8ea7e3167445e38e78b59d36b1c9acc7f85d1b7b409b0981fb6c`](https://explorer-studio.genlayer.com/tx/0x6c87d3e9f0ae8ea7e3167445e38e78b59d36b1c9acc7f85d1b7b409b0981fb6c)

## Evidence matrix

| Target | Evidence | Outcome |
|--------|----------|---------|
| vault-1 | https://docs.genlayer.com | **CLEAR** · is_halted false |
| vault-2 | https://example.com | submit **ERROR** host not allowed — [`0x3e419d4e…`](https://explorer-studio.genlayer.com/tx/0x3e419d4eccbccf0d5f32141d69b168b5bd2d7e8336a6986cf42672635b421166) |
| exploit-demo-2 | https://rekt.news/kiichain-rekt | **CONFIRMED** — [`0x2ed2c095…`](https://explorer-studio.genlayer.com/tx/0x2ed2c095d71144f14dcff91b0776148b505683389f7f4e539ec523e3f35b6d88) · is_halted true |

## Consumer matrix

| Vault | Target | act |
|-------|--------|-----|
| 0x34973C… | exploit-demo-2 (halted) | [`0x1923260e…`](https://explorer-studio.genlayer.com/tx/0x1923260ec001d2fd3ab857831453edf652ca4b0e4b943dc448efc74863465d88) **ERROR** `target halted by HaltGate` |
| 0x0D04c7… | vault-1 (clear) | [`0xf1eea18f…`](https://explorer-studio.genlayer.com/tx/0xf1eea18f93ee2299ab994e110e205074b546310944712c083be9336e27516c7c) **SUCCESS** `ok` |

## Checks covered

- Comparative consensus on CONFIRMED \| CLEAR \| INCONCLUSIVE
- Fail-closed host allowlist
- Empty/failed fetch does not CONFIRMED
- Integrators gate on `is_halted` (demo consumers)
