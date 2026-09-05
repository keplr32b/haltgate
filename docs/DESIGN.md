# HaltGate - Design

## Thesis

HaltGate is a reusable GenLayer Intelligent Contract for the Autonomous Protocols track:

> Emergency halt: mark a target halted when anyone **proves** an active exploit with public evidence under multi-validator consensus.

Other contracts and agents read `is_halted(target_id)` and refuse to act. HaltGate does not forcibly stop arbitrary bytecode; it provides a consensus-backed halt flag as an integration surface.

## Track fit

- Official idea: *Pauses a target contract when anyone proves an active exploit*
- Autonomous Protocols listed no live reference project at hackathon open
- GenLayer-native work: live HTTPS fetch + comparative consensus on a closed verdict label

## Adversarial stake

| False outcome | Who is hurt |
|---------------|-------------|
| False CONFIRMED | Target/integrators freeze without real exploit |
| False CLEAR | Exploit continues while flag stays open |
| Forced INCONCLUSIVE | Delay without unjustified halt |

## Lifecycle

text
NONE → REGISTERED → EVIDENCE → ADJUDICATED
                      (CONFIRMED → halted)
                      (CLEAR / INCONCLUSIVE → not halted)

## Core API

| Method | Role |
|--------|------|
| `register_target(target_id, criteria_text)` | Owner registers target + sealed criteria |
| `allow_host(host)` | Owner allowlists evidence hosts |
| `submit_evidence(target_id, url)` | Permissionless public HTTPS URL |
| `adjudicate(target_id)` | Consensus → CONFIRMED \| CLEAR \| INCONCLUSIVE |
| `is_halted(target_id) -> bool` | Integration surface |
| `read_case(target_id) -> str` | JSON status for UI / indexers |

## Criteria

- Natural language, sealed at register
- Example: "Confirm CONFIRMED only if the evidence describes an active exploit, drain, or critical vulnerability affecting this target; otherwise CLEAR; if evidence cannot be fetched or is unrelated, INCONCLUSIVE"

## Consensus

Non-deterministic block returns JSON:

```json
{
  "verdict": "CONFIRMED",
  "note": "short phrase"
}
```

Equivalence (comparative):
- verdict exact match among CONFIRMED | CLEAR | INCONCLUSIVE
- note ignored for equivalence

Deterministic map:
Verdict      |  Halted
CONFIRMED    |  true
CLEAR        |  false
INCONCLUSIVE | false (fail-closed: do not halt)

## Safety

- HTTPS only; reject IP literals, localhost, userinfo
- Owner-managed host allowlist
- No fund custody in v1 (verdict / flag only)
- Fail-closed on host errors and empty fetches → INCONCLUSIVE, not CONFIRMED
- Schema-safe views: bool, str, u256 only (no dict / list returns)

## Explicit non-goals (v1)

- Forcing pause inside third-party contracts without integration
- Multi-sig recovery theater as the main product
- Internal ERC-20 vault / reputation scores as core logic
- Self-rewriting lifeform behavior

## Demo evidence (real HTTPS only)

- Allowlist real hosts (e.g. docs.genlayer.com, public status/security pages)
- Never use example.com for success paths

## Test matrix (target)

- Register + allow_host
- Submit evidence + adjudicate → CLEAR or CONFIRMED (fixture-dependent)
- is_halted matches verdict
- Disallowed host reverts
- Non-HTTPS reverts
- Unknown target reverts
- read_case returns stable JSON string
