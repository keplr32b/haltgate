# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
HaltGate — evidence-gated emergency halt flag for GenLayer.
Autonomous Protocols: prove exploit via public URL → consensus → is_halted.
"""

from genlayer import *
import json


try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception


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


class HaltGate(gl.Contract):
    owner: Address
    allowed_hosts: TreeMap[str, bool]
    # per target_id
    registered: TreeMap[str, bool]
    criteria_of: TreeMap[str, str]
    evidence_url_of: TreeMap[str, str]
    has_evidence: TreeMap[str, bool]
    verdict_of: TreeMap[str, str]
    note_of: TreeMap[str, str]
    halted_of: TreeMap[str, bool]
    adjudicated_of: TreeMap[str, bool]

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
    def register_target(self, target_id: str, criteria_text: str) -> None:
        require(gl.message.sender_address == self.owner, "only owner")
        tid = (target_id or "").strip()
        crit = (criteria_text or "").strip()
        require(1 <= len(tid) <= 64, "bad target_id")
        require(len(crit) >= 20, "criteria too short")
        require(self.registered.get(tid, False) is not True, "already registered")
        self.registered[tid] = True
        self.criteria_of[tid] = crit
        self.has_evidence[tid] = False
        self.adjudicated_of[tid] = False
        self.halted_of[tid] = False
        self.verdict_of[tid] = ""
        self.note_of[tid] = ""
        self.evidence_url_of[tid] = ""

    @gl.public.write
    def submit_evidence(self, target_id: str, url: str) -> None:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.halted_of.get(tid, False) is not True, "already halted")
        u = (url or "").strip()
        host = _host_of(u)
        require(self.allowed_hosts.get(host, False) is True, "host not allowed: " + host)
        self.evidence_url_of[tid] = u
        self.has_evidence[tid] = True
        self.adjudicated_of[tid] = False
        self.verdict_of[tid] = ""
        self.note_of[tid] = ""
        self.halted_of[tid] = False

    @gl.public.write
    def adjudicate(self, target_id: str) -> str:
        tid = (target_id or "").strip()
        require(self.registered.get(tid, False) is True, "unknown target")
        require(self.has_evidence.get(tid, False) is True, "no evidence")
        require(self.adjudicated_of.get(tid, False) is not True, "already adjudicated")

        url = self.evidence_url_of.get(tid, "")
        criteria = self.criteria_of.get(tid, "")
        host = _host_of(url)
        require(self.allowed_hosts.get(host, False) is True, "host not allowed: " + host)

        def judge() -> str:
            try:
                content = gl.nondet.web.render(url, mode="text")
                snippet = (content[:3500] if content else "")
            except Exception as e:
                snippet = ("[FETCH FAILED: " + str(e) + "]")[:240]
            empty = len(snippet.strip()) == 0 or snippet.startswith("[FETCH FAILED")
            prompt = (
                "You adjudicate whether PUBLIC EVIDENCE proves an ACTIVE EXPLOIT "
                "for an emergency halt decision.\n\n"
                "CRITERIA (sealed):\n"
                + criteria
                + "\n\nEVIDENCE URL: "
                + url
                + "\n\nEVIDENCE CONTENT:\n---\n"
                + (snippet if not empty else "[EMPTY OR FAILED FETCH]")
                + "\n---\n\n"
                "Return ONLY strict JSON:\n"
                '{ "verdict": "CONFIRMED" or "CLEAR" or "INCONCLUSIVE", '
                '"note": "<short reason>" }\n'
                "Rules:\n"
                "- CONFIRMED only if evidence clearly supports an active exploit/"
                "drain/critical issue per criteria.\n"
                "- CLEAR if evidence is readable but does not prove such an exploit.\n"
                "- INCONCLUSIVE if fetch failed, empty, or unrelated/unusable.\n"
            )
            raw = gl.nondet.exec_prompt(prompt)
            data = parse_json_response(raw)
            verdict = str(data.get("verdict", "")).strip().upper()
            if verdict not in ("CONFIRMED", "CLEAR", "INCONCLUSIVE"):
                verdict = "INCONCLUSIVE"
            if empty and verdict == "CONFIRMED":
                verdict = "INCONCLUSIVE"
            note = str(data.get("note", "")).strip()[:160]
            return canonical({"verdict": verdict, "note": note})

        principle = (
            "EQUIVALENT iff 'verdict' is identical "
            "(CONFIRMED, CLEAR, or INCONCLUSIVE). "
            "note may differ. If verdict differs => NOT equivalent."
        )
        agreed = gl.eq_principle.prompt_comparative(judge, principle)
        parsed = json.loads(agreed)
        verdict = str(parsed["verdict"]).strip().upper()
        note = str(parsed.get("note", "")).strip()[:160]
        require(verdict in ("CONFIRMED", "CLEAR", "INCONCLUSIVE"), "bad verdict")

        halted = verdict == "CONFIRMED"
        self.verdict_of[tid] = verdict
        self.note_of[tid] = note
        self.halted_of[tid] = halted
        self.adjudicated_of[tid] = True
        return verdict

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
                "has_evidence": bool(self.has_evidence.get(tid, False)),
                "evidence_url": self.evidence_url_of.get(tid, ""),
                "adjudicated": bool(self.adjudicated_of.get(tid, False)),
                "verdict": self.verdict_of.get(tid, ""),
                "note": self.note_of.get(tid, ""),
                "halted": bool(self.halted_of.get(tid, False)),
            }
        )

    @gl.public.view
    def is_host_allowed(self, host: str) -> bool:
        h = (host or "").strip().lower()
        return self.allowed_hosts.get(h, False) is True

    @gl.public.view
    def get_owner(self) -> Address:
        return self.owner
