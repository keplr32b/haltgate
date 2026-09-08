# HaltGate V3

## Thesis

HaltGate is a GenLayer Intelligent Contract for Autonomous Protocols:

> Emergency halt when anyone **proves** an active exploit with public evidence under validator consensus.

Integrators read `is_halted(target_id)` and freeze privileged actions. HaltGate does not forcibly stop arbitrary bytecode.

## v3 additions

| Feature | Role |
|---------|------|
| Dual-source evidence | Up to 2 HTTPS URLs; CONFIRMED only if consensus supports exploit across sealed set |
| Challenge window | After CONFIRMED, permissionless challenge URL may re-adjudicate before finalization |
| Watch + recheck | Sealed watch URL; permissionless `recheck` re-runs judgment |
| Owner clear | Last-resort ops only — not multi-sig |
| FROZEN consumer | Demo vault blocks act/withdraw while halted |
| Fixtures | Controlled clear/incident pages for reproducible E2E |

## Adversarial stake

| False CONFIRMED | Integrators freeze without real exploit |
| False CLEAR | Exploit continues |
| Challenge grief | Delay finality — mitigated by finalize after window |
| Recheck spam | Same allowlist + criteria; no unilateral halt |

## Lifecycle

```text
REGISTERED
  → submit_evidence (1–2 URLs)
  → adjudicate
       CLEAR / INCONCLUSIVE → not halted
       CONFIRMED → halted + CHALLENGE_OPEN
            → challenge(url) → re-adjudicate
                 CLEAR → halt lifted
                 CONFIRMED → still halted
            → finalize_halt → CHALLENGE_CLOSED (still halted)
  → recheck → may CONFIRMED path if watch evidence supports
  → owner_clear_halt → not halted (ops)
```


| Method | Who |
| :--- | :--- |
| `allow_host` | Owner |
| `register_target(id, criteria, watch_url optional)` | Owner |
| `submit_evidence(id, urls_csv)` | Anyone (1–2 https URLs) |
| `adjudicate(id)` | Anyone |
| `challenge(id, url)` | Anyone while challenge open |
| `finalize_halt(id)` | Anyone after challenge window elapsed |
| `recheck(id)` | Anyone if watch_url set |
| `owner_clear_halt(id)` | Owner |
| `is_halted(id) -> bool` | View |
| `read_case(id) -> str` | View JSON |

## Consensus

Closed labels: CONFIRMED | CLEAR | INCONCLUSIVE
Equivalence on verdict only; note non-binding.
Fail-closed: empty/failed fetch must not CONFIRMED.

## Halt rules

- halted == true only if last binding verdict is CONFIRMED
- Challenge success (CLEAR) clears halt
- finalize_halt closes challenge; does not require multi-sig
- No unilateral halt without consensus

## Non-goals

- Multi-sig pause/unpause councils
- Forced pause of non-integrating contracts
- Universal auto hack detection
- Self-rewriting bytecode
- GEN bond (v3)

## Demo fixtures

- fixtures/clear.html — non-incident status text
- fixtures/incident.html — explicit active exploit / drain narrative
- Host: keplr32b.github.io allowlisted in tests

## Test matrix

- Dual-URL CLEAR (docs / clear fixture)
- Dual-URL or single CONFIRMED (incident fixture)
- Challenge → CLEAR lifts halt
- finalize_halt closes challenge
- recheck on watch path
- host reject
- consumer FROZEN when halted; ok when clear
