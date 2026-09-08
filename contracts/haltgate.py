# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
HaltGate — evidence-gated emergency halt for GenLayer (Autonomous Protocols).
Dual-source evidence, challenge window, watch recheck, owner clear (ops).
"""

from genlayer import *
import json
import time


try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception

CHALLENGE_SECS = 300


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise _UserError(msg)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def parse_json_response(text: str) -> dict:
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t[:4].lower() == "json":
            t = t[4:]
        t = t.strip()
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start : end + 1]
    return json.loads(t)


def _now() -> u256:
    return u256(int(time.time()))


def _host_of(url: str) -> str:
    u = (url or "").strip().lower()
    require(u.startswith("https://"), "only https urls allowed")
    rest = u[8:]
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    require(len(host) > 0, "empty host")
    require("@" not in host, "userinfo not allowed")
    require(not host.replace(".", "").isdigit(), "ip literal hosts rejected")
    require("localhost" not in host, "localhost rejected")
    require(not host.endswith(".local"), "local tld rejected")
    return host


def _parse_urls(raw: str) -> list:
    url_list = [u.strip() for u in (raw or "").split(",") if u.strip()]
    require(1 <= len(url_list) <= 2, "need 1 or 2 comma-separated https urls")
    seen = {}
    for u in url_list:
        require(u not in seen, "duplicate url")
        seen[u] = True
        _host_of(u)
    return url_list


class HaltGate(gl.Contract):
    owner: Address
    allowed_hosts: TreeMap[str, bool]

    registered: TreeMap[str, bool]
    criteria_of: TreeMap[str, str]
    watch_url_of: TreeMap[str, str]

    evidence_csv_of: TreeMap[str, str]
    has_evidence: TreeMap[str, bool]

    verdict_of: TreeMap[str, str]
    note_of: TreeMap[str, str]
    halted_of: TreeMap[str, bool]
    adjudicated_of: TreeMap[str, bool]

    challenge_open_of: TreeMap[str, bool]
    challenge_deadline_of: TreeMap[str, u256]
    finalized_of: TreeMap[str, bool]

    def __init__(self):
        self.owner = gl.message.sender_address

    @gl.public.write
    def allow_host(self, host: str) -> None:
        require(gl.message.sender_address == self.owner, "only owner")
        h = (host or "").strip().lower()
        require(len(h) > 0, "empty host")
        require("://" not in h, "pass host only, not url")
        require("@" not in h, "userinfo not allowed")
        require(not h.replace(".", "").isdigit(), "ip literal rejected")
        self.allowed_hosts[h] = True

    @gl.public.write
    def register_target(self, target_id: str, criteria_text: str, watch_url: str) -> None:
        require(gl.message.sender_address == self.owner, "only owner")
        tid = (target_id or "").strip()
        crit = (criteria_text or "").strip()
        require(1 <= len(tid) <= 64, "bad target_id")
        require(len(crit) >= 20, "criteria too short")
        require(self.registered.get(tid, False) is not True, "already registered")
        w = (watch_url or "").strip()
        if len(w) > 0:
            host = _host_of(w)
            require(self.allowed_hosts.get(host, False) is True, "watch host not allowed: " + host)
            self.watch_url_of[tid] = w
        else:
            self.watch_url_of[tid] = ""
        self.registered[tid] = True
        self.criteria_of[tid] = crit
        self.has_evidence[tid] = False
        self.adjudicated_of[tid] = False
        self.halted_of[tid] = False
        self.verdict_of[tid] = ""
        self.note_of[tid] = ""
        self.evidence_csv_of[tid] = ""
        self.challenge_open_of[tid] = False
        self.challenge_deadline_of[tid] = u256(0)
        self.finalized_of[tid] = False

    def _require_hosts_allowed(self, url_list: list) -> None:
        for u in url_list:
            host = _host_of(u)
            require(self.allowed_hosts.get(host, False) is True, "host not allowed: " + host)

    def _run_judgment(self, criteria: str, url_list: list) -> dict:
        urls_csv = ",".join(url_list)
        total = len(url_list)

        def judge() -> str:
            parts = []
            ok = 0
            for i, u in enumerate(url_list):
                try:
                    content = gl.nondet.web.render(u, mode="text")
                    snippet = (content[:3000] if content else "")
                    if snippet.strip():
                        ok += 1
                    else:
                        snippet = "[EMPTY PAGE]"
                except Exception as e:
                    snippet = ("[FETCH FAILED: " + str(e) + "]")[:240]
                parts.append("SOURCE " + str(i + 1) + " (" + u + "):\n---\n" + snippet + "\n---")
            block = "\n\n".join(parts)
            prompt = (
                "You adjudicate whether PUBLIC EVIDENCE proves an ACTIVE EXPLOIT "
                "for an emergency halt decision.\n\n"
                "CRITERIA (sealed):\n"
                + criteria
                + "\n\nEVIDENCE URLS: "
                + urls_csv
                + "\n\nEVIDENCE CONTENT:\n"
                + block
                + "\n\n"
                "Return ONLY strict JSON:\n"
                '{ "verdict": "CONFIRMED" or "CLEAR" or "INCONCLUSIVE", '
                '"note": "<short reason>" }\n'
                "Rules:\n"
                "- CONFIRMED only if evidence clearly supports an active exploit/"
                "drain/critical issue per criteria.\n"
                "- If multiple sources, CONFIRMED only if the set as a whole supports that.\n"
                "- CLEAR if readable but does not prove such an exploit.\n"
                "- INCONCLUSIVE if fetch failed, empty, or unusable.\n"
            )
            raw = gl.nondet.exec_prompt(prompt)
            data = parse_json_response(raw)
            verdict = str(data.get("verdict", "")).strip().upper()
            if verdict not in ("CONFIRMED", "CLEAR", "INCONCLUSIVE"):
                verdict = "INCONCLUSIVE"
            if ok == 0 and verdict == "CONFIRMED":
                verdict = "INCONCLUSIVE"
            note = str(data.get("note", "")).strip()[:160]
            return canonical({"verdict": verdict, "note": note, "sources_count": total})

        principle = (
            "EQUIVALENT iff 'verdict' is identical (CONFIRMED, CLEAR, or INCONCLUSIVE) "
            "and sources_count is identical. note may differ. "
            "If verdict differs => NOT equivalent."
        )
        agreed = gl.eq_principle.prompt_comparative(judge, principle)
        parsed = json.loads(agreed)
        verdict = str(parsed["verdict"]).strip().upper()
        note = str(parsed.get("note", "")).strip()[:160]
        require(verdict in ("CONFIRMED", "CLEAR", "INCONCLUSIVE"), "bad verdict")
        require(int(parsed["sources_count"]) == total, "sources_count mismatch")
        return {"verdict": verdict, "note": note}

    def _apply_verdict(self, tid: str, verdict: str, note: str, open_challenge: bool) -> str:
        self.verdict_of[tid] = verdict
        self.note_of[tid] = note
        self.adjudicated_of[tid] = True
        if verdict == "CONFIRMED":
            self.halted_of[tid] = True
            if open_challenge:
                self.challenge_open_of[tid] = True
                self.challenge_deadline_of[tid] = _now() + u256(CHALLENGE_SECS)
                self.finalized_of[tid] = False
            else:
                self.challenge_open_of[tid] = False
                self.finalized_of[tid] = True
        else:
            self.halted_of[tid] = False
            self.challenge_open_of[tid] = False
            self.finalized_of[tid] = False
        return verdict

    @gl.public.write
    def submit_evidence(self, target_id: str, urls_csv: str) -> None:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.halted_of.get(tid, False) is not True, "already halted")
        url_list = _parse_urls(urls_csv)
        self._require_hosts_allowed(url_list)
        self.evidence_csv_of[tid] = ",".join(url_list)
        self.has_evidence[tid] = True
        self.adjudicated_of[tid] = False
        self.verdict_of[tid] = ""
        self.note_of[tid] = ""
        self.halted_of[tid] = False
        self.challenge_open_of[tid] = False
        self.finalized_of[tid] = False

    @gl.public.write
    def adjudicate(self, target_id: str) -> str:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.has_evidence.get(tid, False) is True, "no evidence")
        require(self.adjudicated_of.get(tid, False) is not True, "already adjudicated")
        url_list = _parse_urls(self.evidence_csv_of.get(tid, ""))
        self._require_hosts_allowed(url_list)
        criteria = self.criteria_of.get(tid, "")
        result = self._run_judgment(criteria, url_list)
        return self._apply_verdict(tid, result["verdict"], result["note"], open_challenge=True)

    @gl.public.write
    def challenge(self, target_id: str, url: str) -> str:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.halted_of.get(tid, False) is True, "not halted")
        require(self.challenge_open_of.get(tid, False) is True, "challenge closed")
        require(self.finalized_of.get(tid, False) is not True, "already finalized")
        require(_now() <= self.challenge_deadline_of.get(tid, u256(0)), "challenge window elapsed")
        u = (url or "").strip()
        host = _host_of(u)
        require(self.allowed_hosts.get(host, False) is True, "host not allowed: " + host)
        criteria = self.criteria_of.get(tid, "")
        result = self._run_judgment(criteria, [u])
        return self._apply_verdict(tid, result["verdict"], result["note"], open_challenge=False)

    @gl.public.write
    def finalize_halt(self, target_id: str) -> None:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.halted_of.get(tid, False) is True, "not halted")
        require(self.challenge_open_of.get(tid, False) is True, "challenge not open")
        require(_now() > self.challenge_deadline_of.get(tid, u256(0)), "window still open")
        self.challenge_open_of[tid] = False
        self.finalized_of[tid] = True

    @gl.public.write
    def recheck(self, target_id: str) -> str:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        w = self.watch_url_of.get(tid, "")
        require(len(w) > 0, "no watch url")
        require(self.halted_of.get(tid, False) is not True, "already halted")
        host = _host_of(w)
        require(self.allowed_hosts.get(host, False) is True, "host not allowed: " + host)
        criteria = self.criteria_of.get(tid, "")
        result = self._run_judgment(criteria, [w])
        return self._apply_verdict(tid, result["verdict"], result["note"], open_challenge=True)

    @gl.public.write
    def owner_clear_halt(self, target_id: str) -> None:
        require(gl.message.sender_address == self.owner, "only owner")
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.halted_of.get(tid, False) is True, "not halted")
        self.halted_of[tid] = False
        self.verdict_of[tid] = "CLEARED_BY_OWNER"
        self.note_of[tid] = "owner cleared halt"
        self.challenge_open_of[tid] = False
        self.finalized_of[tid] = False

    @gl.public.view
    def is_halted(self, target_id: str) -> bool:
        tid = (target_id or "").strip()
        return self.halted_of.get(tid, False) is True

    @gl.public.view
    def read_case(self, target_id: str) -> str:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        return canonical(
            {
                "target_id": tid,
                "registered": True,
                "watch_url": self.watch_url_of.get(tid, ""),
                "has_evidence": bool(self.has_evidence.get(tid, False)),
                "evidence_csv": self.evidence_csv_of.get(tid, ""),
                "adjudicated": bool(self.adjudicated_of.get(tid, False)),
                "verdict": self.verdict_of.get(tid, ""),
                "note": self.note_of.get(tid, ""),
                "halted": bool(self.halted_of.get(tid, False)),
                "challenge_open": bool(self.challenge_open_of.get(tid, False)),
                "challenge_deadline": int(self.challenge_deadline_of.get(tid, u256(0))),
                "finalized": bool(self.finalized_of.get(tid, False)),
            }
        )

    @gl.public.view
    def is_host_allowed(self, host: str) -> bool:
        h = (host or "").strip().lower()
        return self.allowed_hosts.get(h, False) is True

    @gl.public.view
    def get_owner(self) -> Address:
        return self.owner
