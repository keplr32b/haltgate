# HaltGate — Studionet E2E

| Item | Value |
|------|--------|
| Contract | [`0xD1dC70c83046f99ae2813D311272Cc8DDEa87740`](https://explorer-studio.genlayer.com/address/0xD1dC70c83046f99ae2813D311272Cc8DDEa87740) |
| Deploy | [`0x6c87d3e9f0ae8ea7e3167445e38e78b59d36b1c9acc7f85d1b7b409b0981fb6c`](https://explorer-studio.genlayer.com/tx/0x6c87d3e9f0ae8ea7e3167445e38e78b59d36b1c9acc7f85d1b7b409b0981fb6c) |

## Matrix

| Case | Evidence | Result |
|------|----------|--------|
| vault-1 | https://docs.genlayer.com | **CLEAR** · is_halted false |
| vault-2 | https://example.com | submit **ERROR** host not allowed — [`0x3e419d4e…`](https://explorer-studio.genlayer.com/tx/0x3e419d4eccbccf0d5f32141d69b168b5bd2d7e8336a6986cf42672635b421166) |
| exploit-demo-2 | https://rekt.news/kiichain-rekt | **CONFIRMED** — [`0x2ed2c095…`](https://explorer-studio.genlayer.com/tx/0x2ed2c095d71144f14dcff91b0776148b505683389f7f4e539ec523e3f35b6d88) · is_halted **true** |

## Design checks

- Consensus on closed labels: CONFIRMED \| CLEAR \| INCONCLUSIVE
- Fail-closed: disallowed host reverts; empty fetch does not CONFIRMED
- Integration surface: `is_halted(target_id)` (no claim of forced third-party bytecode stop)
